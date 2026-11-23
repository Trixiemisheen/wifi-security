"""WiFi scanning and analysis logic (refactored from wifisec.py). No GUI, no input()."""
import csv
import json
import os
import re
import subprocess
from datetime import datetime

from wifisec.core.config import DATA_DIR, REPORTS_DIR, SCAN_TIMEOUT, TOOL_NAME
from wifisec.core.logging_utils import log_event

IS_WINDOWS = (os.name == "nt")


class Color:
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    MAGENTA = "\033[95m"
    BOLD = "\033[1m"
    END = "\033[0m"


def c(text, *styles):
    return f"{''.join(styles)}{text}{Color.END}"


# --------- interface detection ---------
def get_wifi_interfaces():
    if IS_WINDOWS:
        return _get_wifi_interfaces_windows()
    return _get_wifi_interfaces_linux()


def _get_wifi_interfaces_windows():
    interfaces = []
    try:
        output = subprocess.check_output(
            ["netsh", "wlan", "show", "interfaces"],
            stderr=subprocess.STDOUT, text=True, errors="ignore")
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        log_event(f"Failed to list Wi-Fi interfaces: {e}")
        return []
    for line in output.splitlines():
        m = re.match(r"Name\s*:\s*(.+)", line.strip())
        if m:
            interfaces.append(m.group(1).strip())
    return interfaces


def _get_wifi_interfaces_linux():
    interfaces = []
    if not os.path.isdir("/sys/class/net"):
        return interfaces
    for iface in os.listdir("/sys/class/net"):
        if iface == "lo":
            continue
        try:
            out = subprocess.check_output(
                ["iwconfig", iface], stderr=subprocess.STDOUT, text=True)
            if "no wireless extensions" not in out.lower():
                interfaces.append(iface)
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
    return interfaces


# --------- scanning ---------
def scan_wifi(interface=None, timeout=SCAN_TIMEOUT):
    log_event(f"Scan started on interface: {interface}")
    if IS_WINDOWS:
        networks = _scan_windows(timeout)
    else:
        if not interface:
            networks = []
        else:
            networks = _scan_linux(interface, timeout)
    log_event(f"Scan finished: {len(networks)} AP(s) found")
    return networks


def _scan_windows(timeout):
    try:
        output = subprocess.check_output(
            ["netsh", "wlan", "show", "networks", "mode=bssid"],
            stderr=subprocess.STDOUT, text=True, errors="ignore",
            timeout=timeout + 5)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    networks = _parse_netsh_output(output)
    for net in networks:
        raw = str(net.get("Signal", "0")).strip()
        try:
            val = int(raw.rstrip("%"))
        except (ValueError, TypeError):
            val = 0
        net["Quality(%)"] = max(0, min(100, val))
        net["Signal"] = f"{val}%"
    return networks


def _parse_netsh_output(output):
    networks = []
    ssid = auth = enc = None
    for raw in output.splitlines():
        line = raw.strip()
        m = re.match(r"^SSID \d+\s*:\s*(.*)$", line)
        if m:
            ssid = m.group(1).strip() or "<HIDDEN>"
            auth = enc = None
            continue
        m = re.match(r"Authentication\s*:\s*(.*)$", line)
        if m:
            auth = m.group(1).strip()
            continue
        m = re.match(r"Encryption\s*:\s*(.*)$", line)
        if m:
            enc = m.group(1).strip()
            continue
        m = re.match(r"BSSID \d+\s*:\s*([0-9A-Fa-f:]{17})", line)
        if m:
            networks.append({
                "ESSID": ssid or "<UNKNOWN>",
                "BSSID": m.group(1),
                "Channel": "N/A",
                "Authentication": auth or "Open",
                "Encryption": _detect_encryption(f"{auth or ''} {enc or ''}"),
                "Signal": "0",
                "Quality(%)": 0,
            })
            continue
        m = re.match(r"Signal\s*:\s*(\d+)%", line)
        if m and networks:
            networks[-1]["Signal"] = f"{m.group(1)}%"
            networks[-1]["Quality(%)"] = int(m.group(1))
            continue
        m = re.match(r"Channel\s*:\s*(\d+)", line)
        if m and networks:
            networks[-1]["Channel"] = m.group(1)
    return networks


def _scan_linux(interface, timeout):
    try:
        output = subprocess.check_output(
            ["iwlist", interface, "scan"],
            stderr=subprocess.STDOUT, text=True, errors="ignore",
            timeout=timeout + 10)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    networks = []
    for cell in output.split("Cell "):
        if "ESSID:" in cell:
            net = _parse_iwlist_cell(cell)
            if net:
                networks.append(net)
    return networks


