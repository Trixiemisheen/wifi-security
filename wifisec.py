# -------- DISCLAIMER ──────────────────────────────────────────
#  This tool is for educational purposes only.
#  Do not use it for illegal activities. The author is not
#  responsible for any misuse of this tool.
#
#  Contact: hello@trixiemisheen.site
#           WhatsApp: +254791915925
#           Instagram: @trixiemisheen
# ─────────────────────────────────────────────────────────────
# ── PROJECT STRUCTURE ────────────────────────────────────────
# The required libraries are: os, re, csv, json, subprocess, datetime, tabulate
# use pip install tabulate csv json

import hashlib, sys
MASTER_CREDIT = "WiFi Security Suite v4.0 | Created by Trixie Misheen™"


# 1. Hardcode the expected SHA-256 hash of your original credit line
EXPECTED_CREDIT_HASH = "3ad322d17b7982234fd383fe0e9d0e35c0fd6cae5406b1ef2e53cefbbe9fffbe"

# 2. Your actual visible banner string
BANNER_CREDIT = "WiFi Security v4.0 | Created by Trixie Misheen"

def verify_brand_integrity():
    """Verifies that the core authorship banner has not been altered."""
    current_hash = hashlib.sha256(BANNER_CREDIT.encode('utf-8')).hexdigest()
    
    if current_hash != EXPECTED_CREDIT_HASH:
        print("\n [!] INTEGRITY ERROR: Code modification detected.")
        print("     Unauthorized removal or edit of original creator credits.")
        print("     Official Repository: https://github.com/Trixiemisheen/Nae-nae/wifi-security\n")
        sys.exit(1)

def main():
    # Enforce integrity check before loading the menu
    verify_brand_integrity()
    
    print(f"=== {BANNER_CREDIT} ===\n")


# --------- 1. IMPORT LIBRARIES & PROJECT SETUP ---------
import os
import re
import csv
import json
import subprocess
from datetime import datetime

# ── ANSI color codes ──
class Color:
    CYAN    = '\033[96m'
    GREEN   = '\033[92m'
    YELLOW  = '\033[93m'
    RED     = '\033[91m'
    MAGENTA = '\033[95m'
    BOLD    = '\033[1m'
    END     = '\033[0m'

def c(text, *styles):
    """Return text wrapped with ANSI color codes."""
    prefix = ''.join(styles)
    return f"{prefix}{text}{Color.END}"

# ── Project folders ──
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR    = os.path.join(BASE_DIR, 'data')
LOGS_DIR    = os.path.join(BASE_DIR, 'logs')
REPORTS_DIR = os.path.join(BASE_DIR, 'reports')

os.makedirs(DATA_DIR,    exist_ok=True)
os.makedirs(LOGS_DIR,    exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

# ── Configuration ──
SCAN_TIMEOUT  = 10
LOG_FILE      = os.path.join(LOGS_DIR, 'wifi_security_tool.log')
RESULTS_FILE  = os.path.join(DATA_DIR, 'network.csv')

# ── Tool Meta ──
TOOL_NAME    = "WiFi Security Tool"
TOOL_VERSION = "4.0"
AUTHOR       = "TRIXIE MISHEEN™"
DESCRIPTION  = "Scan and analyze WiFi networks for security vulnerabilities"
DISCLAIMER   = ("This tool is for educational purposes only. "
                "Do not misuse it. The author is not responsible "
                "for any illegal activities conducted using this tool.")

IS_WINDOWS = (os.name == 'nt')


def log_event(message):
    """Write a timestamped event to the log file."""
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.now().isoformat()}] {message}\n")
    except OSError:
        pass


def print_header(title=None):
    """Print a styled application header."""
    width = 68
    print(f"\n{c('=' * width, Color.CYAN, Color.BOLD)}")
    print(c(f"  {TOOL_NAME}  v{TOOL_VERSION}", Color.CYAN, Color.BOLD))
    print(c(f"  {AUTHOR}", Color.MAGENTA))
    print(c(f"  {DISCLAIMER}", Color.YELLOW))
    if title:
        print(c('-' * width, Color.CYAN))
        print(c(f"  >> {title}", Color.CYAN, Color.BOLD))
    print(c('=' * width, Color.CYAN, Color.BOLD))


