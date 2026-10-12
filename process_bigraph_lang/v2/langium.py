"""
The DSL CLI from Python: `cli-native` (the same binary v1 uses, built once by Deno at wheel-build time) or
`node dsl/bin/cli.js` in a development checkout. Everything the v2 language does, parsing, checking, compiling,
decompiling and rendering headers, lives in TypeScript (`dsl/src/language/v2/`); Python only calls it.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent


def langium_cli() -> list[str] | None:
    """The command that runs the DSL CLI, or None when neither the native binary nor a built checkout exists."""
    for candidate in (_ROOT / "bin").glob("cli-native*"):
        return [str(candidate)]
    script = _ROOT.parent / "dsl" / "bin" / "cli.js"
    if script.exists() and (_ROOT.parent / "dsl" / "out").exists():
        return ["node", str(script)]
    return None


def run_cli(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    """Run a CLI command; raise with its stderr when it fails (unless `check=False`)."""
    command = langium_cli()
    if command is None:
        raise RuntimeError("no Langium CLI: build dsl/ (npm run build) or install the cli-native binary")
    result = subprocess.run([*command, *args], capture_output=True, text=True, encoding="utf-8", check=False)
    if check and result.returncode != 0:
        raise RuntimeError(
            f"Langium CLI failed ({' '.join(args[:2])}): {result.stderr.strip() or result.stdout.strip()}"
        )
    return result


__all__ = ["langium_cli", "run_cli"]
