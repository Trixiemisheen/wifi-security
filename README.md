# Wi-Fi Security & Assessment Toolkit

A collection of Python scripts designed for auditing local Wi-Fi networks, capturing pre-shared keys, performing authorized penetration tests, and retrieving stored profiles.

---

> **DISCLAIMER:**  
> This toolkit is provided strictly for **educational purposes** and **authorized security assessments** on systems you own or have explicit permission to audit. The author assumes no responsibility for misuse or illegal activities.

---

## 🛠️ Components & File Structure

Ensure all three files remain in the **same directory** for full functionality.

| File | Description | System Compatibility |
| :--- | :--- | :--- |
| **`wifisec.py`** | Core module providing underlying Wi-Fi scanning, management, and auditing capabilities. Required by `pentest.py`. | Linux / Windows |
| **`pentest.py`** | Wi-Fi assessment and attack companion. Relies directly on `wifisec.py`. | **Linux (Kali/VM recommended)** |
| **`passwordviewer.py`** | Standalone utility to extract and view saved Wi-Fi profiles and pre-shared keys on the local host. | Linux / Windows |

*Note: `pentest.py` will **not** work as a standalone script—it must be accompanied by `wifisec.py` within the same folder.*

---

## 📋 Dependencies & Installation

Most dependencies belong to the Python Standard Library (`os`, `sys`, `subprocess`, `re`, `csv`, `json`, `datetime`).

Install external packages via `pip`:

```bash
pip install tabulate argparse
🚀 Usage
1. Wi-Fi Assessment Companion (pentest.py)
Run pentest.py with elevated permissions on Linux to leverage full scanning, handshake capture, and cracking capabilities.

Command-Line Interface (CLI):

Bash
# Target automated assessment using a wordlist (up to 3 targets)
sudo python3 pentest.py --wordlist /usr/share/wordlists/rockyou.txt --max-targets 3

# Target a specific SSID without auto-connecting
sudo python3 pentest.py --target-ssid "MyLab" --no-connect
Importing as a Module:

Python
import pentest

# Run automated assessment against target list
result = pentest.auto_pwn(wordlist="wordlist.txt", max_targets=2)
print(result)
Behavior & Limits:

Logic: Automatically skips testing if already connected to --target-ssid. Scans and ranks targets in order (Open/WEP first, followed by strongest WPA/WPA2 signal), stopping after the first successful connection.

Platform Limit: Monitor mode, IV capture, and WPA/WPA2 handshake cracking require a Linux environment (Kali Linux or a Linux Virtual Machine with a supported wireless adapter). On Windows, operations are strictly limited to Open networks or saved profiles.

2. Wi-Fi Profile Auditor (passwordviewer.py)
Extract saved Wi-Fi profiles and their pre-shared cleartext keys from the current system:

Bash
python passwordviewer.py
📬 Contact & Support
For bug reports, improvements, or suggestions:

Email: misheentrixie@gmail.com

WhatsApp: +254791915925

Instagram: @trixiemisheen

🔍 Troubleshooting & Prerequisites for Linux (`pentest.py`)

For `pentest.py` to perform IV capture and WPA/WPA2 handshake cracking on Linux, your system must have the **Aircrack-ng suite** installed and an air-interface wireless adapter capable of **Monitor Mode** and **Packet Injection**.

---
sudo apt install hcxdumptool hcxtools hashcat

# 2) Full attack: PMKID + client-recon + handshake, JSON output
sudo python3 pentest.py --target-ssid "MyLab" --wordlist /usr/share/wordlists/rockyou.txt --format json

# 3) Just see who's on the air
sudo python3 pentest.py --clients --interface wlan0

# 4) Prefer GPU cracking on handshakes too
sudo python3 pentest.py --target-ssid "MyLab" --hashcat

### 1. Install Required System Tools

Install `aircrack-ng` and standard networking utilities using your package manager:

```bash
sudo apt update && sudo apt install -y aircrack-ng pciutils usbutils wireless-tools
2. Verify Adapter CapabilitiesEnsure your wireless network card supports monitor mode and packet injection:Bash# Identify your network interface (e.g., wlan0)
ip link show

# Check if the adapter supports Monitor Mode
iw list | grep -A 8 "Supported interface modes"
Look for monitor in the output list. Integrated Wi-Fi cards (or generic VM virtual network adapters) often lack monitor mode support—a USB Wi-Fi adapter (such as an Alfa AWUS036ACH or similar RT2870/RTL8812AU chipset) is typically required.3. Kill Interfering ProcessesBackground network managers often pull interfaces out of monitor mode or cause capture drops. Stop interfering processes before running assessments:Bash# Terminate processes interfering with monitor mode
sudo airmon-ng check kill
4. Enable Monitor Mode Manually (If Needed)If pentest.py fails to set the interface state automatically:Method A: Using airmon-ngBashsudo airmon-ng start wlan0
# The interface will rename to wlan0mon
Method B: Using iw / ipBashsudo ip link set wlan0 down
sudo iw dev wlan0 set type monitor
sudo ip link set wlan0 up
5. Common Common Error FixesSymptom / ErrorRoot CauseSolutionaircrack-ng: command not foundAircrack-ng suite is not installed.Run sudo apt install aircrack-ng.Operation not permittedScript executed without root privileges.Re-run with sudo python3 pentest.py ....No such device / Interface downWireless adapter not passed to VM.In VirtualBox/VMware, ensure the USB adapter is attached to the Guest OS, not the Host.Device or resource busyNetworkManager re-grabbed control.Run sudo airmon-ng check kill or stop NetworkManager (sudo systemctl stop NetworkManager).
