"""
Static checks of a composite, run by the DSL CLI's `check` command (the checker lives in TypeScript,
`dsl/src/language/v2/check.ts`, so the editor, the browser and the CLI share one implementation).

`check_document(doc, registry)` prints the model as `.pbl` text, writes the registry as a header manifest and
runs `cli-native check --json`; `check_file` does the same for a `.pbl` file and manifest files. Both return the
findings of the `pblang-diagnostics/1` envelope as `Diagnostic`s.
"""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from process_bigraph_lang.v2.interfaces import InterfaceRegistry
from process_bigraph_lang.v2.langium import langium_cli
from process_bigraph_lang.v2.model import Document
from process_bigraph_lang.v2.printer import print_document


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


def check_document(doc: Document, registry: InterfaceRegistry | None = None) -> list[Diagnostic]:
    """Check a model (printed to text) against a registry (written as a manifest)."""
    with tempfile.TemporaryDirectory() as tmp:
        source = Path(tmp) / "document.pbl"
        source.write_text(print_document(doc, name="document", registry=registry).text, encoding="utf-8")
        manifests: list[Path] = []
        if registry is not None and registry.decls:
            manifest = Path(tmp) / "manifest.json"
            manifest.write_text(json.dumps(registry.to_manifest(), default=str), encoding="utf-8")
            manifests.append(manifest)
        return check_file(source, manifests)


def check_file(path: str | os.PathLike[str], manifests: list[Path] | None = None) -> list[Diagnostic]:
    """Check a `.pbl` file against header manifests through the CLI."""
    command = langium_cli()
    if command is None:
        raise RuntimeError("no Langium CLI: build dsl/ (npm run build) or install the cli-native binary")
    args = [*command, "check", str(Path(path).resolve()), "--json"]
    if manifests:
        args += ["--interfaces", *[str(Path(m).resolve()) for m in manifests]]
    result = subprocess.run(args, capture_output=True, text=True, check=False)
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
