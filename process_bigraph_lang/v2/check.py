"""
Static checks of a composite against interface declarations, without importing any process code.

Given a `Document` and an `InterfaceRegistry` (interface files or manifests), `check_document` reports: ports
that the interface does not declare, config keys it does not declare or requires, wires that name no declared
store (process-bigraph would create one silently), wires whose target's declared type differs from the port's,
paths that escape the root, an `interval` on a step, components the registry does not know (their ports and
config go unchecked) and interfaces whose ports depend on an instance (declared by hand later). This is the
S2–S4 slice of the diagnostics model in `docs/v2/design.md`; codes follow `docs/v2/registry-and-authoring.md`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from process_bigraph_lang.v2.interfaces import InterfaceRegistry
from process_bigraph_lang.v2.model import Address, Composite, Document, Edge, InterfaceDecl, Node, Site, Store
from process_bigraph_lang.v2.normalize import _canon_type
from process_bigraph_lang.v2.paths import Path, Wire
from process_bigraph_lang.v2.types import Named, Struct, TypeExpr, to_bigraph
from process_bigraph_lang.v2.values import MISSING


@dataclass
class Diagnostic:
    code: str
    slug: str
    severity: str  # error | warning | info
    path: str  # document path, slash-joined (as `fill_sites` spells it)
    message: str

    def __str__(self) -> str:
        return f"{self.severity:7} {self.code} {self.slug:24} {self.path}: {self.message}"


def check_document(doc: Document, registry: InterfaceRegistry | None = None) -> list[Diagnostic]:
    checker = _Checker(registry)
    checker.scope(doc.root, ())
    order = {"error": 0, "warning": 1, "info": 2}
    return sorted(checker.diagnostics, key=lambda d: (order[d.severity], d.path, d.code))


_Target = tuple[tuple[str | int, ...], TypeExpr | None, bool]  # absolute path, declared type, declared?


class _Checker:
    def __init__(self, registry: InterfaceRegistry | None) -> None:
        self.registry = registry
        self.diagnostics: list[Diagnostic] = []
        self.index: dict[tuple[str | int, ...], Store | Node | Edge] = {}

    def report(self, code: str, slug: str, severity: str, path: tuple[str | int, ...], message: str) -> None:
        self.diagnostics.append(Diagnostic(code, slug, severity, "/".join(str(p) for p in path), message))

    # --- scopes ------------------------------------------------------------------------------------------------

    def scope(self, composite: Composite, base: tuple[str | int, ...]) -> None:
        """A composite body: wires inside it are relative to it, so each nested composite is its own scope."""
        saved = self.index
        self.index = {}
        self.index_composite(composite, ())
        for path, element in list(self.index.items()):
            if isinstance(element, Edge):
                self.edge(element, path)
                if element.inner is not None:
                    self.scope(element.inner, (*base, *path))
        self.index = saved

    def index_composite(self, composite: Composite, path: tuple[str | int, ...]) -> None:
        for key, element in composite.children.items():
            here = (*path, key)
            self.index[here] = element
            if isinstance(element, Node):
                self.index_composite(Composite(element.children), here)

    # --- edges -------------------------------------------------------------------------------------------------

    def edge(self, edge: Edge, path: tuple[str | int, ...]) -> None:
        decl = self.declaration(edge, path)
        if edge.kind == "step" and edge.interval is not None:
            self.report("T130", "interval-on-step", "error", path, "a step has no interval; only processes do")
        if decl is not None:
            self.config(edge, decl, path)
        for label, wires in (("inputs", edge.inputs), ("outputs", edge.outputs)):
            declared = getattr(decl, label) if decl is not None else None
            if edge.ports is not None and getattr(edge.ports, label) is not None:
                declared = getattr(edge.ports, label)  # the node's own `_inputs`/`_outputs` win
            for port, wire in wires.items():
                port_path = (*path, label, port)
                port_type = declared.get(port) if declared is not None else None
                if declared is not None and port not in declared and not (decl is not None and decl.dynamic_ports):
                    known = ", ".join(sorted(declared)) or "none"
                    self.report(
                        "S021",
                        "unknown-port",
                        "error",
                        port_path,
                        f"{self.name(decl, edge)} has no {label[:-1]} port '{port}' (declared: {known})",
                    )
                self.wire(wire, port_type, path[:-1], port_path)

    def declaration(self, edge: Edge, path: tuple[str | int, ...]) -> InterfaceDecl | None:
        if isinstance(edge.address, Site):
            self.report(
                "I300",
                "open-address",
                "info",
                path,
                "the address is an open site; ports are checked against its sort later",
            )
            return None
        if self.registry is None or not isinstance(edge.address, Address):
            return None
        if edge.address.is_composite:
            return None
        decl = self.registry.lookup(edge.address)
        if decl is None:
            self.report(
                "S020",
                "unknown-component",
                "info",
                path,
                f"'{edge.address}' is not in the registry; its ports and config are not checked",
            )
            return None
        if decl.dynamic_ports:
            self.report(
                "I210",
                "dynamic-ports",
                "info",
                path,
                f"{decl.name}: ports depend on an instance; only the declared ones are checked",
            )
        return decl

    def config(self, edge: Edge, decl: InterfaceDecl, path: tuple[str | int, ...]) -> None:
        if not decl.config:
            return
        for key, field in decl.config.items():
            if field.default is MISSING and key not in edge.config:
                self.report(
                    "T121", "config-missing", "error", (*path, "config", key), f"{decl.name} requires config '{key}'"
                )
        for key in edge.config:
            if key not in decl.config:
                known = ", ".join(decl.config)
                self.report(
                    "S022",
                    "config-unknown-key",
                    "warning",
                    (*path, "config", key),
                    f"{decl.name} has no config '{key}' (declared: {known})",
                )

    def name(self, decl: InterfaceDecl | None, edge: Edge) -> str:
        return decl.name if decl is not None else f"'{edge.address}'"

    # --- wires -------------------------------------------------------------------------------------------------

    def wire(
        self, wire: Wire, port_type: TypeExpr | None, parent: tuple[str | int, ...], port_path: tuple[str | int, ...]
    ) -> None:
        if isinstance(wire, dict):
            element = _map_value_type(port_type)
            for sub_port, sub_wire in wire.items():
                self.wire(sub_wire, element, parent, (*port_path, sub_port))
            return
        target = self.resolve(wire, parent, port_path)
        if target is None:
            return
        absolute, store_type, declared = target
        if not declared:
            self.report(
                "W211",
                "store-not-declared",
                "warning",
                port_path,
                f"wire names no declared store '{'/'.join(map(str, absolute))}'; process-bigraph would create it from the port",
            )
            return
        if store_type is None:
            self.report(
                "I220",
                "store-untyped",
                "info",
                port_path,
                f"store '{'/'.join(map(str, absolute))}' has no declared type; the port type cannot be checked",
            )
            return
        if port_type is not None and _canon(port_type) != _canon(store_type):
            self.report(
                "W200",
                "wire-type-mismatch",
                "warning",
                port_path,
                f"port type '{_text(port_type)}' but store '{'/'.join(map(str, absolute))}' is declared '{_text(store_type)}'",
            )

    def resolve(self, wire: Path, parent: tuple[str | int, ...], port_path: tuple[str | int, ...]) -> _Target | None:
        absolute: list[str | int] = list(parent)
        for step in wire.steps:
            if step == "..":
                if not absolute:
                    self.report(
                        "E110",
                        "path-escapes-root",
                        "error",
                        port_path,
                        f"'{wire.to_text()}' goes above the composite root",
                    )
                    return None
                absolute.pop()
            elif step == "*":
                return None
            else:
                absolute.append(step)
        # the longest indexed prefix, then descend into the store's value / type
        for cut in range(len(absolute), 0, -1):
            prefix = tuple(absolute[:cut])
            element = self.index.get(prefix)
            if element is None:
                continue
            rest = absolute[cut:]
            if isinstance(element, Edge):
                return None
            if isinstance(element, Node):
                return (tuple(absolute), element.type, not rest) if not rest else (tuple(absolute), None, False)
            return (tuple(absolute), *_descend(element, rest))
        return tuple(absolute), None, False


def _descend(store: Store, rest: list[str | int]) -> tuple[TypeExpr | None, bool]:
    """Follow the remaining path into a store's value (dict keys) and type (map values, array elements)."""
    store_type: TypeExpr | None = store.type if store.site is None else store.site.sort
    value: Any = store.value
    for step in rest:
        if isinstance(step, int):
            store_type = _array_data_type(store_type)
            value = MISSING
            continue
        if isinstance(value, dict):
            if step not in value:
                return None, False
            value = value[step]
        elif value is not MISSING:
            return None, False
        store_type = (
            _map_value_type(store_type) if not isinstance(store_type, Struct) else store_type.fields.get(str(step))
        )
    return store_type, True


def _map_value_type(expr: TypeExpr | None) -> TypeExpr | None:
    if isinstance(expr, Named) and expr.name == "map" and expr.args:
        return expr.args[-1]
    return None


def _array_data_type(expr: TypeExpr | None) -> TypeExpr | None:
    if isinstance(expr, Named) and expr.name in ("array", "list") and expr.args:
        return next((a for a in reversed(expr.args) if isinstance(a, (Named, Struct))), None)
    if isinstance(expr, Named) and expr.name not in ("array", "list") and len(expr.args) == 2:
        return expr.args[1]  # positive_array<float>[n, m]
    return None


def _canon(expr: TypeExpr) -> Any:
    return _canon_type(to_bigraph(expr), None)


def _text(expr: TypeExpr) -> str:
    from process_bigraph_lang.v2.types import to_surface

    return to_surface(expr)
