#!/usr/bin/env python3
"""Watches the Claude binary and re-patches after auto-updates."""

import platform
import subprocess
import time
from pathlib import Path

BINARY = Path("~/.local/bin/claude").expanduser()
OLD_SALT = b"friend-2026-401"
SALT_FILE = Path("~/.config/buddy-patcher/salt").expanduser()
IS_MACOS = platform.system() == "Darwin"


def get_salt():
    return SALT_FILE.read_text().strip().encode()


def patch_if_needed(new_salt):
    data = BINARY.read_bytes()
    if OLD_SALT not in data:
        return
    data = data.replace(OLD_SALT, new_salt)
    BINARY.write_bytes(data)
    if IS_MACOS:
        subprocess.run(["codesign", "--force", "--sign", "-", BINARY], check=True)
    subprocess.run(["logger", f"claude-buddy-patcher: patched{' and re-signed' if IS_MACOS else ''} {BINARY}"])


def main():
    salt = get_salt()
    patch_if_needed(salt)
    # Poll for binary changes (cross-platform)
    last_mtime = BINARY.stat().st_mtime if BINARY.exists() else 0
    while True:
        time.sleep(2)
        try:
            mtime = BINARY.stat().st_mtime
        except FileNotFoundError:
            continue
        if mtime != last_mtime:
            last_mtime = mtime
            time.sleep(1)
            patch_if_needed(salt)


if __name__ == "__main__":
    main()