def show_main_menu():
    os.system('cls' if IS_WINDOWS else 'clear')
    print_header("MAIN MENU")
    items = [
        ("1",  "📡  List Wireless Interfaces"),
        ("2",  "🔎  Scan for WiFi Networks"),
        ("3",  "🔐  Analyze Network Security"),
        ("4",  "📄  Generate Report"),
        ("5",  "📂  View Saved Results"),
        ("6",  "🚪  Exit"),
    ]
    for key, label in items:
        print(f"  {c(key, Color.GREEN, Color.BOLD)}. {label}")
    print(c("─" * 68, Color.CYAN))


# --------- 2. WI-FI INTERFACE DETECTION ---------
def get_wifi_interfaces():
    """List all wireless interfaces."""
    if IS_WINDOWS:
        return _get_wifi_interfaces_windows()
    return _get_wifi_interfaces_linux()


def _get_wifi_interfaces_windows():
    interfaces = []
    try:
        output = subprocess.check_output(
            ['netsh', 'wlan', 'show', 'interfaces'],
            stderr=subprocess.STDOUT, text=True, errors='ignore')
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
    if not os.path.isdir('/sys/class/net'):
        return interfaces
    for iface in os.listdir('/sys/class/net'):
        if iface == 'lo':
            continue
        try:
            out = subprocess.check_output(
                ['iwconfig', iface], stderr=subprocess.STDOUT, text=True)
            if 'no wireless extensions' not in out.lower():
                interfaces.append(iface)
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
    return interfaces


# --------- 3. WiFi SCANNING ---------
def scan_wifi(interface=None, timeout=SCAN_TIMEOUT):
    """Scan for WiFi networks. Returns a list of network dicts."""
    print(c(f"\n  [*] Scanning on '{interface}' (timeout {timeout}s) ...",
            Color.YELLOW))
    log_event(f"Scan started on interface: {interface}")

    if IS_WINDOWS:
        return _scan_windows(timeout)

    if not interface:
        print(c("  [!] No interface specified for scan.", Color.RED))
        return []
    return _scan_linux(interface, timeout)


def _scan_windows(timeout):
    try:
        output = subprocess.check_output(
            ['netsh', 'wlan', 'show', 'networks', 'mode=bssid'],
            stderr=subprocess.STDOUT, text=True, errors='ignore',
            timeout=timeout + 5)
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(c(f"  [!] Scan failed: {e}", Color.RED))
        print(c("  [!] Run as Administrator if WLAN AutoConfig is not running.",
                Color.YELLOW))
        return []

    networks = _parse_netsh_output(output)
    # Normalise signal for netsh results
    for net in networks:
        raw = str(net.get("Signal", "0")).strip()
        try:
            val = int(raw.rstrip('%'))
        except (ValueError, TypeError):
            val = 0
        net["Quality(%)"] = max(0, min(100, val))
        net["Signal"]     = f"{val}%"

    print(c(f"  [+] Found {len(networks)} access point(s)", Color.GREEN, Color.BOLD))
    log_event(f"Scan finished: {len(networks)} AP(s) found")
    return networks


def _parse_netsh_output(output):
    """Parse 'netsh wlan show networks mode=bssid' output."""
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
                "ESSID":         ssid or "<UNKNOWN>",
                "BSSID":         m.group(1),
                "Channel":       "N/A",
                "Authentication": auth or "Open",
                "Encryption":    _detect_encryption(f"{auth or ''} {enc or ''}"),
                "Signal":        "0",
                "Quality(%)":    0,
            })
            continue

        m = re.match(r"Signal\s*:\s*(\d+)%", line)
        if m and networks:
            networks[-1]["Signal"]     = f"{m.group(1)}%"
            networks[-1]["Quality(%)"] = int(m.group(1))
            continue

        m = re.match(r"Channel\s*:\s*(\d+)", line)
        if m and networks:
            networks[-1]["Channel"] = m.group(1)

    return networks


