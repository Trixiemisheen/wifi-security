"""Git-based updater (refactored from suite_updater.py). Returns a status string."""
import os
import shutil
import subprocess

_statuses = {"up-to-date", "updated", "skipped", "failed", "not-a-repo"}


def check_for_updates(project_dir: str | None = None) -> str:
    if os.environ.get("WIFI_SUITE_UPDATE_CHECKED") == "1":
        return "skipped"
    os.environ["WIFI_SUITE_UPDATE_CHECKED"] = "1"

    if shutil.which("git") is None:
        return "skipped"

    project_dir = project_dir or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    try:
        repo = subprocess.run(
            ["git", "-C", project_dir, "rev-parse", "--is-inside-work-tree"],
            capture_output=True, text=True, timeout=10)
        if repo.returncode != 0 or repo.stdout.strip() != "true":
            return "not-a-repo"

        before = subprocess.run(
            ["git", "-C", project_dir, "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=10)
        if before.returncode != 0:
            return "failed"

        result = subprocess.run(
            ["git", "-C", project_dir, "pull", "--ff-only"],
            capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            return "failed"

        after = subprocess.run(
            ["git", "-C", project_dir, "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=10)
        if after.returncode != 0:
            return "failed"

        if before.stdout.strip() != after.stdout.strip():
            return "updated"
        return "up-to-date"
    except (OSError, subprocess.SubprocessError):
        return "failed"