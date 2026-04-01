"""Single Typer CLI: find, build, install, uninstall."""

import typer

from buddy_patcher.build import build
from buddy_patcher.find import find
from buddy_patcher.install import install
from buddy_patcher.uninstall import uninstall

app = typer.Typer(help="Choose your Claude Code /buddy companion.", add_completion=False)
app.command()(build)
app.command()(find)
app.command()(install)
app.command()(uninstall)
