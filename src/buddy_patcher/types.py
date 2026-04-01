"""Companion types and constants — mirrors buddy/companion.ts exactly."""

import platform
import string
from dataclasses import dataclass
from enum import StrEnum, auto
from pathlib import Path
from typing import Final

IS_MACOS: Final[bool] = platform.system() == "Darwin"


class Rarity(StrEnum):
    COMMON = auto()
    UNCOMMON = auto()
    RARE = auto()
    EPIC = auto()
    LEGENDARY = auto()


class Species(StrEnum):
    DUCK = auto()
    GOOSE = auto()
    BLOB = auto()
    CAT = auto()
    DRAGON = auto()
    OCTOPUS = auto()
    OWL = auto()
    PENGUIN = auto()
    TURTLE = auto()
    SNAIL = auto()
    GHOST = auto()
    AXOLOTL = auto()
    CAPYBARA = auto()
    CACTUS = auto()
    ROBOT = auto()
    RABBIT = auto()
    MUSHROOM = auto()
    CHONK = auto()


class Eyes(StrEnum):
    DOT = "·"
    STAR = "✦"
    CROSS = "×"
    CIRCLE = "◉"
    AT = "@"
    DEGREE = "°"


class Hat(StrEnum):
    NONE = auto()
    CROWN = auto()
    TOPHAT = auto()
    PROPELLER = auto()
    HALO = auto()
    WIZARD = auto()
    BEANIE = auto()
    TINYDUCK = auto()


class Stat(StrEnum):
    DEBUGGING = "DEBUGGING"
    PATIENCE = "PATIENCE"
    CHAOS = "CHAOS"
    WISDOM = "WISDOM"
    SNARK = "SNARK"


@dataclass(frozen=True, slots=True)
class Companion:
    rarity: Rarity
    species: Species
    eye: Eyes
    hat: Hat
    shiny: bool
    stats: dict[Stat, int]


RARITY_WEIGHTS = {
    Rarity.COMMON: 60,
    Rarity.UNCOMMON: 25,
    Rarity.RARE: 10,
    Rarity.EPIC: 4,
    Rarity.LEGENDARY: 1,
}

RARITY_FLOOR = {
    Rarity.COMMON: 5,
    Rarity.UNCOMMON: 15,
    Rarity.RARE: 25,
    Rarity.EPIC: 35,
    Rarity.LEGENDARY: 50,
}

BINARY: Final[Path] = Path("~/.local/bin/claude").expanduser()
OLD_SALT: Final[bytes] = b"friend-2026-401"
CONFIG_DIR: Final[Path] = Path("~/.config/buddy-patcher").expanduser()
SALT_FILE: Final[Path] = CONFIG_DIR / "salt"
PATCHER_SCRIPT: Final[Path] = Path("~/bin/buddy-patcher-watch.py").expanduser()
CLAUDE_CONFIG: Final[Path] = Path("~/.claude.json").expanduser()
CHARSET: Final[str] = string.ascii_lowercase + string.digits

# macOS LaunchAgent constants
PLIST_LABEL: Final[str] = "com.user.claude-buddy-patcher"
PLIST_PATH: Final[Path] = Path(f"~/Library/LaunchAgents/{PLIST_LABEL}.plist").expanduser()

# Linux systemd constants
SYSTEMD_USER_DIR: Final[Path] = Path("~/.config/systemd/user").expanduser()
SYSTEMD_SERVICE: Final[str] = "claude-buddy-patcher.service"
SYSTEMD_SERVICE_PATH: Final[Path] = SYSTEMD_USER_DIR / SYSTEMD_SERVICE
