"""WiFi Security Suite — Unified Launcher
Trixie Misheen™"""

MASTER_CREDIT = "WiFi Security Suite v4.0 | Created by Trixie Misheen™"


import sys
import os
import hashlib
import subprocess

# 1. Hardcode the expected SHA-256 hash of your original credit line
EXPECTED_CREDIT_HASH = "9f49728ac2aa6dc85bf3c9791baf730363c13ab7eeca04f060cd552743270b3c"

# 2. Your actual visible banner string
BANNER_CREDIT = "WiFi Security Suite v4.0 | Created by Trixie Misheen"

def check_file_integrity(filepath, expected_hash):
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest() == expected_hash

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


TOOLS = {
    "1": ("wifisec.py",        "📡  Scan & Analyze WiFi Networks"),
    "2": ("pentest.py",        "⚔️   Attack Networks (handshake/WEP crack)"),
    "3": ("passwordviewer.py", "🔑  Dump Stored Wi-Fi Passwords"),
}

def main():
    print("WiFi Security Suite v4.0 — by TRIXIE MISHEEN™\n")
    for k, (_, desc) in TOOLS.items():
        print(f"  {k}. {desc}")
    
    ch = input("\nSelect tool: ").strip()
    if ch in TOOLS:
        script = TOOLS[ch][0]
        script_path = os.path.join(os.path.dirname(__file__), script)
        args = sys.argv[1:] if ch == "2" else []  # pass CLI args only to pentest
        
        # subprocess handles spaces in paths safely
        subprocess.run([sys.executable, script_path] + args)
    else:
        print("Invalid choice.")

if __name__ == "__main__":
    from suite_updater import check_for_updates
    check_for_updates(__file__)
    main()