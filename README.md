# buddy-patcher

Choose your Claude Code `/buddy` companion.

## Requirements

- macOS (Apple Silicon)
- [Bun](https://bun.sh), [fswatch](https://github.com/emcrisostomo/fswatch), [uv](https://docs.astral.sh/uv/)

```bash
arch -arm64 brew install fswatch oven-sh/bun/bun
```

## Usage

```bash
uv run buddy-patcher --help
uv run buddy-patcher find --help
uv run buddy-patcher install --help
uv run buddy-patcher uninstall --help
```

## How it works

Claude Code generates companion traits deterministically from `hash(userId + SALT)` using a seeded PRNG. By replacing the 15-byte salt in the compiled binary, you change what the PRNG produces for your user ID. A LaunchAgent re-patches automatically after updates.
