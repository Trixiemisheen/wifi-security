import os
import shutil
import subprocess
import sys


def check_for_updates(entrypoint=None):
    """Pull the shared repository once and restart the current entrypoint if it changed."""
    if os.environ.get("WIFI_SUITE_UPDATE_CHECKED") == "1":
        return
    os.environ["WIFI_SUITE_UPDATE_CHECKED"] = "1"

    if shutil.which("git") is None:
        print("[*] Git is not installed; update check skipped.\n")
        return

    project_dir = os.path.dirname(os.path.abspath(__file__))

    try:
        repository = subprocess.run(
            ["git", "-C", project_dir, "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if repository.returncode != 0 or repository.stdout.strip() != "true":
            print("[*] Project is not a Git checkout; update check skipped.\n")
            return

        before = subprocess.run(
            ["git", "-C", project_dir, "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if before.returncode != 0:
            print("[*] Could not determine the current revision.\n")
            return

        print("[*] Checking GitHub for repository updates...")
        result = subprocess.run(
            ["git", "-C", project_dir, "pull", "--ff-only"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            message = (result.stdout + result.stderr).strip()
            print("[-] Git update check failed.")
            if message:
                print(message)
            print("[*] Continuing with current version...\n")
            return

        after = subprocess.run(
            ["git", "-C", project_dir, "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if after.returncode != 0:
            print("[*] Could not verify the updated revision.\n")
            return

        if before.stdout.strip() != after.stdout.strip():
            print("[+] Repository updated successfully!")
            print("[!] Restarting script to apply updates...\n")
            restart = entrypoint or sys.argv[0]
            os.execv(sys.executable, [sys.executable, restart] + sys.argv[1:])
        else:
            print("[*] Project is up to date.\n")
    except (OSError, subprocess.SubprocessError) as e:
        print(f"[-] Git update check skipped/failed: {e}\n")
        print("[*] Continuing with current version...\n")
