"""Companion roll logic — mirrors buddy/companion.ts exactly."""

import ctypes
from collections.abc import Callable, Sequence
from typing import Final

from buddy_patcher.types import (
    Companion,
    Rarity,
    Species,
    Eyes,
    Hat,
    Stat,
    RARITY_WEIGHTS,
    RARITY_FLOOR,
)

_ALL_SPECIES: Final[Sequence[Species]] = list(Species)
_ALL_EYES: Final[Sequence[Eyes]] = list(Eyes)
_ALL_HATS: Final[Sequence[Hat]] = list(Hat)
_ALL_STATS: Final[Sequence[Stat]] = list(Stat)


def _to_i32(x: int) -> int:
    """Convert to signed 32-bit int (JS `| 0` behavior)."""
    return ctypes.c_int32(x).value


def _to_u32(x: int) -> int:
    """Convert to unsigned 32-bit int (JS `>>> 0` behavior)."""
    return x & 0xFFFFFFFF


def _imul(a: int, b: int) -> int:
    """Equivalent to Math.imul — signed 32-bit truncating multiply."""
    return ctypes.c_int32(a * b).value


type Rng = Callable[[], float]


def mulberry32(seed: int) -> Rng:
    # JS: let a = seed >>> 0
    a = _to_u32(seed)

    def next_val() -> float:
        nonlocal a
        # JS: a |= 0
        a_signed = _to_i32(a)
        # JS: a = (a + 0x6d2b79f5) | 0
        a_signed = _to_i32(a_signed + 0x6D2B79F5)
        # JS: let t = Math.imul(a ^ (a >>> 15), 1 | a)
        t = _imul(_to_i32(a_signed ^ _to_u32(a_signed) >> 15), _to_i32(1 | a_signed))
        # JS: t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t
        t = _to_i32(t + _imul(_to_i32(t ^ (_to_u32(t) >> 7)), _to_i32(61 | t))) ^ t
        # JS: return ((t ^ (t >>> 14)) >>> 0) / 4294967296
        result = _to_u32(t ^ (_to_u32(t) >> 14))
        # Update a for next call (store as the signed value for next iteration)
        a = _to_u32(a_signed)
        return result / 4294967296

    return next_val


def _pick[T](rng: Rng, arr: Sequence[T]) -> T:
    return arr[int(rng() * len(arr))]


def _roll_rarity(rng: Rng) -> Rarity:
    threshold = rng() * 100

    for rarity in Rarity:
        threshold -= RARITY_WEIGHTS[rarity]
        if threshold < 0:
            return rarity

    return Rarity.COMMON


def _roll_stats(rng: Rng, rarity: Rarity) -> dict[Stat, int]:
    floor = RARITY_FLOOR[rarity]
    peak = _pick(rng, _ALL_STATS)
    dump = _pick(rng, _ALL_STATS)

    while dump == peak:
        dump = _pick(rng, _ALL_STATS)

    stats = {}
    for name in Stat:
        if name == peak:
            stats[name] = min(100, floor + 50 + int(rng() * 30))
        elif name == dump:
            stats[name] = max(1, floor - 10 + int(rng() * 15))
        else:
            stats[name] = floor + int(rng() * 40)

    return stats


def roll(hash32: int) -> Companion:
    rng = mulberry32(hash32)
    rarity = _roll_rarity(rng)
    species = _pick(rng, _ALL_SPECIES)
    eye = _pick(rng, _ALL_EYES)
    hat = Hat.NONE if rarity == Rarity.COMMON else _pick(rng, _ALL_HATS)
    shiny = rng() < 0.01
    stats = _roll_stats(rng, rarity)
    return Companion(
        rarity=rarity,
        species=species,
        eye=eye,
        hat=hat,
        shiny=shiny,
        stats=stats,
    )
