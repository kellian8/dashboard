"""Send a break signal to the dashboard process listening on port 8080."""

import os
import signal
import subprocess
import sys
from pathlib import Path

import psutil


_SERVER_PORT = 8080


_ALLOWED_DIRS = {
    Path(__file__).parent.parent.resolve(),         # dash-services/
    Path(__file__).parent.parent.parent.resolve(),  # repo root
}


def _is_dashboard_process(pid: str) -> bool:
    try:
        return Path(psutil.Process(int(pid)).cwd()) in _ALLOWED_DIRS
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return False


def stop(port: int = _SERVER_PORT):
    if sys.platform == "win32":
        result = subprocess.run(
            f"netstat -ano | findstr :{port} | findstr LISTENING",
            capture_output=True, text=True, shell=True
        )
        pids = {line.split()[-1] for line in result.stdout.splitlines() if line.strip()}
    else:
        result = subprocess.run(
            ["lsof", "-i", f":{port}", "-t", "-s", "TCP:LISTEN"],
            capture_output=True, text=True
        )
        pids = {line.strip() for line in result.stdout.splitlines() if line.strip()}

    if not pids:
        print(f"No process found listening on port {port}")
        sys.exit(1)

    for pid in pids:
        if not _is_dashboard_process(pid):
            print(f"PID {pid} on port {port} doesn't look like this app — aborting")
            sys.exit(1)
        os.kill(int(pid), signal.SIGBREAK if sys.platform == "win32" else signal.SIGTERM)
        print(f"Sent CTRL_BREAK to PID {pid}")


if __name__ == "__main__":
    stop()
