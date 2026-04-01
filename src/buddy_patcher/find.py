"""The 'find' command: brute-force search for a desired companion."""

import secrets
import threading

import typer
from rich.live import Live
from rich.text import Text
from typer import Option

from buddy_patcher.common import get_user_id
from buddy_patcher.types import CHARSET, Species, Eyes, Hat, Companion
from buddy_patcher.hasher import BunHasher
from buddy_patcher.roller import roll


def _matches_filters(
    r: Companion,
    species: str | None,
    eyes: str | None,
    hat: str | None,
    shiny: bool,
    rarity: str | None,
) -> bool:
    if rarity and r.rarity != rarity:
        return False
    if species and r.species != species:
        return False
    if eyes and r.eye != eyes:
        return False
    if hat and r.hat != hat:
        return False
    return not (shiny and not r.shiny)


def _status_line(found: int, count: int, attempts: int) -> Text:
    return Text(f"⏳ Searching... {found}/{count} found | {attempts:,} iterations checked", style="bold cyan")


def _format_result(index: int, attempts: int, salt: str, r: Companion) -> str:
    stats_str = " ".join(f"{k}:{v}" for k, v in r.stats.items())
    return (
        f"[{index}] after {attempts:,} attempts:\n"
        f"  Salt:    {salt}\n"
        f"  Rarity:  {r.rarity}{'  (SHINY!)' if r.shiny else ''}\n"
        f"  Species: {r.species}  |  Eyes: {r.eye}  |  Hat: {r.hat}\n"
        f"  Stats:   {stats_str}\n"
    )


def brute_force_search(
    uid: str,
    species: str | None = None,
    eyes: str | None = None,
    hat: str | None = None,
    shiny: bool = False,
    rarity: str | None = None,
    count: int = 5,
) -> list[tuple[str, Companion]]:
    """Run the brute-force search loop. Shared by `find` and `build` commands.

    Returns a list of (salt, Companion) tuples for all matches found.
    """
    typer.echo(
        f"Searching for: rarity={rarity or 'any'} "
        f"species={species or 'any'} hat={hat or 'any'} "
        f"eyes={eyes or 'any'} shiny={'yes' if shiny else 'any'}"
    )
    typer.echo("")

    found = 0
    attempts = 0
    results: list[tuple[str, Companion]] = []
    done = threading.Event()

    def _update_status(live: Live) -> None:
        while not done.wait(timeout=1.0):
            live.update(_status_line(found, count, attempts))

    with BunHasher() as hasher, Live(_status_line(0, count, 0), refresh_per_second=1) as live:
        ticker = threading.Thread(target=_update_status, args=(live,), daemon=True)
        ticker.start()

        while found < count:
            attempts += 1
            salt = "".join(secrets.choice(CHARSET) for _ in range(15))
            h = hasher.hash(uid + salt)
            r = roll(h)

            if not _matches_filters(r, species, eyes, hat, shiny, rarity):
                continue

            found += 1
            results.append((salt, r))
            live.console.print(_format_result(found, attempts, salt, r))
            live.update(_status_line(found, count, attempts))

        done.set()
        ticker.join()

    typer.echo(f"Done. {attempts:,} total attempts.")
    return results


def find(
    species: str | None = Option(None, help=f"Filter species: {', '.join(Species)}"),
    hat: str | None = Option(None, help=f"Filter hat: {', '.join(Hat)}"),
    eyes: str | None = Option(None, help=f"Filter eyes: {' '.join(Eyes)}"),
    shiny: bool = Option(False, help="Require shiny"),
    legendary: bool = Option(False, help="Require legendary rarity"),
    count: int = Option(5, help="Number of results to find"),
) -> None:
    """Brute-force search for a salt that gives your desired companion."""
    uid = get_user_id()
    brute_force_search(
        uid=uid,
        species=species,
        eyes=eyes,
        hat=hat,
        shiny=shiny,
        rarity="legendary" if legendary else None,
        count=count,
    )
    typer.echo("\nTo install: buddy-patcher install <salt>")
