"""Streaming interface to Bun.hash() via a long-lived subprocess."""

import subprocess
from pathlib import Path

_HASH_SCRIPT = Path(__file__).parent / "bun_hash.mjs"


class BunHasher:
    """Spawns a single bun process, sends strings over stdin, reads uint32 hashes from stdout."""

    def __init__(self) -> None:
        self.__proc = subprocess.Popen(
            ["bun", _HASH_SCRIPT],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
        )

    def hash(self, s: str) -> int:
        assert self.__proc.stdin is not None
        assert self.__proc.stdout is not None

        self.__proc.stdin.write(s + "\n")
        self.__proc.stdin.flush()

        return int(self.__proc.stdout.readline().strip())

    def close(self) -> None:
        assert self.__proc.stdin is not None

        self.__proc.stdin.close()
        self.__proc.wait()

    def __enter__(self) -> BunHasher:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
