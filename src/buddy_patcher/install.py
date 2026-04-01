"""The 'install' command: patch the Claude binary and set up auto-re-patching."""

import shutil
import subprocess
from importlib.resources import files

import typer

from buddy_patcher.common import wipe_companion
from buddy_patcher.types import (
    BINARY,
    IS_MACOS,
    OLD_SALT,
    CONFIG_DIR,
    SALT_FILE,
    PLIST_LABEL,
    PLIST_PATH,
    PATCHER_SCRIPT,
    SYSTEMD_SERVICE,
    SYSTEMD_SERVICE_PATH,
    SYSTEMD_USER_DIR,
)


def _validate_salt(salt: str) -> None:
    if len(salt) != 15:
        typer.echo(f"ERROR: Salt must be exactly 15 characters (got {len(salt)}).", err=True)
        raise typer.Exit(1)


def _check_deps() -> None:
    missing = []
    if not shutil.which("bun"):
        missing.append("bun")
    if missing:
        typer.echo(f"Missing dependencies: {', '.join(missing)}")
        raise typer.Exit(1)


def _check_binary() -> None:
    if not BINARY.is_file():
        typer.echo(f"ERROR: Claude binary not found at {BINARY}", err=True)
        raise typer.Exit(1)


def _save_salt(salt: str) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    SALT_FILE.write_text(salt)
    typer.echo(f"Saved salt to {SALT_FILE}")


def _backup_binary() -> None:
    backup = BINARY.with_suffix(".bak")
    if backup.is_file():
        typer.echo(f"Backup already exists at {backup} — keeping original")
        return
    shutil.copy2(BINARY, backup)
    typer.echo(f"Backup saved to {backup}")


def _patch_binary(salt: str, prev_salt: str | None = None) -> None:
    data = BINARY.read_bytes()
    new = salt.encode()

    # Try the original hardcoded salt first
    target = OLD_SALT
    count = data.count(target)

    # Fall back to previously-installed custom salt
    if count == 0 and prev_salt and prev_salt.encode() != new:
        target = prev_salt.encode()
        count = data.count(target)

    if count == 0:
        typer.echo("WARNING: No known salt found in binary — cannot patch.")
        return

    data = data.replace(target, new)
    BINARY.write_bytes(data)
    if IS_MACOS:
        subprocess.run(["codesign", "--force", "--sign", "-", BINARY], check=True)
    typer.echo(f"Patched {count} occurrence(s)" + (" and re-signed" if IS_MACOS else ""))


def _install_watcher() -> None:
    """Install the standalone watcher script to ~/bin/."""
    script = files("buddy_patcher.templates").joinpath("watcher.py").read_text()
    PATCHER_SCRIPT.parent.mkdir(parents=True, exist_ok=True)
    PATCHER_SCRIPT.write_text(script)
    PATCHER_SCRIPT.chmod(0o755)
    typer.echo(f"Installed watcher to {PATCHER_SCRIPT}")


def _install_launchagent() -> None:
    subprocess.run(["launchctl", "unload", PLIST_PATH], capture_output=True)
    template = files("buddy_patcher.templates").joinpath("launchagent.plist").read_text()
    plist = template.format(plist_label=PLIST_LABEL, patcher_script=PATCHER_SCRIPT)
    PLIST_PATH.parent.mkdir(parents=True, exist_ok=True)
    PLIST_PATH.write_text(plist)
    subprocess.run(["launchctl", "load", PLIST_PATH], check=True)
    typer.echo("LaunchAgent installed and loaded")


def _install_systemd_service() -> None:
    template = files("buddy_patcher.templates").joinpath("buddy-patcher.service").read_text()
    service = template.format(patcher_script=PATCHER_SCRIPT)
    SYSTEMD_USER_DIR.mkdir(parents=True, exist_ok=True)
    SYSTEMD_SERVICE_PATH.write_text(service)
    subprocess.run(["systemctl", "--user", "daemon-reload"], check=True)
    subprocess.run(["systemctl", "--user", "enable", "--now", SYSTEMD_SERVICE], check=True)
    typer.echo("systemd user service installed and started")


def install(
    salt: str = typer.Argument(help="15-character salt from 'buddy-patcher find'"),
) -> None:
    """Patch the Claude binary with a chosen salt and set up auto-re-patching."""
    _validate_salt(salt)
    _check_deps()
    _check_binary()
    prev_salt = SALT_FILE.read_text().strip() if SALT_FILE.is_file() else None
    _save_salt(salt)
    _backup_binary()
    _patch_binary(salt, prev_salt)
    wipe_companion()
    _install_watcher()
    if IS_MACOS:
        _install_launchagent()
    else:
        _install_systemd_service()
    typer.echo("\nDone! Launch Claude and run /buddy to hatch your new companion.")