def _scan_linux(interface, timeout):
    try:
        output = subprocess.check_output(
            ['iwlist', interface, 'scan'],
            stderr=subprocess.STDOUT, text=True, errors='ignore',
            timeout=timeout + 10)
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(c(f"  [!] iwlist scan failed: {e}", Color.RED))
        print(c("  [!] Try: sudo iwconfig <iface> mode managed && sudo iwlist scan",
                Color.YELLOW))
        return []

    networks = []
    for cell in output.split("Cell "):
        if "ESSID:" in cell:
            net = _parse_iwlist_cell(cell)
            if net:
                networks.append(net)

    print(c(f"  [+] Found {len(networks)} access point(s)", Color.GREEN, Color.BOLD))
    log_event(f"Scan finished: {len(networks)} AP(s) found")
    return networks


def _parse_iwlist_cell(cell):
    """Parse a single 'iwlist scan' cell into a network dict."""
    net = {}

    m = re.search(r"Address:\s*([0-9A-Fa-f:]{17})", cell)
    net["BSSID"] = m.group(1) if m else ""

    m = re.search(r'ESSID:"(.*)"', cell)
    net["ESSID"] = m.group(1) if m else "<HIDDEN>"

    m = re.search(r"Channel:(\d+)", cell)
    net["Channel"] = m.group(1) if m else "N/A"

    m = re.search(r"Frequency:([\d.]+)\s*GHz", cell)
    net["Frequency"] = m.group(1) if m else ""

    # Parse quality as integer percentage
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
    net["Signal"]     = f"{pct}%"

    # Encryption detection
    net["Encryption"] = _detect_encryption(cell)

    return net


def _detect_encryption(text):
    """Detect encryption type from raw text (netsh auth line or iwlist cell)."""
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


# --------- 4. RESULTS DISPLAY & FILTERING ---------
def display_results(networks, title=None):
    """Show networks in a formatted tabulate table."""
    if not networks:
        print(c("  [!] No networks to display.", Color.YELLOW))
        return

    try:
        from tabulate import tabulate
    except ImportError:
        _display_results_fallback(networks)
        return

    if title:
        print(c(f"\n  ── {title} ──", Color.CYAN, Color.BOLD))

    table = []
    for net in networks:
        table.append([
            net.get("ESSID", ""),
            net.get("BSSID", ""),
            net.get("Channel", ""),
            net.get("Encryption", ""),
            net.get("Signal", ""),
            net.get("Quality(%)", ""),
            _assess_security(net),
        ])

    headers = ["ESSID", "BSSID", "Ch", "Encryption", "Signal", "Q(%)", "Security"]
    print(tabulate(table, headers=headers, tablefmt="grid"))
    print(c(f"  Total: {len(networks)} network(s)\n", Color.GREEN))


def _display_results_fallback(networks):
    """Fallback plain-text table when tabulate is not installed."""
    print(c("  [!] Install 'tabulate' for prettier tables: pip install tabulate",
            Color.YELLOW))
    headers = ["#", "ESSID", "BSSID", "Ch", "Encryption", "Signal", "Q(%)"]
    print('-' * 100)
    print(f"{'#':<3} {'ESSID':<22} {'BSSID':<18} {'Ch':<4} "
          f"{'Encryption':<12} {'Signal':<8} {'Q(%)':<5}")
    print('-' * 100)
    for i, net in enumerate(networks, 1):
        row = [net.get("ESSID","")[:22], net.get("BSSID","")[:18],
               net.get("Channel",""), net.get("Encryption",""),
               net.get("Signal",""), net.get("Quality(%)","")]
        print(f"{i:<3} {row[0]:<22} {row[1]:<18} {row[2]:<4} "
              f"{row[3]:<12} {row[4]:<8} {row[5]:<5}")

