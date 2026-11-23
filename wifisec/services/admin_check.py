"""Admin/root detection."""
import os


def is_admin() -> bool:
    if os.name == "nt":
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except (ImportError, AttributeError):
            return False
    try:
        return os.geteuid() == 0
    except AttributeError:
        return True


def privilege_warning() -> str:
    if is_admin():
        return ""
    if os.name == "nt":
        return (
            "Some profiles may not show passwords without admin rights. "
            "Run as Administrator if needed."
        )
    return "On Linux, attacks require root (sudo)."