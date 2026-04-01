"""The 'uninstall' command: restore the original Claude binary and clean up."""

import shutil
import subprocess

import typer

from buddy_patcher.common import wipe_companion
from buddy_patcher.types import (
    BINARY,
    CONFIG_DIR,
    IS_MACOS,
    PLIST_PATH,
    PATCHER_SCRIPT,
    SYSTEMD_SERVICE,
    SYSTEMD_SERVICE_PATH,
)


def _stop_service() -> None:
    if IS_MACOS:
        subprocess.run(["launchctl", "unload", PLIST_PATH], capture_output=True)
        if PLIST_PATH.is_file():
            PLIST_PATH.unlink()
            typer.echo("Removed LaunchAgent")
    else:
        subprocess.run(
            ["systemctl", "--user", "disable", "--now", SYSTEMD_SERVICE],
            capture_output=True,
        )
        if SYSTEMD_SERVICE_PATH.is_file():
            SYSTEMD_SERVICE_PATH.unlink()
            typer.echo("Removed systemd user service")


def _restore_binary() -> None:
    backup = BINARY.with_suffix(".bak")

    if backup.is_file():
        shutil.copy2(backup, BINARY)
        if IS_MACOS:
            subprocess.run(["codesign", "--force", "--sign", "-", BINARY], check=True)
        typer.echo("Restored original binary from backup")
    else:
        typer.echo(f"WARNING: No backup found at {backup} — binary not restored")


def _clean_up() -> None:
    if PATCHER_SCRIPT.is_file():
        PATCHER_SCRIPT.unlink()
        typer.echo("Removed watcher script")

    if CONFIG_DIR.is_dir():
        shutil.rmtree(CONFIG_DIR)
        typer.echo("Removed config")


def uninstall() -> None:
    """Restore the original Claude binary and remove all buddy-patcher components."""
    typer.echo("Uninstalling buddy-patcher...")

    _stop_service()
    _restore_binary()
    _clean_up()
    wipe_companion()

    typer.echo("\nDone! Launch Claude and /buddy to get your original companion back.")
