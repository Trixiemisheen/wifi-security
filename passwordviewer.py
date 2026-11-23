"""
Wi-Fi Profile Auditor - Extracts saved WiFi profiles and their pre-shared keys.
Authorized use: security assessments, penetration testing, and audit of your own systems.
"""
# the required libraries are: subprocess, re, sys, argparse use pip install argparse, the remaining are in-built.

import subprocess
import re
import sys
import argparse
from typing import Optional


def get_wifi_profiles() -> list[dict]:
    """
    Get all Wi-Fi profiles from the system.
    Returns a list of dicts with profile name and optional details.
    """
    try:
        output = subprocess.check_output(
            ["netsh", "wlan", "show", "profiles"],
            shell=True,
            stderr=subprocess.STDOUT,
            timeout=10
        ).decode('utf-8', errors='replace')
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"[!] Error executing netsh: {e}")
        print("[!] Are you on Windows? Do you have admin privileges?")
        sys.exit(1)
    except subprocess.TimeoutExpired:
        print("[!] Command timed out.")
        sys.exit(1)

    profiles = []
    # Handle multiple locales: "All User Profile" (en) / "Profil de tous les utilisateurs" (fr) / etc.
    # Fallback: grab anything after ":" on lines that look like profile entries
    for line in output.splitlines():
        if ":" in line and ("Profile" in line or "profil" in line.lower()):
            parts = line.split(":", 1)
            if len(parts) == 2 and parts[1].strip():
                profiles.append({
                    "name": parts[1].strip(),
                    "index": len(profiles) + 1
                })

    if not profiles:
        # More aggressive fallback: look for quoted names
        matches = re.findall(r'"([^"]+)"', output)
        profiles = [{"name": m, "index": i + 1} for i, m in enumerate(matches)]

    return profiles


def get_wifi_password(profile_name: str) -> Optional[str]:
    """
    Extract the password (key material) for a given Wi-Fi profile.
    Returns the password string or None if not found / inaccessible.
    """
    try:
        output = subprocess.check_output(
            f'netsh wlan show profile name="{profile_name}" key=clear',
            shell=True,
            stderr=subprocess.STDOUT,
            timeout=10
        ).decode('utf-8', errors='replace')
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return None

    # Extract the Key Content field
    match = re.search(
        r'Key Content\s*:\s*(.+?)\r?\n',
        output,
        re.IGNORECASE
    )
    if match:
        return match.group(1).strip()

    # Fallback: try "Contenu de la clé" (French) or other locales
    match = re.search(
        r'Contenu de la cl[ée]\s*:\s*(.+?)\r?\n',
        output,
        re.IGNORECASE
    )
    return match.group(1).strip() if match else None


def display_all_profiles(profiles: list[dict], show_passwords: bool = False) -> None:
    """Display all profiles in a formatted table."""
    print(f"\n{'#' :<4} {'SSID':<30} {'Password':<30}")
    print("-" * 68)
    for p in profiles:
        pwd = get_wifi_password(p["name"]) if show_passwords else "***"
        print(f"{p['index']:<4} {p['name']:<30} {str(pwd):<30}")


def export_to_csv(profiles: list[dict], filename: str = "wifi_profiles.csv") -> None:
    """Export profiles and passwords to a CSV file."""
    import csv
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["SSID", "Password"])
        for p in profiles:
            pwd = get_wifi_password(p["name"])
            writer.writerow([p["name"], pwd if pwd else "[No Password / Hidden]"])
    print(f"[+] Exported to {filename}")


def main():
    parser = argparse.ArgumentParser(
        description="Wi-Fi Profile Auditor - List and extract saved Wi-Fi credentials",
        epilog="Use responsibly on systems you own or have explicit authorization to test."
    )
    parser.add_argument(
        "-a", "--all", action="store_true",
        help="Show all profiles at once instead of interactive mode"
    )
    parser.add_argument(
        "-p", "--passwords", action="store_true",
        help="Display passwords inline (use with --all)"
    )
    parser.add_argument(
        "-e", "--export", metavar="FILE", nargs="?", const="wifi_profiles.csv",
        help="Export results to CSV file"
    )
    parser.add_argument(
        "-n", "--name", metavar="SSID",
        help="Directly fetch password for a specific profile name"
    )
    args = parser.parse_args()

    # Check for admin (optional - some profiles need it)
    try:
        import ctypes
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
        if not is_admin:
            print("[!] Note: Some profiles may not show passwords without admin rights.")
            print("[!] Re-run as Administrator if needed.\n")
    except (ImportError, AttributeError):
        pass

    profiles = get_wifi_profiles()
    if not profiles:
        print("[!] No Wi-Fi profiles found.")
        sys.exit(1)

    # Direct name lookup
    if args.name:
        pwd = get_wifi_password(args.name)
        if pwd:
            print(f"\n[+] SSID: {args.name}")
            print(f"    Password: {pwd}")
        else:
            print(f"[-] No password found for '{args.name}' (or profile doesn't exist).")
        return

    # Export mode
    if args.export:
        export_to_csv(profiles, args.export)
        return

    # Show all mode
    if args.all:
        display_all_profiles(profiles, show_passwords=args.passwords)
        # Still offer interactive drill-down
        print()
        ch = input("Enter profile number to view details (or just press Enter to exit): ").strip()
        if not ch:
            return
        try:
            idx = int(ch) - 1
            if 0 <= idx < len(profiles):
                show_single_profile(profiles[idx]["name"])
        except ValueError:
            pass
        return

    # --- Interactive mode (original behavior, enhanced) ---
    print(f"\n[+] Found {len(profiles)} Wi-Fi profile(s):\n")
    for p in profiles:
        print(f"  {p['index']}. {p['name']}")

    print()
    try:
        ch = input("Enter profile number to view details: ").strip()
        if not ch:
            return
        idx = int(ch) - 1
        if idx < 0 or idx >= len(profiles):
            print("[!] Invalid selection.")
            sys.exit(1)
        show_single_profile(profiles[idx]["name"])
    except (ValueError, IndexError):
        print("[!] Invalid input.")
        sys.exit(1)


def show_single_profile(wifi_name: str) -> None:
    """Display full profile details for a single SSID."""
    print(f"\n{'='*60}")
    print(f"  Profile: {wifi_name}")
    print(f"{'='*60}")
    try:
        result = subprocess.check_output(
            f'netsh wlan show profile name="{wifi_name}" key=clear',
            shell=True,
            stderr=subprocess.STDOUT,
            timeout=10
        ).decode('utf-8', errors='replace')
        print(f"\n{result}")
    except subprocess.CalledProcessError as e:
        print(f"[!] Error: {e.output.decode() if e.output else 'Unknown error'}")
    except subprocess.TimeoutExpired:
        print("[!] Command timed out.")


if __name__ == "__main__":
    from suite_updater import check_for_updates
    check_for_updates(__file__)
    main()