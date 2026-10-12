"""
Static checks of a composite against interface declarations, without importing any process code.

Given a `Document` and an `InterfaceRegistry` (interface files or manifests), `check_document` reports: ports
that the interface does not declare, config keys it does not declare or requires, wires that name no declared
store (process-bigraph would create one silently), wires whose target's declared type differs from the port's,
paths that escape the root, an `interval` on a step, components the registry does not know (their ports and
config go unchecked) and interfaces whose ports depend on an instance (declared by hand later). It also analyses
the writers of each store: additive writers that superpose (for review), an overwriting writer next to another
writer (order-dependent), and a step publishing an array additively (usually meant `overwrite`). This is the
S2–S4 slice of the diagnostics model in `docs/v2/design.md`; codes follow `docs/v2/registry-and-authoring.md`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from process_bigraph_lang.v2.interfaces import InterfaceRegistry
from process_bigraph_lang.v2.model import Address, Composite, Document, Edge, InterfaceDecl, Node, Site, Store
from process_bigraph_lang.v2.normalize import _canon_type
from process_bigraph_lang.v2.paths import Path, Wire
from process_bigraph_lang.v2.types import Group, Named, Struct, TypeExpr, to_bigraph
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


@dataclass
class _Writer:
    port_path: tuple[str | int, ...]
    kind: str  # process | step
    port_type: TypeExpr | None
    store_type: TypeExpr | None


class _Checker:
    def __init__(self, registry: InterfaceRegistry | None) -> None:
        self.registry = registry
        self.diagnostics: list[Diagnostic] = []
        self.index: dict[tuple[str | int, ...], Store | Node | Edge] = {}
        self.writers: dict[tuple[str | int, ...], list[_Writer]] = {}

    def report(self, code: str, slug: str, severity: str, path: tuple[str | int, ...], message: str) -> None:
        self.diagnostics.append(Diagnostic(code, slug, severity, "/".join(str(p) for p in path), message))

    # --- scopes ------------------------------------------------------------------------------------------------

    def scope(self, composite: Composite, base: tuple[str | int, ...]) -> None:
        """A composite body: wires inside it are relative to it, so each nested composite is its own scope."""
        saved, saved_writers = self.index, self.writers
        self.index, self.writers = {}, {}
        self.index_composite(composite, ())
        for path, element in list(self.index.items()):
            if isinstance(element, Edge):
                self.edge(element, path)
        self.writer_analysis()
        for path, element in list(self.index.items()):
            if isinstance(element, Edge) and element.inner is not None:
                self.scope(element.inner, (*base, *path))
        self.index, self.writers = saved, saved_writers

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
                self.wire(wire, port_type, path[:-1], port_path, writer=edge.kind if label == "outputs" else None)

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
        self,
        wire: Wire,
        port_type: TypeExpr | None,
        parent: tuple[str | int, ...],
        port_path: tuple[str | int, ...],
        writer: str | None = None,
    ) -> None:
        """Check one wire; `writer` is the edge kind when this is an output wire (it then writes the store)."""
        if isinstance(wire, dict):
            element = _map_value_type(port_type)
            for sub_port, sub_wire in wire.items():
                self.wire(sub_wire, element, parent, (*port_path, sub_port), writer)
            return
        target = self.resolve(wire, parent, port_path)
        if target is None:
            return
        absolute, store_type, declared = target
        if writer is not None:
            self.writers.setdefault(absolute, []).append(_Writer(port_path, writer, port_type, store_type))
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

    # --- writers -----------------------------------------------------------------------------------------------

    def writer_analysis(self) -> None:
        """
        How the processes that write one store combine. Additive writers superpose (process-bigraph's default
        model, reported for review); an overwriting writer next to any other writer is order-dependent; a step
        publishing an array-typed value with accumulate semantics usually meant `overwrite`.
        """
        for store, writers in sorted(self.writers.items(), key=lambda kv: tuple(map(str, kv[0]))):
            store_text = "/".join(map(str, store))
            store_overwrite = any(_semantics(w.store_type) == "overwrite" for w in writers if w.store_type is not None)
            kinds = {w.port_path: ("overwrite" if store_overwrite else _semantics(w.port_type)) for w in writers}
            for w in writers:
                if (
                    w.kind == "step"
                    and kinds[w.port_path] == "accumulate"
                    and w.port_type is not None
                    and _contains_array(w.port_type)
                ):
                    self.report(
                        "W223",
                        "step-array-accumulates",
                        "warning",
                        w.port_path,
                        f"a step publishes array-typed '{_text(w.port_type)}' into '{store_text}' with accumulate semantics; "
                        "a step usually computes a whole value: did you mean overwrite<...>?",
                    )
            if len(writers) < 2:
                continue
            names = ", ".join("/".join(map(str, w.port_path)) for w in writers)
            if any(k == "overwrite" for k in kinds.values()):
                self.report(
                    "W221",
                    "overwrite-conflict",
                    "warning",
                    store,
                    f"'{store_text}' is overwritten by one writer and also written by another ({names}): "
                    "the last update applied wins, so the result depends on scheduling order",
                )
            elif all(k == "accumulate" for k in kinds.values()):
                self.report(
                    "W220",
                    "additive-writers",
                    "info",
                    store,
                    f"'{store_text}' is written additively by {len(writers)} processes ({names}): "
                    "their contributions are summed each tick (simultaneous splitting)",
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


def _semantics(expr: TypeExpr | None) -> str:
    """`overwrite` when the written value replaces the store (also per key for `map<overwrite<T>>`), else `accumulate`."""
    if expr is None:
        return "unknown"
    if isinstance(expr, Named):
        if expr.name == "overwrite":
            return "overwrite"
        if expr.name in ("map", "list", "maybe") and expr.args:
            return _semantics(expr.args[-1])
    return "accumulate"


def _contains_array(expr: TypeExpr | None) -> bool:
    if isinstance(expr, Named):
        return "array" in expr.name or any(_contains_array(a) for a in expr.args if not isinstance(a, Group))
    return False


def _canon(expr: TypeExpr) -> Any:
    return _canon_type(to_bigraph(expr), None)


def _text(expr: TypeExpr) -> str:
    from process_bigraph_lang.v2.types import to_surface

    return to_surface(expr)