def analyze_signal(networks):
    """Normalize signal into Quality(%) 0-100.

    Handles both netsh percentages ('81%') and iwlist dBm ('-40 dBm').
    """
    for net in networks:
        raw = str(net.get("Signal", "")).strip()
        try:
            if raw.lower().endswith("dbm"):
                dbm = int(re.sub(r"[^\-\d]", "", raw))
                quality = (dbm + 100) * 2          # -100..0 dBm -> 0..100
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
    """Count networks per channel, return dict."""
    cnt = {}
    for net in networks:
        ch = net.get("Channel", "N/A")
        cnt[ch] = cnt.get(ch, 0) + 1
    return cnt


def filter_networks(networks, security=None, ssid=None, min_quality=0):
    """Filter by encryption type, SSID substring, or minimum quality."""
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


# --------- 5. SECURITY ASSESSMENT ---------
def _assess_security(net):
    """Return a human-readable security level string."""
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
    """Attach a Security Level key to every network entry."""
    for net in networks:
        net["Security Level"] = _assess_security(net)
    return networks


def generate_report(networks):
    """Build a report table (list of lists) ready for tabulate or CSV."""
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


def print_report(report):
    """Display the security report using tabulate."""
    try:
        from tabulate import tabulate
    except ImportError:
        print(c("[!] Install tabulate: pip install tabulate", Color.YELLOW))
        return
    print(c("\n  ── WIFI SECURITY ASSESSMENT REPORT ──", Color.CYAN, Color.BOLD))
    headers = ["#", "ESSID", "BSSID", "Ch", "Q(%)", "Encryption", "Security Level"]
    print(tabulate(report, headers=headers, tablefmt="grid"))
    print()


# --------- 6. EXPORT & SAVE ---------
def save_results_csv(networks, filename="wifi_results.csv"):
    """Save scanned networks to CSV."""
    if not networks:
        print(c("  [!] No data to save.", Color.YELLOW))
        return
    path = os.path.join(DATA_DIR, filename)
    fields = ["ESSID", "BSSID", "Channel", "Encryption",
              "Signal", "Quality(%)", "Security Level"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        w.writeheader()
        w.writerows(networks)
    print(c(f"  [+] Saved to {path}", Color.GREEN, Color.BOLD))


def save_results_json(networks, filename="wifi_results.json"):
    if not networks:
        print(c("  [!] No data to save.", Color.YELLOW))
        return
    path = os.path.join(DATA_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(networks, f, indent=4)
    print(c(f"  [+] Saved to {path}", Color.GREEN, Color.BOLD))


def save_report_csv(report, filename="wifi_report.csv"):
    """Save report table to CSV."""
    path = os.path.join(REPORTS_DIR, filename)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["#", "ESSID", "BSSID", "Channel", "Quality(%)",
                     "Encryption", "Security Level"])
        w.writerows(report)
    print(c(f"  [+] Report saved to {path}", Color.GREEN, Color.BOLD))


def export_report_txt(report, filename=None):
    """Export report as a nicely formatted TXT file."""
    if not filename:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"wifi_report_{ts}.txt"
    path = os.path.join(REPORTS_DIR, filename)
    try:
        from tabulate import tabulate
    except ImportError:
        print(c("  [!] Install tabulate for TXT export.", Color.YELLOW))
        return
    headers = ["#", "ESSID", "BSSID", "Ch", "Q(%)", "Encryption", "Security Level"]
    body = tabulate(report, headers=headers, tablefmt="grid")
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"{TOOL_NAME} - Security Report\n")
        f.write(f"Generated: {datetime.now()}\n")
        f.write(f"Total networks: {len(report)}\n\n")
        f.write(body)
        f.write("\n\n--- End of Report ---\n")
    print(c(f"  [+] Report saved to {path}", Color.GREEN, Color.BOLD))


def export_prompt(networks):
    """Interactive export prompt after scan."""
    print(c("\n  ── Export Results ──", Color.CYAN, Color.BOLD))
    print("  1. Export as CSV")
    print("  2. Export as JSON")
    print("  3. Export report as TXT")
    print("  4. Skip\n")
    choice = input("  Select [1-4]: ").strip()

    if choice == '1':
        name = input("  Filename (default: wifi_results.csv): ").strip()
        save_results_csv(networks, name or "wifi_results.csv")
    elif choice == '2':
        name = input("  Filename (default: wifi_results.json): ").strip()
        save_results_json(networks, name or "wifi_results.json")
    elif choice == '3':
        report = generate_report(networks)
        export_report_txt(report)
    else:
        print(c("  － Export skipped.", Color.YELLOW))


