"""Shared helpers for buddy-patcher commands."""

import json
from json import JSONDecodeError

import typer

from buddy_patcher.types import CLAUDE_CONFIG


def get_user_id() -> str:
    """Read the user's accountUuid from ~/.claude.json."""
    try:
        with CLAUDE_CONFIG.open() as f:
            config = json.load(f)
        uid = config.get("oauthAccount", {}).get("accountUuid")
        if uid:
            return uid
    except FileNotFoundError, JSONDecodeError:
        pass

    typer.echo("ERROR: Could not read accountUuid from ~/.claude.json", err=True)
    raise typer.Exit(1)


def wipe_companion() -> None:
    try:
        with CLAUDE_CONFIG.open() as f:
            config = json.load(f)
    except FileNotFoundError, json.JSONDecodeError:
        return

    if "companion" in config:
        name = config["companion"].get("name", "unknown")
        del config["companion"]

        with CLAUDE_CONFIG.open("w") as f:
            json.dump(config, f, indent=2)

        typer.echo(f'Removed companion "{name}" from config')
