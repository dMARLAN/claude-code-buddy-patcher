# buddy-patcher

Choose your Claude Code `/buddy` companion.

<img width="290" height="531" alt="image" src="https://github.com/user-attachments/assets/7dd26d1f-892d-4140-8313-54b26f7abf26" />

## Requirements

- macOS or Linux
- [Bun](https://bun.sh), [uv](https://docs.astral.sh/uv/), a C compiler (`cc`)

## Usage

```bash
uv run buddy-patcher --help
uv run buddy-patcher build
```

## How it works

Claude Code generates companion traits deterministically from `hash(userId + SALT)` using a seeded PRNG. By replacing the 15-byte salt in the compiled binary, you change what the PRNG produces for your user ID. A LaunchAgent (macOS) or systemd user service (Linux) re-patches automatically after updates.