# --------- 7. VIEW SAVED RESULTS ---------
def view_saved_results():
    """List saved data files and optionally display one."""
    files = [f for f in os.listdir(DATA_DIR)
             if f.endswith(('.csv', '.json'))]
    if not files:
        print(c(f"  [!] No saved results found in {DATA_DIR}.", Color.YELLOW))
        return

    print(c(f"\n  ── Saved Files ──", Color.CYAN, Color.BOLD))
    for i, fname in enumerate(files, 1):
        size = os.path.getsize(os.path.join(DATA_DIR, fname))
        print(f"  {c(i, Color.GREEN)}. {fname}  ({size} bytes)")

    sel = input(c("\n  Enter number to view (or Enter to skip): ", Color.YELLOW)).strip()
    if not sel.isdigit():
        return
    idx = int(sel) - 1
    if idx < 0 or idx >= len(files):
        return

    path = os.path.join(DATA_DIR, files[idx])
    print(c(f"\n  ── Contents of {files[idx]} ──", Color.CYAN, Color.BOLD))
    try:
        if path.endswith('.json'):
            with open(path, encoding='utf-8') as f:
                print(json.dumps(json.load(f), indent=2))
        else:
            with open(path, encoding='utf-8') as f:
                print(f.read())
    except Exception as e:
        print(c(f"  [!] Error reading file: {e}", Color.RED))


# --------- 8. SECURITY ANALYSIS SUB-MENU ---------
def analysis_menu(networks):
    """Sub-menu for security analysis and channel view."""
    if not networks:
        print(c("  [!] No scan data. Run option 2 first.", Color.YELLOW))
        input(c("  Press Enter to continue...", Color.YELLOW))
        return

    while True:
        os.system('cls' if IS_WINDOWS else 'clear')
        print_header("SECURITY ANALYSIS")

        results = security_assessment(networks)
        display_results(results, title="All Networks — Security Assessment")

        # Channel usage
        ch_counts = analyze_channels(results)
        print(c("  ── Channel Usage ──", Color.MAGENTA, Color.BOLD))
        if ch_counts:
            max_ch = max(ch_counts.values()) if ch_counts else 1
            bar_w = 25
            for ch, cnt in sorted(ch_counts.items(), key=lambda x: x[1], reverse=True):
                bar = '█' * int((cnt / max_ch) * bar_w)
                print(f"  Ch {ch:>4} |{c(bar, Color.CYAN)} {cnt}")
        else:
            print("  (no channel data)")

        print(c("\n  Options:", Color.YELLOW))
        print("  1. Filter by minimum quality")
        print("  2. Filter by encryption type")
        print("  3. Back to main menu\n")

        choice = input("  Select [1-3]: ").strip()

        if choice == '1':
            q = input("  Minimum quality (0-100, Enter=skip): ").strip()
            if q.isdigit():
                filtered = filter_networks(results, min_quality=int(q))
                display_results(filtered, title=f"Networks ≥ {q}% quality")
                input(c("  Press Enter to continue...", Color.YELLOW))

        elif choice == '2':
            print(c("  Encryption types:", Color.CYAN))
            enc_types = sorted(set(n.get("Encryption", "UNKNOWN") for n in results))
            for i, e in enumerate(enc_types, 1):
                print(f"    {c(i, Color.GREEN)}. {e}")
            sel = input("  Select number: ").strip()
            if sel.isdigit() and 1 <= int(sel) <= len(enc_types):
                enc = enc_types[int(sel) - 1]
                filtered = filter_networks(results, security=enc)
                display_results(filtered, title=f"Networks — {enc}")
                input(c("  Press Enter to continue...", Color.YELLOW))

        elif choice == '3':
            break
        else:
            print(c("  ✘ Invalid option.", Color.RED))
            input(c("  Press Enter to continue...", Color.YELLOW))