def _parse_iwlist_cell(cell):
    net = {}
    m = re.search(r"Address:\s*([0-9A-Fa-f:]{17})", cell)
    net["BSSID"] = m.group(1) if m else ""
    m = re.search(r'ESSID:"(.*)"', cell)
    net["ESSID"] = m.group(1) if m else "<HIDDEN>"
    m = re.search(r"Channel:(\d+)", cell)
    net["Channel"] = m.group(1) if m else "N/A"
    m = re.search(r"Frequency:([\d.]+)\s*GHz", cell)
    net["Frequency"] = m.group(1) if m else ""
    m_q = re.search(r"Quality=(\d+)/(\d+)", cell)
    if m_q:
        try:
            q, max_q = int(m_q.group(1)), int(m_q.group(2))
            pct = int((q / max_q) * 100) if max_q else 0
        except (ValueError, ZeroDivisionError):
            pct = 0
    else:
        pct = 0
    net["Quality(%)"] = max(0, min(100, pct))
    net["Signal"] = f"{pct}%"
    net["Encryption"] = _detect_encryption(cell)
    return net


def _detect_encryption(text):
    t = (text or "").upper()
    if "WPA3" in t:
        return "WPA3"
    if "WPA2" in t:
        return "WPA2"
    if "WPA" in t:
        return "WPA"
    if "WEP" in t or "PRIVACY" in t:
        return "WEP"
    if "ENCRYPTION KEY:ON" in t:
        return "WEP"
    return "OPEN"


# --------- analysis ---------
def analyze_signal(networks):
    for net in networks:
        raw = str(net.get("Signal", "")).strip()
        try:
            if raw.lower().endswith("dbm"):
                dbm = int(re.sub(r"[^\-\d]", "", raw))
                quality = (dbm + 100) * 2
            elif raw.endswith("%"):
                quality = int(raw.rstrip("%"))
            else:
                quality = int(raw) if raw else 0
        except (ValueError, TypeError):
            quality = 0
        net["Quality(%)"] = max(0, min(100, quality))
        net["Signal"] = raw
    return networks


def analyze_channels(networks):
    cnt = {}
    for net in networks:
        ch = net.get("Channel", "N/A")
        cnt[ch] = cnt.get(ch, 0) + 1
    return cnt


def filter_networks(networks, security=None, ssid=None, min_quality=0):
    filtered = []
    for net in networks:
        if security and net.get("Encryption", "") != security:
            continue
        if ssid and ssid.lower() not in net.get("ESSID", "").lower():
            continue
        try:
            q = int(net.get("Quality(%)", 0) or 0)
        except (ValueError, TypeError):
            q = 0
        if q < min_quality:
            continue
        filtered.append(net)
    return filtered


# --------- security assessment ---------
def _assess_security(net):
    enc = str(net.get("Encryption", "")).upper()
    if "WPA3" in enc:
        return "SECURE (WPA3)"
    if "WPA2" in enc:
        return "MODERATE (WPA2)"
    if "WPA" in enc:
        return "WEAK (WPA)"
    if "WEP" in enc:
        return "WEAK (WEP)"
    if enc in ("", "OPEN", "NONE"):
        return "UNSECURED (OPEN)"
    return "UNKNOWN"


def security_assessment(networks):
    for net in networks:
        net["Security Level"] = _assess_security(net)
    return networks


def generate_report(networks):
    report = []
    for i, net in enumerate(networks, 1):
        report.append([
            i,
            net.get("ESSID", ""),
            net.get("BSSID", ""),
            net.get("Channel", ""),
            net.get("Quality(%)", ""),
            net.get("Encryption", ""),
            _assess_security(net),
        ])
    return report


# --------- export ---------
def save_results_csv(networks, filename="wifi_results.csv"):
    if not networks:
        return None
    path = os.path.join(DATA_DIR, filename)
    fields = ["ESSID", "BSSID", "Channel", "Encryption",
              "Signal", "Quality(%)", "Security Level"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(networks)
    return path


def save_results_json(networks, filename="wifi_results.json"):
    if not networks:
        return None
    path = os.path.join(DATA_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(networks, f, indent=4)
    return path


def save_report_csv(report, filename="wifi_report.csv"):
    path = os.path.join(REPORTS_DIR, filename)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["#", "ESSID", "BSSID", "Channel", "Quality(%)",
                    "Encryption", "Security Level"])
        w.writerows(report)
    return path


def export_report_txt(report, filename=None):
    if not filename:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"wifi_report_{ts}.txt"
    path = os.path.join(REPORTS_DIR, filename)
    try:
        from tabulate import tabulate
    except ImportError:
        return None
    headers = ["#", "ESSID", "BSSID", "Ch", "Q(%)", "Encryption", "Security Level"]
    body = tabulate(report, headers=headers, tablefmt="grid")
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"{TOOL_NAME} - Security Report\n")
        f.write(f"Generated: {datetime.now()}\n")
        f.write(f"Total networks: {len(report)}\n\n")
        f.write(body)
        f.write("\n\n--- End of Report ---\n")
    return path