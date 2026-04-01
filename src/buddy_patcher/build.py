"""Interactive 'build' command: choose companion traits with arrow-key menus."""

from __future__ import annotations

from collections.abc import Callable
from typing import Final

import questionary
from prompt_toolkit.application import Application
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import HSplit, Layout, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.widgets import Frame
from rich.console import Console
from rich.panel import Panel
from typer import Option

from buddy_patcher.common import get_user_id
from buddy_patcher.find import brute_force_search
from buddy_patcher.install import install as run_install
from buddy_patcher.sprites import render_sprite
from buddy_patcher.types import Companion, Eyes, Hat, Rarity, Species

ANY_LABEL: Final[str] = "Any"
console = Console()

RARITY_COLORS: Final[dict[Rarity, str]] = {
    Rarity.COMMON: "",
    Rarity.UNCOMMON: "ansigreen",
    Rarity.RARE: "ansiblue",
    Rarity.EPIC: "ansimagenta",
    Rarity.LEGENDARY: "ansiyellow",
}


def _preview_lines(
    species: Species | None = None,
    eye: Eyes | None = None,
    hat: Hat | None = None,
    rarity: Rarity | None = None,
    shiny: bool | None = None,
) -> list[str]:
    """Build the preview content from current selections."""
    if species is None:
        sprite = ["", "    (no species yet)", ""]
    else:
        sprite = render_sprite(species, eye or Eyes.DOT, hat or Hat.NONE)

    info_parts = [
        *([] if not species else [f"Species: {species.value}"]),
        *([] if not eye else [f"Eyes: {eye.value}"]),
        *([] if not rarity else [f"Rarity: {rarity.value}"]),
        *([] if not hat or hat == Hat.NONE else [f"Hat: {hat.value}"]),
        *(["Shiny: yes ✨"] if shiny is True else []),
    ]

    lines = sprite[:]
    if info_parts:
        lines.append("")
        lines.append("  ".join(info_parts))
    return lines


def _rarity_description(r: Rarity) -> str:
    return {
        Rarity.COMMON: "60% — no hat",
        Rarity.UNCOMMON: "25%",
        Rarity.RARE: "10%",
        Rarity.EPIC: "4%",
        Rarity.LEGENDARY: "1%",
    }[r]


# ---------------------------------------------------------------------------
# Custom arrow-key selector with live preview
# ---------------------------------------------------------------------------


def _make_select_keybindings(options: list[str], index: list[int]) -> KeyBindings:
    """Create arrow-key/j-k/enter/ctrl-c bindings for the selector."""
    kb = KeyBindings()

    @kb.add("up")
    @kb.add("k")
    def _up(_event: object) -> None:
        index[0] = (index[0] - 1) % len(options)

    @kb.add("down")
    @kb.add("j")
    def _down(_event: object) -> None:
        index[0] = (index[0] + 1) % len(options)

    @kb.add("enter")
    def _enter(event: object) -> None:
        event.app.exit(result=options[index[0]])  # type: ignore[union-attr]

    @kb.add("c-c")
    def _abort(event: object) -> None:
        event.app.exit(result=None)  # type: ignore[union-attr]

    return kb


def _live_select(
    title: str,
    choices: list[str],
    preview_fn: Callable[[str], list[str]],
    color: str = "",
    color_fn: Callable[[str], str] | None = None,
    include_any: bool = True,
) -> str | None:
    """Arrow-key select with a live-updating preview above the choices.

    *color* applies a fixed ANSI style to the preview text.
    *color_fn*, if given, overrides *color* dynamically per highlighted option.
    *include_any* prepends an "Any" option when True (default).

    Returns the selected value, or None if 'Any' was chosen.
    Raises KeyboardInterrupt on Ctrl-C.
    """
    options = [ANY_LABEL, *choices] if include_any else list(choices)
    index = [0]  # mutable so closures can update

    def _get_preview_text() -> FormattedText:
        current = options[index[0]]
        lines = preview_fn(current)
        effective = color_fn(current) if color_fn else color
        return FormattedText([(effective, line + "\n") for line in lines])

    def _get_choices_text() -> FormattedText:
        fragments = [("bold", f" {title}\n")]
        for i, opt in enumerate(options):
            style = "bold fg:ansigreen" if i == index[0] else ""
            prefix = " ❯ " if i == index[0] else "   "
            fragments.append((style, f"{prefix}{opt}\n"))
        return FormattedText(fragments)

    preview_window = Window(FormattedTextControl(_get_preview_text), height=8, dont_extend_height=True)
    layout = Layout(
        HSplit([
            Frame(preview_window, title="Your Companion"),
            Window(FormattedTextControl(_get_choices_text)),
        ])
    )

    app: Application[str | None] = Application(
        layout=layout, key_bindings=_make_select_keybindings(options, index), full_screen=True
    )
    result = app.run()

    if result is None:
        raise KeyboardInterrupt
    return None if result == ANY_LABEL else result


# ---------------------------------------------------------------------------
# Wizard step helpers
# ---------------------------------------------------------------------------

RICH_RARITY_STYLES: Final[dict[Rarity, str]] = {
    Rarity.COMMON: "",
    Rarity.UNCOMMON: "green",
    Rarity.RARE: "blue",
    Rarity.EPIC: "magenta",
    Rarity.LEGENDARY: "yellow",
}


def _pick_species() -> Species | None:
    def preview(val: str) -> list[str]:
        sp = Species(val) if val != ANY_LABEL else None
        return _preview_lines(species=sp)

    result = _live_select("Choose a species:", [s.value for s in Species], preview)
    return Species(result) if result else None


