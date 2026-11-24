"""Experimental native Windows 802.11 capture: netsh trace -> pcapng -> 22000."""
import os
import subprocess
import time

from wifisec.core.toolchain import find_tool


def is_supported():
    return os.name == "nt"


def capture_wireless(duration=30, out_dir=None, log_callback=None,
                     cancel_check=None):
    """Passive capture only (no packet injection on Windows).

    Returns path to .22000 if usable, else the raw .pcapng/.etl, else None.
    """
    log = log_callback or print
    if not is_supported():
        log("[!] netsh trace capture is Windows-only.")
        return None
    out_dir = out_dir or os.getcwd()
    os.makedirs(out_dir, exist_ok=True)
    etl = os.path.join(out_dir, f"wifi_trace_{int(time.time())}.etl")

    subprocess.run(["netsh", "trace", "stop"], capture_output=True)
    start = subprocess.run(
        ["netsh", "trace", "start", f"tracefile={etl}",
         "capture=yes", "wireless=yes", "overwrite=yes"],
        capture_output=True, text=True, errors="ignore")
    if start.returncode != 0:
        log("[!] netsh trace failed: " + (start.stdout + start.stderr)[-300:])
        return None

    log(f"[*] Capturing 802.11 frames for {duration}s ...")
    waited = 0
    while waited < duration:
        if cancel_check and cancel_check():
            break
        time.sleep(1)
        waited += 1
    subprocess.run(["netsh", "trace", "stop"], capture_output=True)

    if not os.path.exists(etl):
        log("[!] No trace file produced (driver may not support wireless capture).")
        return None

    conv = find_tool("etl2pcapng")
    if not conv:
        log("[!] etl2pcapng missing - install it to convert the .etl file.")
        return etl
    pcap = etl[:-4] + ".pcapng"
    subprocess.run([conv, etl, pcap], capture_output=True, timeout=180)

    hcx = find_tool("hcxpcapngtool")
    if hcx and os.path.exists(pcap):
        h22 = etl[:-4] + ".22000"
        subprocess.run([hcx, "-o", h22, pcap], capture_output=True, timeout=180)
        if os.path.exists(h22) and os.path.getsize(h22) > 0:
            log(f"[+] Hash ready: {h22}")
            return h22
        log("[i] Converted, but no PMKID/EAPOL in this window.")
    return pcap