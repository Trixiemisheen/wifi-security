"""Native hashcat cracking + Windows profile install after success."""
import os
import subprocess

from wifisec.core.config import DATA_DIR
from wifisec.core.toolchain import find_tool

POTFILE = os.path.join(DATA_DIR, "hashcat.potfile")


def ssid_from_22000(line: str) -> str:
    """Extract the SSID from a WPA*02 hash line (ESSID is the 6th field, hex)."""
    parts = line.split("*")
    if len(parts) >= 6 and parts[0].startswith("WPA"):
        try:
            return bytes.fromhex(parts[5]).decode("utf-8", "replace")
        except ValueError:
            return ""
    return ""


def normalize_to_22000(path, log_callback=None):
    """Convert .cap/.pcapng/.hccapx to hashcat 22000 format."""
    log = log_callback or (lambda m: None)
    low = path.lower()
    if low.endswith(".22000"):
        return path
    tool = find_tool("hcxpcapngtool")
    if not tool:
        log("[!] hcxpcapngtool not found - cannot convert capture.")
        return None
    out = os.path.splitext(path)[0] + ".22000"
    try:
        subprocess.run([tool, "-o", out, path],
                       capture_output=True, text=True, timeout=180)
    except (OSError, subprocess.SubprocessError) as exc:
        log(f"[!] Conversion failed: {exc}")
        return None
    if os.path.exists(out) and os.path.getsize(out) > 0:
        return out
    log("[!] No PMKID/EAPOL found in capture.")
    return None


def crack(hashfile, wordlist, mode=22000, log_callback=None, cancel_check=None):
    """Run hashcat against hashfile. Returns list of {ssid, hash, password}."""
    log = log_callback or print
    hc = find_tool("hashcat")
    if not hc:
        raise RuntimeError("hashcat not found (PATH or tools/ folder).")
    if not os.path.isfile(hashfile):
        raise RuntimeError(f"hash file missing: {hashfile}")
    if wordlist and not os.path.isfile(wordlist):
        raise RuntimeError(f"wordlist missing: {wordlist}")

    cmd = [hc, "-m", str(mode), hashfile, "-a", "0",
           "--potfile-path", POTFILE, "--status", "--status-timer", "5",
           "--workload-profile", "3"]
    if wordlist:
        cmd.append(wordlist)
    log("[*] " + " ".join(cmd))

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, text=True,
                            errors="ignore", bufsize=1)
    try:
        for line in proc.stdout:
            log(line.rstrip())
            if cancel_check and cancel_check():
                proc.terminate()
                log("[!] Cancelled.")
                break
        proc.wait(timeout=60)
    except subprocess.TimeoutExpired:
        proc.kill()

    show = subprocess.run(
        [hc, "-m", str(mode), hashfile, "--show", "--potfile-path", POTFILE],
        capture_output=True, text=True, errors="ignore", timeout=120)
    results = []
    for line in show.stdout.splitlines():
        if ":" in line:
            digest, password = line.rsplit(":", 1)
            results.append({
                "hash": digest,
                "password": password,
                "ssid": ssid_from_22000(digest),
            })
    return results


def install_profile_and_connect(ssid, psk, auth="WPA2", log_callback=None):
    """Create a Windows WLAN profile and connect. Returns True on success."""
    log = log_callback or print
    if os.name != "nt":
        log("[!] Profile install is Windows-only.")
        return False
    from wifisec.core.pentest import (
        verify_connection,
        windows_add_profile,
        windows_connect,
    )
    if not windows_add_profile(ssid, auth=auth, password=psk):
        log(f"[!] Could not add profile for {ssid}")
        return False
    windows_connect(ssid)
    ok = verify_connection(ssid)
    log(f"[+] {'Connected' if ok else 'Profile installed, but not connected'} -> {ssid}")
    return ok