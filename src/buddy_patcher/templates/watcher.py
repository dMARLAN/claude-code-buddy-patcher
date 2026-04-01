#!/usr/bin/env python3
"""Watches the Claude binary and re-patches after auto-updates."""

import subprocess
import time
from pathlib import Path

BINARY = Path("~/.local/bin/claude").expanduser()
OLD_SALT = b"friend-2026-401"
SALT_FILE = Path("~/.config/buddy-patcher/salt").expanduser()


def get_salt():
    return SALT_FILE.read_text().strip().encode()


def patch_if_needed(new_salt):
    data = BINARY.read_bytes()
    if OLD_SALT not in data:
        return
    data = data.replace(OLD_SALT, new_salt)
    BINARY.write_bytes(data)
    subprocess.run(["codesign", "--force", "--sign", "-", BINARY], check=True)
    subprocess.run(["logger", f"claude-buddy-patcher: patched and re-signed {BINARY}"])


def main():
    salt = get_salt()
    patch_if_needed(salt)
    proc = subprocess.Popen(["fswatch", "-o", str(BINARY)], stdout=subprocess.PIPE, text=True)
    assert proc.stdout is not None
    for _ in proc.stdout:
        time.sleep(1)
        patch_if_needed(salt)


if __name__ == "__main__":
    main()
