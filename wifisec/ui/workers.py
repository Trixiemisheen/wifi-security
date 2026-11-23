"""Background workers so no subprocess call ever blocks the GUI."""
import traceback

from PySide6.QtCore import QThread, Signal

from wifisec.core import scanner
from wifisec.core.password_auditor import get_wifi_profiles, get_wifi_password
from wifisec.services.updater import check_for_updates


class Worker(QThread):
    finished_ok = Signal(object)
    failed = Signal(str)
    log_line = Signal(str)

    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self._fn = fn
        self._args = args
        self._kwargs = kwargs
        self.cancelled = False

    def cancel(self):
        self.cancelled = True

    def cancel_check(self):
        return self.cancelled

    def run(self):
        try:
            result = self._fn(*self._args, **self._kwargs)
            self.finished_ok.emit(result)
        except Exception:
            self.failed.emit(traceback.format_exc(limit=5))


class ScanWorker(Worker):
    """Scans networks on the given interface."""

    def __init__(self, interface):
        super().__init__(self._job, interface)

    def _job(self, interface):
        nets = scanner.scan_wifi(interface)
        return scanner.security_assessment(nets)


class PasswordWorker(Worker):
    """Loads profiles and optionally their passwords."""

    def __init__(self, reveal=False):
        super().__init__(self._job, reveal)

    def _job(self, reveal):
        profiles = get_wifi_profiles()
        if reveal:
            for p in profiles:
                if self.cancel_check():
                    break
                p["password"] = get_wifi_password(p["name"]) or ""
        return profiles


class PentestWorker(Worker):
    """Runs the full audit_and_attack flow with live log forwarding."""

    def __init__(self, wordlist=None, iface=None, target_ssid=None,
                 max_targets=None, min_quality=None, connect=True,
                 use_pmkid=True, scan_clients_flag=True, hashcat_first=False):
        super().__init__(
            self._job, wordlist=wordlist, iface=iface,
            target_ssid=target_ssid, max_targets=max_targets,
            min_quality=min_quality, connect=connect,
            use_pmkid=use_pmkid, scan_clients_flag=scan_clients_flag,
            hashcat_first=hashcat_first,
        )

    def _job(self, **kwargs):
        from wifisec.core.pentest import audit_and_attack
        return audit_and_attack(
            cancel_check=self.cancel_check,
            log_callback=lambda m: self.log_line.emit(str(m)),
            **kwargs,
        )


class UpdateWorker(Worker):
    def __init__(self):
        super().__init__(check_for_updates)