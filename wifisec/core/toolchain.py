"""Resolve external binaries from PATH or the bundled tools/ folder."""
import os
import shutil

from wifisec.core.config import BASE_DIR

TOOLS_DIR = os.path.join(BASE_DIR, "tools")

WINDOWS_TOOLS = ["hashcat", "hcxpcapngtool", "hcxdumptool", "etl2pcapng"]
LINUX_TOOLS = ["airmon-ng", "airodump-ng", "aireplay-ng", "aircrack-ng",
               "hcxdumptool", "hcxpcapngtool", "hashcat"]

INSTALL_HINTS = {
    "hashcat": (
        "Download the Windows release (hashcat-X.Y.Z.7z) from "
        "github.com/hashcat/hashcat/releases"
    ),
    "hcxpcapngtool": "Download hcxtools Windows build from github.com/ZerBea/hcxtools/releases",
    "hcxdumptool": "Download from github.com/ZerBea/hcxdumptool/releases (Linux only for capture)",
    "etl2pcapng": "Download from github.com/microsoft/etl2pcapng/releases",
}


def _names(name):
    return [name + ".exe", name] if os.name == "nt" else [name]


def find_tool(name):
    """Find a binary: PATH first, then tools/, then tools/<subdir>/."""
    for cand in _names(name):
        path = shutil.which(cand)
        if path:
            return path
    for cand in _names(name):
        path = os.path.join(TOOLS_DIR, cand)
        if os.path.isfile(path):
            return path
    if os.path.isdir(TOOLS_DIR):
        for entry in sorted(os.listdir(TOOLS_DIR)):
            sub = os.path.join(TOOLS_DIR, entry)
            if not os.path.isdir(sub):
                continue
            for cand in _names(name):
                path = os.path.join(sub, cand)
                if os.path.isfile(path):
                    return path
    return None


def tool_report(names=None):
    names = names or (WINDOWS_TOOLS if os.name == "nt" else LINUX_TOOLS)
    return {name: find_tool(name) for name in names}


def ensure_tools_dir():
    os.makedirs(TOOLS_DIR, exist_ok=True)
    return TOOLS_DIR