"""
Static checks of a composite, run by the DSL CLI's `check` command (the checker lives in TypeScript,
`dsl/src/language/v2/check.ts`, so the editor, the browser and the CLI share one implementation).

`check_file` runs `cli-native check --json` on a `.pblang` file with header manifests; `check_text` does the same
for text. Both return the findings of the `pblang-diagnostics/1` envelope as `Diagnostic`s.
"""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from process_bigraph_lang.v2.interfaces import InterfaceRegistry
from process_bigraph_lang.v2.langium import run_cli


@dataclass
class Diagnostic:
    code: str
    slug: str
    severity: str  # error | warning | info | hint
    path: str  # document path, slash-joined (as `fill_sites` spells it)
    message: str
    line: int | None = None

    def __str__(self) -> str:
        return f"{self.severity:7} {self.code} {self.slug:24} {self.path}: {self.message}"


def check_text(
    text: str, manifests: list[Path] | None = None, registry: InterfaceRegistry | None = None
) -> list[Diagnostic]:
    """Check v2 text against header manifests and/or a registry (written as a manifest)."""
    with tempfile.TemporaryDirectory() as tmp:
        source = Path(tmp) / "document.pblang"
        source.write_text(text, encoding="utf-8")
        return check_file(source, [*(manifests or []), *registry_manifests(registry, Path(tmp))])


def check_file(path: str | os.PathLike[str], manifests: list[Path] | None = None) -> list[Diagnostic]:
    """Check a `.pblang` file against header manifests through the CLI."""
    args = ["check", str(Path(path).resolve()), "--json"]
    if manifests:
        args += ["--interfaces", *[str(Path(m).resolve()) for m in manifests]]
    result = run_cli(*args, check=False)
    if not result.stdout.strip():
        raise RuntimeError(f"Langium CLI failed on {path}: {result.stderr.strip()}")
    envelope: dict[str, Any] = json.loads(result.stdout)
    return [
        Diagnostic(
            d["code"],
            d["slug"],
            d["severity"],
            d["path"],
            d["message"],
            d.get("range", {}).get("start", {}).get("line"),
        )
        for d in envelope.get("diagnostics", [])
    ]


def registry_manifests(registry: InterfaceRegistry | None, directory: Path) -> list[Path]:
    """A registry written as a manifest file in `directory` (none when the registry is empty)."""
    if registry is None or not registry.decls:
        return []
    manifest = directory / "registry.manifest.json"
    manifest.write_text(json.dumps(registry.to_manifest(), default=str), encoding="utf-8")
    return [manifest]
