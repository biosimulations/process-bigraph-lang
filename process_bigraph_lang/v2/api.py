"""
The public Python API of v2: text in, checked documents out; documents in, text out. All of it runs in the DSL
CLI (`cli-native`, TypeScript): parsing, checking, compiling and decompiling. There is no Python model of a
composite, so a Python tool that builds composites targets the DSL text, where the result is checked, reviewed
and documented (docs/v2/design.md, section 5.3).

- `compile_text` / `compile_file`: `.pbl` text -> parse -> check -> a process-bigraph `{"schema", "state"}`
  document or a CompositeSpec mapping. An error-level finding stops the compile (`CompileError` carries every
  finding); warnings and infos come back on the result.
- `decompile`: a document or a CompositeSpec mapping -> canonical `.pbl` text plus sidecar assets.

Documents cross the CLI boundary as JSON in `bigraph_schema.json_codec`'s encoding (numpy arrays tagged), with
tuples tagged as `{"__tuple__": true, "data": [...]}` so that they survive too.
"""

from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

from bigraph_schema import json_codec  # type: ignore[import-untyped]

from process_bigraph_lang.v2.check import Diagnostic, check_file, registry_manifests
from process_bigraph_lang.v2.interfaces import InterfaceRegistry
from process_bigraph_lang.v2.langium import run_cli

Target = Literal["document", "spec"]


@dataclass
class Compiled:
    """What `compile_text` / `compile_file` return: the artifact and the findings that did not stop the compile."""

    document: dict[str, Any]
    diagnostics: list[Diagnostic] = field(default_factory=list)

    @property
    def warnings(self) -> list[Diagnostic]:
        return [d for d in self.diagnostics if d.severity == "warning"]


@dataclass
class Printed:
    """What `decompile` returns: the `.pbl` text and its sidecar assets (`<name>.assets/...`), by path."""

    text: str
    assets: dict[str, bytes] = field(default_factory=dict)


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
    strict: bool = False,
    force: bool = False,
    assets: dict[str, bytes] | None = None,
) -> Compiled:
    """Compile v2 text. `assets` holds the sidecar files `file(...)` references name, by path."""
    with tempfile.TemporaryDirectory() as tmp:
        source = Path(tmp) / "document.pbl"
        source.write_text(text, encoding="utf-8")
        for name, content in (assets or {}).items():
            target = Path(tmp) / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
        return compile_file(source, registry=registry, manifests=manifests, to=to, strict=strict, force=force)


def compile_file(
    path: str | os.PathLike[str],
    *,
    registry: InterfaceRegistry | None = None,
    manifests: list[Path] | None = None,
    to: Target = "document",
    strict: bool = False,
    force: bool = False,
) -> Compiled:
    """
    Compile a `.pbl` file; `file(...)` references resolve next to it. `force` compiles despite the checker's
    errors (parse errors still stop it): the escape for documents that rely on defaults the checker flags.
    """
    source = Path(path).resolve()
    with tempfile.TemporaryDirectory() as tmp:
        manifest_paths = [*(manifests or []), *registry_manifests(registry, Path(tmp))]
        diagnostics = check_file(source, manifest_paths)
        fatal = set() if force else {"error", "warning"} if strict else {"error"}
        if any(d.severity in fatal for d in diagnostics) or any(d.code == "P001" for d in diagnostics):
            raise CompileError(diagnostics)
        out = Path(tmp) / ("compiled.yaml" if to == "spec" else "compiled.json")
        args = ["compile", str(source), "--to", to, "--out", str(out), *(["--force"] if force else [])]
        if manifest_paths:
            args += ["--interfaces", *[str(Path(m).resolve()) for m in manifest_paths]]
        run_cli(*args)
        text = out.read_text(encoding="utf-8")
    if to == "spec":
        import yaml

        return Compiled(yaml.safe_load(text), diagnostics)
    return Compiled(loads(text), diagnostics)


def decompile(
    mapping: dict[str, Any],
    *,
    name: str = "document",
    registry: InterfaceRegistry | None = None,
    manifests: list[Path] | None = None,
) -> Printed:
    """Canonical `.pbl` text (and sidecar assets) for a document or a CompositeSpec mapping (told apart by keys)."""
    with tempfile.TemporaryDirectory() as tmp:
        source = Path(tmp) / f"{name}.json"
        source.write_text(dumps(mapping), encoding="utf-8")
        out = Path(tmp) / f"{name}.pbl"
        args = ["decompile", str(source), "--name", name, "--out", str(out)]
        manifest_paths = [*(manifests or []), *registry_manifests(registry, Path(tmp))]
        if manifest_paths:
            args += ["--interfaces", *[str(Path(m).resolve()) for m in manifest_paths]]
        run_cli(*args)
        printed = Printed(out.read_text(encoding="utf-8"))
        assets_dir = Path(tmp) / f"{name}.assets"
        if assets_dir.is_dir():
            for asset in sorted(assets_dir.iterdir()):
                printed.assets[f"{name}.assets/{asset.name}"] = asset.read_bytes()
        return printed


# --- the JSON that crosses the CLI boundary ----------------------------------------------------------------------


def dumps(document: Any) -> str:
    """`bigraph_schema.json_codec` encoding, plus tuples tagged so that they come back as tuples."""
    return str(json_codec.dumps(_tag_tuples(document)))


def loads(text: str) -> Any:
    return _untag_tuples(json_codec.loads(text))


def _tag_tuples(value: Any) -> Any:
    if isinstance(value, tuple):
        return {"__tuple__": True, "data": [_tag_tuples(v) for v in value]}
    if isinstance(value, dict):
        return {k: _tag_tuples(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_tag_tuples(v) for v in value]
    return value


def _untag_tuples(value: Any) -> Any:
    if isinstance(value, dict):
        if value.get("__tuple__") is True and isinstance(value.get("data"), list):
            return tuple(_untag_tuples(v) for v in value["data"])
        return {k: _untag_tuples(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_untag_tuples(v) for v in value]
    return value


def write_json(document: Any, path: str | os.PathLike[str]) -> None:
    Path(path).write_text(dumps(document) + "\n", encoding="utf-8")


def read_json(path: str | os.PathLike[str]) -> Any:
    return loads(Path(path).read_text(encoding="utf-8"))


__all__ = [
    "CompileError",
    "Compiled",
    "Printed",
    "compile_file",
    "compile_text",
    "decompile",
    "dumps",
    "loads",
    "read_json",
    "write_json",
]
