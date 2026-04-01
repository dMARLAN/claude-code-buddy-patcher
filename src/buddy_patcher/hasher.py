"""Fast wyhash via compiled C library — matches Bun.hash() exactly."""

import ctypes
import platform
import subprocess
import sys
from pathlib import Path

_SRC_DIR = Path(__file__).parent
_C_SRC = _SRC_DIR / "wyhash.c"
_LIB_SUFFIX = ".dylib" if platform.system() == "Darwin" else ".so"
_LIB_PATH = _SRC_DIR / f"_wyhash{_LIB_SUFFIX}"


def _compile_wyhash() -> None:
    """Compile the wyhash C library if it doesn't exist."""
    if _LIB_PATH.exists():
        return
    if not _C_SRC.exists():
        raise FileNotFoundError(f"wyhash.c not found at {_C_SRC}")
    # Target the same architecture as the running Python interpreter
    arch = platform.machine()  # e.g. "arm64", "x86_64"
    cmd = ["cc", "-O3", "-shared", "-fPIC", "-arch", arch, "-o", str(_LIB_PATH), str(_C_SRC)]
    subprocess.check_call(cmd, stdout=sys.stderr, stderr=sys.stderr)


_compile_wyhash()
_lib = ctypes.CDLL(str(_LIB_PATH))

_lib.wyhash_single.argtypes = [ctypes.c_char_p, ctypes.c_uint32]
_lib.wyhash_single.restype = ctypes.c_uint32

_lib.wyhash_batch.argtypes = [
    ctypes.c_char_p,                              # data (concatenated)
    ctypes.POINTER(ctypes.c_uint32),               # offsets
    ctypes.POINTER(ctypes.c_uint32),               # lengths
    ctypes.POINTER(ctypes.c_uint32),               # results
    ctypes.c_uint32,                               # count
]
_lib.wyhash_batch.restype = None


def wyhash(s: str) -> int:
    b = s.encode()
    return _lib.wyhash_single(b, len(b))


def wyhash_batch(strings: list[str]) -> list[int]:
    """Hash multiple strings in one C call."""
    n = len(strings)
    encoded = [s.encode() for s in strings]
    data = b"".join(encoded)

    offsets = (ctypes.c_uint32 * n)()
    lengths = (ctypes.c_uint32 * n)()
    results = (ctypes.c_uint32 * n)()

    off = 0
    for i, b in enumerate(encoded):
        offsets[i] = off
        lengths[i] = len(b)
        off += len(b)

    _lib.wyhash_batch(data, offsets, lengths, results, n)
    return list(results)
