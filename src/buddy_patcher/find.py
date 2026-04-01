"""The 'find' command: brute-force search for a desired companion."""

import multiprocessing
import os
import secrets
import threading

import typer
from rich.live import Live
from rich.text import Text
from typer import Option

from buddy_patcher.common import get_user_id
from buddy_patcher.types import CHARSET, Species, Eyes, Hat, Rarity, RARITY_WEIGHTS, Companion
from buddy_patcher.hasher import wyhash_batch
from buddy_patcher.roller import roll

BATCH_SIZE: int = 2048
SEARCH_RATE: int = 250_000  # approximate hashes per second


def calculate_odds(
    species: str | None = None,
    eyes: str | None = None,
    hat: str | None = None,
    shiny: bool = False,
    rarity: str | None = None,
) -> float:
    """Calculate the probability of a random roll matching the given filters.

    Returns a float between 0 and 1.
    """
    total_weight = sum(RARITY_WEIGHTS.values())  # 100

    p_species = 1 / len(Species) if species else 1.0
    p_eyes = 1 / len(Eyes) if eyes else 1.0
    p_shiny = 0.01 if shiny else 1.0

    # Rarity and hat are coupled: common always gets Hat.NONE
    if rarity:
        rarities = [Rarity(rarity)]
    else:
        rarities = list(Rarity)

    p_rarity_hat = 0.0
    for r in rarities:
        p_r = RARITY_WEIGHTS[r] / total_weight

        if hat is None:
            p_hat = 1.0
        elif r == Rarity.COMMON:
            # Common always has no hat
            p_hat = 1.0 if hat == Hat.NONE.value else 0.0
        else:
            # Non-common picks uniformly from all 8 hats
            p_hat = 1 / len(Hat)

        p_rarity_hat += p_r * p_hat

    return p_rarity_hat * p_species * p_eyes * p_shiny


def _format_time(est_seconds: float) -> str:
    if est_seconds < 1:
        return "< 1 second"
    if est_seconds < 60:
        return f"~{est_seconds:.0f} seconds"
    if est_seconds < 3600:
        return f"~{est_seconds / 60:.1f} minutes"
    return f"~{est_seconds / 3600:.1f} hours"


def format_odds(
    species: str | None = None,
    eyes: str | None = None,
    hat: str | None = None,
    shiny: bool = False,
    rarity: str | None = None,
    count: int = 5,
) -> str:
    """Return a formatted string showing odds and estimated search time."""
    odds = calculate_odds(species, eyes, hat, shiny, rarity)
    one_in = 1 / odds if odds > 0 else float("inf")

    expected_iters = count / odds if odds > 0 else float("inf")
    est_seconds = expected_iters / SEARCH_RATE

    return (
        f"Odds: 1 in {one_in:,.0f}  ({odds:.5%})"
        f"  |  Est. time for {count} finds @ ~{SEARCH_RATE:,}/sec: {_format_time(est_seconds)}"
    )


def format_odds_short(
    species: str | None = None,
    eyes: str | None = None,
    hat: str | None = None,
    shiny: bool = False,
    rarity: str | None = None,
    count: int = 5,
) -> str:
    """Short odds string for inline preview (e.g. wizard steps)."""
    odds = calculate_odds(species, eyes, hat, shiny, rarity)
    if odds <= 0:
        return "Odds: impossible"
    one_in = 1 / odds
    expected_iters = count / odds
    est_seconds = expected_iters / SEARCH_RATE
    return f"1 in {one_in:,.0f} | {count} finds: {_format_time(est_seconds)}"


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


def _gen_salts(n: int) -> list[str]:
    """Generate n random salts."""
    return [secrets.token_hex(8)[:15] for _ in range(n)]


def _worker(
    uid: str,
    species: str | None,
    eyes: str | None,
    hat: str | None,
    shiny: bool,
    rarity: str | None,
    result_queue: multiprocessing.Queue,
    stop_event: multiprocessing.Event,
    attempt_counter: multiprocessing.Value,
) -> None:
    """Worker process: hash batches and send matches back via queue."""
    while not stop_event.is_set():
        salts = _gen_salts(BATCH_SIZE)
        strings = [uid + s for s in salts]
        hashes = wyhash_batch(strings)

        local_matches = []
        for i, h in enumerate(hashes):
            r = roll(h)
            if _matches_filters(r, species, eyes, hat, shiny, rarity):
                local_matches.append((salts[i], r))

        with attempt_counter.get_lock():
            attempt_counter.value += BATCH_SIZE

        for match in local_matches:
            result_queue.put(match)


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
    typer.echo(format_odds(species, eyes, hat, shiny, rarity, count))
    typer.echo("")

    num_workers = max(1, os.cpu_count() or 1)
    result_queue: multiprocessing.Queue = multiprocessing.Queue()
    stop_event = multiprocessing.Event()
    attempt_counter = multiprocessing.Value("Q", 0)  # unsigned long long

    workers = []
    for _ in range(num_workers):
        p = multiprocessing.Process(
            target=_worker,
            args=(uid, species, eyes, hat, shiny, rarity, result_queue, stop_event, attempt_counter),
        )
        p.daemon = True
        p.start()
        workers.append(p)

    results: list[tuple[str, Companion]] = []
    found = 0
    done = threading.Event()

    def _update_status(live: Live) -> None:
        while not done.wait(timeout=0.5):
            live.update(_status_line(found, count, attempt_counter.value))

    with Live(_status_line(0, count, 0), refresh_per_second=2) as live:
        ticker = threading.Thread(target=_update_status, args=(live,), daemon=True)
        ticker.start()

        while found < count:
            match = result_queue.get()
            found += 1
            salt, r = match
            results.append((salt, r))
            live.console.print(_format_result(found, attempt_counter.value, salt, r))
            live.update(_status_line(found, count, attempt_counter.value))

        stop_event.set()
        done.set()
        ticker.join()

    for p in workers:
        p.join(timeout=2)
        if p.is_alive():
            p.kill()

    typer.echo(f"Done. {attempt_counter.value:,} total attempts across {num_workers} workers.")
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