def _pick_eyes(species: Species | None) -> Eyes | None:
    display = {f"{e.value}  ({e.name.lower()})": e for e in Eyes}

    def preview(val: str) -> list[str]:
        return _preview_lines(species=species, eye=display.get(val))

    result = _live_select("Choose eyes:", list(display.keys()), preview)
    return display[result] if result else None


def _pick_rarity(species: Species | None, eye: Eyes | None) -> Rarity | None:
    display = {f"{r.value}  ({_rarity_description(r)})": r for r in Rarity}

    def preview(val: str) -> list[str]:
        return _preview_lines(species=species, eye=eye, rarity=display.get(val))

    def color_for(val: str) -> str:
        r = display.get(val)
        return RARITY_COLORS.get(r, "") if r else ""

    result = _live_select("Choose rarity:", list(display.keys()), preview, color_fn=color_for)
    return display[result] if result else None


def _pick_hat(species: Species | None, eye: Eyes | None, rarity: Rarity | None) -> Hat | None:
    rarity_color = RARITY_COLORS.get(rarity, "") if rarity else ""

    if rarity == Rarity.COMMON:
        return Hat.NONE

    def preview(val: str) -> list[str]:
        h = Hat(val) if val != ANY_LABEL else None
        return _preview_lines(species=species, eye=eye, rarity=rarity, hat=h)

    result = _live_select("Choose a hat:", [h.value for h in Hat], preview, color=rarity_color)
    return Hat(result) if result else None


def _pick_shiny(species: Species | None, eye: Eyes | None, rarity: Rarity | None, hat: Hat | None) -> bool:
    rarity_color = RARITY_COLORS.get(rarity, "") if rarity else ""

    def preview(val: str) -> list[str]:
        s = True if val == "yes" else None
        lines = _preview_lines(species=species, eye=eye, rarity=rarity, hat=hat, shiny=s)
        lines.append("")
        lines.append("  (cosmetic only — shows on hatch card)")
        return lines

    result = _live_select("Require shiny?", ["yes", "no"], preview, color=rarity_color, include_any=False)
    return result == "yes"


def _show_confirmation(
    species: Species | None, eye: Eyes | None, rarity: Rarity | None, hat: Hat | None, shiny: bool
) -> bool:
    """Show final build and ask for confirmation. Returns True to proceed."""
    console.clear()
    text = "\n".join(_preview_lines(species=species, eye=eye, rarity=rarity, hat=hat, shiny=shiny or None))
    style = RICH_RARITY_STYLES.get(rarity, "") if rarity else ""
    panel_text = f"[{style}]{text}[/{style}]" if style else text
    console.print(Panel(panel_text, title="Your Companion", expand=False))
    console.print()
    return questionary.confirm("Start searching?", default=True).ask()


# ---------------------------------------------------------------------------
# Build command
# ---------------------------------------------------------------------------


def _pick_companion_to_install(results: list[tuple[str, Companion]]) -> str | None:
    """Let the user pick one of the found companions to install. Returns the salt or None."""

    def _label(i: int, salt: str, c: Companion) -> str:
        shiny_tag = "  SHINY!" if c.shiny else ""
        hat_tag = f"  Hat: {c.hat}" if c.hat != Hat.NONE.value else ""
        return f"[{i + 1}] {c.species}  Eyes: {c.eye}{hat_tag}  ({c.rarity}{shiny_tag})"

    def preview(val: str) -> list[str]:
        if val == ANY_LABEL:
            return ["", "    (skip install)", ""]
        idx = int(val.split("]")[0].lstrip("[")) - 1
        salt, comp = results[idx]
        sp = Species(comp.species)
        ey = Eyes(comp.eye)
        ht = Hat(comp.hat)
        lines = render_sprite(sp, ey, ht)
        stats_str = "  ".join(f"{k}:{v}" for k, v in comp.stats.items())
        lines.append("")
        lines.append(f"Salt: {salt}")
        lines.append(stats_str)
        return lines

    def color_for(val: str) -> str:
        if val == ANY_LABEL:
            return ""
        idx = int(val.split("]")[0].lstrip("[")) - 1
        _, comp = results[idx]
        return RARITY_COLORS.get(Rarity(comp.rarity), "")

    labels = [_label(i, s, c) for i, (s, c) in enumerate(results)]
    result = _live_select(
        "Choose a companion to install:",
        labels,
        preview,
        color_fn=color_for,
        include_any=True,
    )
    if result is None:
        return None
    idx = int(result.split("]")[0].lstrip("[")) - 1
    return results[idx][0]


def build(
    count: int = Option(5, help="Number of results to find"),
) -> None:
    """Interactively choose companion traits, then brute-force search."""
    uid = get_user_id()

    try:
        species = _pick_species()
        eye = _pick_eyes(species)
        rarity = _pick_rarity(species, eye)
        hat = _pick_hat(species, eye, rarity)
        shiny = _pick_shiny(species, eye, rarity, hat)

        if not _show_confirmation(species, eye, rarity, hat, shiny):
            console.print("Cancelled.")
            return

    except KeyboardInterrupt:
        console.print("\nCancelled.")
        return

    results = brute_force_search(
        uid=uid,
        species=species.value if species else None,
        eyes=eye.value if eye else None,
        hat=hat.value if hat else None,
        shiny=shiny,
        rarity=rarity.value if rarity else None,
        count=count,
    )

    if not results:
        return

    try:
        salt = _pick_companion_to_install(results)
    except KeyboardInterrupt:
        console.print("\nSkipped install.")
        return

    if salt is None:
        console.print("Skipped install.")
        return

    console.print(f"\nInstalling companion with salt: [bold]{salt}[/bold]\n")
    run_install(salt)