# --------- 9. REPORT MENU ---------
def report_menu(networks):
    """Sub-menu for report generation and export."""
    if not networks:
        print(c("  [!] No scan data. Run option 2 first.", Color.YELLOW))
        input(c("  Press Enter to continue...", Color.YELLOW))
        return

    while True:
        os.system('cls' if IS_WINDOWS else 'clear')
        print_header("GENERATE REPORT")

        report = generate_report(networks)
        print_report(report)

        print("  1. Save report as CSV")
        print("  2. Save report as TXT (formatted)")
        print("  3. Back to main menu\n")

        choice = input("  Select [1-3]: ").strip()

        if choice == '1':
            name = input("  Filename (default: wifi_report.csv): ").strip()
            save_report_csv(report, name or "wifi_report.csv")
            input(c("  Press Enter to continue...", Color.YELLOW))

        elif choice == '2':
            name = input("  Filename (default: auto-named): ").strip()
            export_report_txt(report, name or None)
            input(c("  Press Enter to continue...", Color.YELLOW))

        elif choice == '3':
            break
        else:
            print(c("  ✘ Invalid option.", Color.RED))
            input(c("  Press Enter to continue...", Color.YELLOW))


# --------- 10. MAIN PROGRAM LOOP ---------
def main():
    interfaces = get_wifi_interfaces()
    if not interfaces:
        print(c("\n  [-] No Wi-Fi interface found.", Color.RED, Color.BOLD))
        if IS_WINDOWS:
            print(c("      Make sure Wi-Fi is enabled and 'WLAN AutoConfig' "
                    "service is running.", Color.YELLOW))
        else:
            print(c("      Enable your wireless adapter and check iwconfig.",
                    Color.YELLOW))
        input(c("  Press Enter to exit...", Color.YELLOW))
        return

    networks = []          # holds the last scan results
    active_iface = interfaces[0]   # default interface

    while True:
        show_main_menu()
        choice = input(f"\n  Select [1-6]: ").strip()

        if choice == '1':
            print(c("\n  ── Wireless Interfaces ──", Color.CYAN, Color.BOLD))
            for i, iface in enumerate(interfaces, 1):
                marker = c("← ACTIVE", Color.GREEN) if iface == active_iface else ""
                print(f"  {c(i, Color.GREEN)}. {iface}  {marker}")
            sel = input(c("\n  Select interface to use (Enter to keep current): ",
                         Color.YELLOW)).strip()
            if sel.isdigit() and 1 <= int(sel) <= len(interfaces):
                active_iface = interfaces[int(sel) - 1]
                print(c(f"  [+] Active interface set to: {active_iface}",
                        Color.GREEN, Color.BOLD))
            input(c("  Press Enter to continue...", Color.YELLOW))

        elif choice == '2':
            networks = scan_wifi(active_iface, timeout=SCAN_TIMEOUT)
            if networks:
                display_results(networks, title="Scan Results")
                export_prompt(networks)
            input(c("  Press Enter to continue...", Color.YELLOW))

        elif choice == '3':
            analysis_menu(networks)

        elif choice == '4':
            report_menu(networks)

        elif choice == '5':
            os.system('cls' if IS_WINDOWS else 'clear')
            print_header("VIEW SAVED RESULTS")
            view_saved_results()
            input(c("\n  Press Enter to continue...", Color.YELLOW))

        elif choice == '6':
            print(c(f"\n  [+] Scan complete. Stay secured™. Exiting...\n",
                    Color.CYAN, Color.BOLD))
            break

        else:
            print(c("  ✘ Invalid option. Choose 1-6.", Color.RED))
            input(c("  Press Enter to continue...", Color.YELLOW))


if __name__ == "__main__":
    try:
        from suite_updater import check_for_updates
        check_for_updates(__file__)
        main()
    except KeyboardInterrupt:
        print(c("\n  [!] Interrupted. Exiting...\n", Color.YELLOW))