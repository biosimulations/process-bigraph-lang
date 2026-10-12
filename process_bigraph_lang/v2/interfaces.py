"""
Interface declarations as data: a minimal stage-A `describe` and the registry the normalizer resolves addresses in.

`describe_module` imports a Python module once (the publish-time step; authoring never imports) and turns every
step/process class it exposes into an `InterfaceDecl`: the address in portable `local:!module.Class` form, the
`config_schema`, and the ports obtained by calling `inputs()`/`outputs()` with the class standing in for `self`
(ports that depend on an instance are marked `dynamic_ports`). Types stay in bigraph-schema's own form. The
`InterfaceRegistry` holds declarations and reads and writes the JSON manifest (`pblang-manifest/0`), which the
TypeScript checker, printer and binder consume; `render_interfaces` has the CLI print the `.pblang` header file.
"""

from __future__ import annotations

import importlib
import inspect
import json
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from process_bigraph_lang.v2.describe_env import doc_of, is_edge_class, kind_of, ports_of
from process_bigraph_lang.v2.types import MISSING, Named, parse_type

MANIFEST_VERSION = "pblang-manifest/0"


@dataclass
class ConfigField:
    """One entry of a `config_schema`: the type in bigraph-schema form and its default, when it has one."""

    type: Any = None
    default: Any = MISSING


@dataclass
class InterfaceDecl:
    """A process/step interface as a manifest entry: address, config fields, ports (bigraph-schema forms)."""

    name: str
    kind: str  # process | step | adapter
    address: str | None = None
    module: str | None = None
    config: dict[str, ConfigField] = field(default_factory=dict)
    inputs: dict[str, Any] | None = None
    outputs: dict[str, Any] | None = None
    doc: str | None = None
    dynamic_ports: bool = False  # inputs()/outputs() could not be evaluated without an instance


def short_name(address: str) -> str:
    """`Name` of `local:!pkg.mod.Name`, `local:Name` or `Name`."""
    data = address.split(":", 1)[1] if ":" in address else address
    return data.lstrip("!").rsplit(".", 1)[-1]


def describe_module(module_name: str) -> list[InterfaceDecl]:
    """Declarations for the step/process classes a module defines or re-exports (classes of its own package only)."""
    module = importlib.import_module(module_name)
    is_package = hasattr(module, "__path__")
    decls: list[InterfaceDecl] = []
    for name, cls in inspect.getmembers(module, inspect.isclass):
        if name.startswith("_") or not is_edge_class(cls) or not _belongs_to(cls, module_name, is_package):
            continue
        decls.append(describe_class(cls, module_name, name))
    return decls


def describe_class(cls: type, module_name: str | None = None, name: str | None = None) -> InterfaceDecl:
    """The declaration of one step/process class."""
    module_name = module_name or cls.__module__
    name = name or cls.__name__
    inputs, outputs, dynamic = ports_of(cls)
    return InterfaceDecl(
        name=name,
        kind=kind_of(cls),
        address=f"local:!{module_name}.{name}",
        module=module_name,
        config=_config_fields(getattr(cls, "config_schema", None) or {}),
        inputs=inputs,
        outputs=outputs,
        doc=doc_of(cls),
        dynamic_ports=dynamic,
    )


@dataclass
class InterfaceRegistry:
    """Declarations by address: the manifest the CLI reads, and what the normalizer resolves edges in."""

    decls: list[InterfaceDecl] = field(default_factory=list)

    @classmethod
    def from_modules(cls, *module_names: str) -> InterfaceRegistry:
        registry = cls()
        for module_name in module_names:
            registry.decls.extend(describe_module(module_name))
        return registry

    @classmethod
    def from_manifest(cls, manifest: dict[str, Any]) -> InterfaceRegistry:
        return cls([_decl_from_manifest(entry) for entry in manifest.get("components", [])])

    def to_manifest(self) -> dict[str, Any]:
        return {"schema_version": MANIFEST_VERSION, "components": [_decl_to_manifest(d) for d in self.decls]}

    def lookup(self, address: str) -> InterfaceDecl | None:
        """By exact address; else by unique short name (`local:Name`, or a class re-exported from another module)."""
        wanted = address if ":" in address else f"local:{address}"
        if not wanted.startswith("local:"):
            return None
        exact = [d for d in self.decls if d.address == wanted]
        if exact:
            return exact[0]
        by_name = [d for d in self.decls if d.name == short_name(wanted)]
        return by_name[0] if len(by_name) == 1 else None

    def write_manifest(self, path: Path) -> Path:
        path.write_text(json.dumps(self.to_manifest(), indent=2, default=str) + "\n", encoding="utf-8")
        return path


def render_interfaces(decls: list[InterfaceDecl], module_name: str) -> str:
    """The `.pblang` header file of a module's declarations, as the CLI prints it."""
    from process_bigraph_lang.v2.langium import run_cli

    with tempfile.TemporaryDirectory() as tmp:
        manifest = Path(tmp) / "manifest.json"
        entries = [_decl_to_manifest(d) for d in decls]
        for entry in entries:
            entry["module"] = module_name
        manifest.write_text(json.dumps({"schema_version": MANIFEST_VERSION, "components": entries}, default=str))
        return run_cli("headers", str(manifest)).stdout


# --- describe ----------------------------------------------------------------------------------------------------


def _belongs_to(cls: type, module_name: str, is_package: bool) -> bool:
    """Defined in the module itself, or (for a package) re-exported from one of its submodules."""
    return cls.__module__ == module_name or (is_package and cls.__module__.startswith(module_name + "."))


def _config_fields(schema: Any) -> dict[str, ConfigField]:
    if not isinstance(schema, dict):
        return {}
    fields: dict[str, ConfigField] = {}
    for key, spec in schema.items():
        default: Any = MISSING
        try:
            expr = parse_type(spec)
            if isinstance(expr, Named):
                default = expr.default
        except (TypeError, ValueError):
            pass
        fields[str(key)] = ConfigField(spec if isinstance(spec, (str, dict)) else None, default)
    return fields


# --- manifest ----------------------------------------------------------------------------------------------------


def _decl_to_manifest(decl: InterfaceDecl) -> dict[str, Any]:
    entry: dict[str, Any] = {
        "name": decl.name,
        "kind": decl.kind,
        "address": decl.address,
        "module": decl.module,
        "config": {
            k: {"type": f.type, **({"default": f.default} if f.default is not MISSING else {})}
            for k, f in decl.config.items()
        },
        "inputs": dict(decl.inputs) if decl.inputs is not None else None,
        "outputs": dict(decl.outputs) if decl.outputs is not None else None,
        "dynamic_ports": decl.dynamic_ports,
    }
    if decl.doc:
        entry["doc"] = decl.doc
    return entry


def _decl_from_manifest(entry: dict[str, Any]) -> InterfaceDecl:
    config = {k: ConfigField(f.get("type"), f.get("default", MISSING)) for k, f in (entry.get("config") or {}).items()}
    return InterfaceDecl(
        name=entry["name"],
        kind=entry.get("kind", "process"),
        address=entry["address"] if entry.get("address") else None,
        module=entry.get("module"),
        config=config,
        inputs=_ports_from_manifest(entry.get("inputs")),
        outputs=_ports_from_manifest(entry.get("outputs")),
        doc=entry.get("doc"),
        dynamic_ports=bool(entry.get("dynamic_ports", False)),
    )


def _ports_from_manifest(ports: Any) -> dict[str, Any] | None:
    if ports is None:
        return None
    return {str(k): v for k, v in ports.items()}
