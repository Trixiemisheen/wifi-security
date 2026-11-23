"""WiFi profile auditor (refactored from passwordviewer.py). No GUI, no input()."""
import csv
import re
import subprocess


def get_wifi_profiles() -> list[dict]:
    try:
        output = subprocess.check_output(
            ["netsh", "wlan", "show", "profiles"],
            shell=True,
            stderr=subprocess.STDOUT,
            timeout=10,
        ).decode("utf-8", errors="replace")
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return []

    profiles = []
    for line in output.splitlines():
        if ":" in line and ("Profile" in line or "profil" in line.lower()):
            parts = line.split(":", 1)
            if len(parts) == 2 and parts[1].strip():
                profiles.append({"name": parts[1].strip(), "index": len(profiles) + 1})

    if not profiles:
        matches = re.findall(r'"([^"]+)"', output)
        profiles = [{"name": m, "index": i + 1} for i, m in enumerate(matches)]

    return profiles


def get_wifi_password(profile_name: str) -> str | None:
    try:
        output = subprocess.check_output(
            f'netsh wlan show profile name="{profile_name}" key=clear',
            shell=True,
            stderr=subprocess.STDOUT,
            timeout=10,
        ).decode("utf-8", errors="replace")
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return None

    match = re.search(r"Key Content\s*:\s*(.+?)\r?\n", output, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    match = re.search(r"Contenu de la cl[ée]\s*:\s*(.+?)\r?\n", output, re.IGNORECASE)
    return match.group(1).strip() if match else None


def export_to_csv(profiles: list[dict], filename: str = "wifi_profiles.csv") -> str:
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["SSID", "Password"])
        for p in profiles:
            pwd = get_wifi_password(p["name"])
            writer.writerow([p["name"], pwd if pwd else "[No Password / Hidden]"])
    return filename