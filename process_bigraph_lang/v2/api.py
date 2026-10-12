"""
The public Python API of v2: text in, checked documents out; documents in, text out.

- `compile_text` / `compile_file`: `.pbl` text -> parse (`cli-native generate`) -> check (`cli-native check`) ->
  a process-bigraph `{"schema", "state"}` document or a CompositeSpec mapping. An error-level finding stops the
  compile (`CompileError` carries every finding); warnings and infos come back on the result.
- `decompile`: a document or a CompositeSpec mapping -> canonical `.pbl` text plus sidecar assets.

The dataclass model (`model.py`) with its reader, writer and printer is the pivot these functions use, and it is
internal: there is no public path to a runnable document that skips the text and the checker, so a Python tool
that builds composites targets the DSL text, where the result is checked, reviewed and documented
(docs/v2/design.md, section 5.3).
"""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

import numpy as np

from process_bigraph_lang.v2.check import Diagnostic, check_file
from process_bigraph_lang.v2.interfaces import InterfaceRegistry
from process_bigraph_lang.v2.langium import read_langium
from process_bigraph_lang.v2.model import ExternalRef
from process_bigraph_lang.v2.printer import Printed, print_document
from process_bigraph_lang.v2.reader import read_composite_spec, read_document
from process_bigraph_lang.v2.writer import AssetLoader, write_composite_spec, write_document

Target = Literal["document", "spec"]

# a mapping with any of these top-level keys is a CompositeSpec, not a `{"schema", "state"}` document
SPEC_KEYS = frozenset({
    "name",
    "description",
    "tags",
    "requires",
    "parameters",
    "emitters",
    "default_n_steps",
    "visualizations",
    "analyses",
    "id",
    "module",
})


@dataclass
class Compiled:
    """What `compile_text` / `compile_file` return: the artifact and the findings that did not stop the compile."""

    document: dict[str, Any]
    diagnostics: list[Diagnostic] = field(default_factory=list)

    @property
    def warnings(self) -> list[Diagnostic]:
        return [d for d in self.diagnostics if d.severity == "warning"]


class CompileError(Exception):
    """The text did not pass the checker; `diagnostics` holds every finding, errors first."""

    def __init__(self, diagnostics: list[Diagnostic]):
        self.diagnostics = diagnostics
        errors = [d for d in diagnostics if d.severity == "error"]
        super().__init__("\n".join(str(d) for d in errors or diagnostics))


def compile_text(
    text: str,
    *,
    registry: InterfaceRegistry | None = None,
    manifests: list[Path] | None = None,
    to: Target = "document",
    assets: AssetLoader | None = None,
    strict: bool = False,
) -> Compiled:
    """Compile v2 text. `assets` resolves `file(...)` references; without it the text must be self-contained."""
    with tempfile.TemporaryDirectory() as tmp:
        source = Path(tmp) / "document.pbl"
        source.write_text(text, encoding="utf-8")
        return compile_file(source, registry=registry, manifests=manifests, to=to, assets=assets, strict=strict)


def compile_file(
    path: str | os.PathLike[str],
    *,
    registry: InterfaceRegistry | None = None,
    manifests: list[Path] | None = None,
    to: Target = "document",
    assets: AssetLoader | None = None,
    strict: bool = False,
) -> Compiled:
    """Compile a `.pbl` file; `file(...)` references resolve next to it unless `assets` is given."""
    source = Path(path).resolve()
    with tempfile.TemporaryDirectory() as tmp:
        manifest_paths = list(manifests or [])
        if registry is not None and registry.decls:
            manifest = Path(tmp) / "registry.manifest.json"
            manifest.write_text(json.dumps(registry.to_manifest(), default=str), encoding="utf-8")
            manifest_paths.append(manifest)
        diagnostics = check_file(source, manifest_paths)
    fatal = {"error", "warning"} if strict else {"error"}
    if any(d.severity in fatal for d in diagnostics):
        raise CompileError(diagnostics)
    model = read_langium(source, registry=registry)
    loader = assets if assets is not None else asset_loader(source.parent)
    document = write_composite_spec(model, assets=loader) if to == "spec" else write_document(model, assets=loader)
    return Compiled(document, diagnostics)


def decompile(
    mapping: dict[str, Any],
    *,
    name: str = "document",
    registry: InterfaceRegistry | None = None,
    kind: Literal["auto", "document", "spec"] = "auto",
) -> Printed:
    """Canonical `.pbl` text (and sidecar assets) for a document or a CompositeSpec mapping."""
    if kind == "auto":
        kind = "spec" if SPEC_KEYS & set(mapping) else "document"
    model = read_composite_spec(mapping) if kind == "spec" else read_document(mapping)
    return print_document(model, name=name, registry=registry)


def asset_loader(directory: str | os.PathLike[str]) -> AssetLoader:
    """An `assets` callback that reads the printer's sidecar files below `directory`."""
    base = Path(directory)

    def load(ref: ExternalRef) -> Any:
        return decode_asset(ref, (base / ref.path).read_bytes())

    return load


def decode_asset(ref: ExternalRef, content: bytes) -> Any:
    """A sidecar's value: text verbatim, arrays from `{dtype, shape, data}`, anything else as JSON."""
    if ref.kind == "text":
        return content.decode("utf-8")
    payload = json.loads(content)
    if ref.kind == "array":
        return np.asarray(payload["data"], dtype=payload["dtype"]).reshape(payload["shape"])
    return payload


__all__ = [
    "Compiled",
    "CompileError",
    "asset_loader",
    "compile_file",
    "compile_text",
    "decode_asset",
    "decompile",
]
