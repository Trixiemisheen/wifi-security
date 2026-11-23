"""Central configuration for WiFi Security Suite."""
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
WORK_DIR = os.path.join(BASE_DIR, "attack_work")

for _d in (DATA_DIR, LOGS_DIR, REPORTS_DIR, WORK_DIR):
    os.makedirs(_d, exist_ok=True)

LOG_FILE = os.path.join(LOGS_DIR, "wifi_security_tool.log")
RESULTS_FILE = os.path.join(DATA_DIR, "network.csv")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")

TOOL_NAME = "WiFi Security Suite"
TOOL_VERSION = "4.1.0"
AUTHOR = "Trixie Misheen"
BANNER_CREDIT = "WiFi Security Suite v4.0 | Created by Trixie Misheen"

IS_WINDOWS = (os.name == "nt")

SCAN_TIMEOUT = 10

# Pentest defaults
PENTEST_CONFIG = {
    "wordlist": os.path.join(BASE_DIR, "wordlist.txt"),
    "work_dir": WORK_DIR,
    "scan_timeout": 10,
    "deauth_count": 5,
    "handshake_wait": 45,
    "crack_timeout": 300,
    "connect_wait": 25,
    "min_quality": 30,
    "max_targets": 3,
    "pmkid_wait": 20,
    "client_scan": 15,
}