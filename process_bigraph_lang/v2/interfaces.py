"""
Interface declarations as data: a minimal stage-A `describe` and the registry the printer resolves addresses in.

`describe_module` imports a Python module once (the publish-time step; authoring never imports) and turns every
step/process class it exposes into an `InterfaceDecl`: the address in portable `local:!module.Class` form, the
`config_schema`, and the ports obtained by calling `inputs()`/`outputs()` with the class standing in for `self`
(ports that depend on an instance are marked `dynamic_ports`). `InterfaceRegistry` holds declarations, reads and
writes the JSON manifest, and resolves an edge's address to a declaration.
"""

from __future__ import annotations

import importlib
import inspect
from dataclasses import dataclass, field
from typing import Any

from process_bigraph_lang.v2.model import Address, ConfigField, InterfaceDecl
from process_bigraph_lang.v2.types import Named, TypeExpr, parse_type, to_bigraph
from process_bigraph_lang.v2.values import MISSING

MANIFEST_VERSION = "pblang-manifest/0"


def describe_module(module_name: str) -> list[InterfaceDecl]:
    """Declarations for the step/process classes a module defines or re-exports (classes of its own package only)."""
    module = importlib.import_module(module_name)
    is_package = hasattr(module, "__path__")
    decls: list[InterfaceDecl] = []
    for name, cls in inspect.getmembers(module, inspect.isclass):
        if not _is_edge_class(cls) or not _belongs_to(cls, module_name, is_package):
            continue
        decls.append(describe_class(cls, module_name, name))
    return decls


def describe_class(cls: type, module_name: str | None = None, name: str | None = None) -> InterfaceDecl:
    """The declaration of one step/process class."""
    module_name = module_name or cls.__module__
    name = name or cls.__name__
    inputs, outputs, dynamic = _ports(cls)
    return InterfaceDecl(
        name=name,
        kind=_kind(cls),
        address=Address("local", f"!{module_name}.{name}"),
        module=module_name,
        config=_config_fields(getattr(cls, "config_schema", None) or {}),
        inputs=inputs,
        outputs=outputs,
        doc=_doc(cls),
        dynamic_ports=dynamic,
    )


@dataclass
class InterfaceRegistry:
    """Declarations the printer resolves edge addresses in (an `import` is printed instead of an inline declaration)."""

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

    def lookup(self, address: Address) -> InterfaceDecl | None:
        """By exact address; else by unique short name (`local:Name`, or a class re-exported from another module)."""
        if address.protocol != "local":
            return None
        wanted = str(address)
        exact = [d for d in self.decls if d.address is not None and str(d.address) == wanted]
        if exact:
            return exact[0]
        by_name = [d for d in self.decls if d.name == address.short_name]
        return by_name[0] if len(by_name) == 1 else None


# --- describe ----------------------------------------------------------------------------------------------------


def _is_edge_class(cls: type) -> bool:
    return any(base.__name__ == "Edge" for base in cls.__mro__)


def _belongs_to(cls: type, module_name: str, is_package: bool) -> bool:
    """Defined in the module itself, or (for a package) re-exported from one of its submodules."""
    return cls.__module__ == module_name or (is_package and cls.__module__.startswith(module_name + "."))


def _kind(cls: type) -> str:
    names = [base.__name__ for base in cls.__mro__]
    if "Process" in names:
        return "process"
    return "step"


def _ports(cls: type) -> tuple[dict[str, TypeExpr] | None, dict[str, TypeExpr] | None, bool]:
    faces: list[dict[str, TypeExpr] | None] = []
    dynamic = False
    for method_name in ("inputs", "outputs"):
        method = getattr(cls, method_name, None)
        if method is None:
            faces.append(None)
            continue
        try:
            ports = method(cls)  # the class stands in for `self`: works for literal port dicts
        except Exception:  # noqa: BLE001 - ports depend on an instance (self.config, children, ...)
            faces.append(None)
            dynamic = True
            continue
        faces.append({str(k): parse_type(v) for k, v in ports.items()} if isinstance(ports, dict) else None)
    return faces[0], faces[1], dynamic


def _config_fields(schema: Any) -> dict[str, ConfigField]:
    if not isinstance(schema, dict):
        return {}
    fields: dict[str, ConfigField] = {}
    for key, spec in schema.items():
        try:
            expr: TypeExpr | None = parse_type(spec)
        except TypeError:
            expr = None
        default = expr.default if isinstance(expr, Named) else MISSING
        fields[str(key)] = ConfigField(expr, default)
    return fields


def _doc(cls: type) -> str | None:
    text = cls.__dict__.get("__doc__")
    if not text:
        return None
    first = inspect.cleandoc(text).split("\n\n", 1)[0].strip()
    return first or None


# --- manifest ----------------------------------------------------------------------------------------------------


def _decl_to_manifest(decl: InterfaceDecl) -> dict[str, Any]:
    entry: dict[str, Any] = {
        "name": decl.name,
        "kind": decl.kind,
        "address": str(decl.address) if decl.address is not None else None,
        "module": decl.module,
        "config": {
            k: {
                "type": to_bigraph(f.type) if f.type is not None else None,
                **({"default": f.default} if f.default is not MISSING else {}),
            }
            for k, f in decl.config.items()
        },
        "inputs": {k: to_bigraph(v) for k, v in decl.inputs.items()} if decl.inputs is not None else None,
        "outputs": {k: to_bigraph(v) for k, v in decl.outputs.items()} if decl.outputs is not None else None,
        "dynamic_ports": decl.dynamic_ports,
    }
    if decl.doc:
        entry["doc"] = decl.doc
    return entry


def _decl_from_manifest(entry: dict[str, Any]) -> InterfaceDecl:
    config = {
        k: ConfigField(parse_type(f["type"]) if f.get("type") is not None else None, f.get("default", MISSING))
        for k, f in (entry.get("config") or {}).items()
    }
    return InterfaceDecl(
        name=entry["name"],
        kind=entry.get("kind", "process"),
        address=Address.from_any(entry["address"]) if entry.get("address") else None,
        module=entry.get("module"),
        config=config,
        inputs=_ports_from_manifest(entry.get("inputs")),
        outputs=_ports_from_manifest(entry.get("outputs")),
        doc=entry.get("doc"),
        dynamic_ports=bool(entry.get("dynamic_ports", False)),
    )


def _ports_from_manifest(ports: Any) -> dict[str, TypeExpr] | None:
    if ports is None:
        return None
    return {str(k): parse_type(v) for k, v in ports.items()}
