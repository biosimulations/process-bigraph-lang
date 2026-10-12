"""
Static checks of a composite against interface declarations, without importing any process code.

Given a `Document` and an `InterfaceRegistry` (interface files or manifests), `check_document` reports: ports
that the interface does not declare, config keys it does not declare or requires, wires that name no declared
store (process-bigraph would create one silently), wires whose target's declared type differs from the port's,
paths that escape the root, an `interval` on a step, components the registry does not know (their ports and
config go unchecked) and interfaces whose ports depend on an instance (declared by hand later). It also analyses
the writers of each store: additive writers that superpose (for review), an overwriting writer next to another
writer (order-dependent), and a step publishing an array additively (usually meant `overwrite`); it checks units
(port units, possibly with unit variables bound from the wired stores, against the stores' units); and it checks
`emit` declarations: a path naming no declared store, or an observable that nothing writes. This is the
S2–S4 slice of the diagnostics model in `docs/v2/design.md`; codes follow `docs/v2/registry-and-authoring.md`.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from process_bigraph_lang.v2.interfaces import InterfaceRegistry
from process_bigraph_lang.v2.model import (
    MODEL_BLOCKS,
    Address,
    Composite,
    ConfigField,
    Document,
    Edge,
    Emitter,
    InterfaceDecl,
    ModelDecl,
    ModelRef,
    Node,
    Param,
    ParamRef,
    Site,
    Store,
)
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
    checker = _Checker(
        registry, {m.name: m for m in doc.models}, {p.name: p for p in doc.params}, {d.name: d for d in doc.interfaces}
    )
    checker.scope(doc.root, ())
    checker.emitters(doc.emitters)
    order = {"error": 0, "warning": 1, "info": 2}
    return sorted(checker.diagnostics, key=lambda d: (order[d.severity], d.path, d.code))


_Target = tuple[tuple[str | int, ...], TypeExpr | None, bool]  # absolute path, declared type, declared?


@dataclass
class _UnitObligation:
    port_path: tuple[str | int, ...]
    port_units: str  # may contain unit variables `?U`
    store_units: str
    store: str


_UNIT_VAR = re.compile(r"\?([A-Za-z_][A-Za-z0-9_]*)")
_REGISTRY: list[Any] = []


def _unit_registry() -> Any:
    if not _REGISTRY:
        import pint

        _REGISTRY.append(pint.UnitRegistry())
    return _REGISTRY[0]


def _substitute(expr: str, bindings: dict[str, str]) -> str:
    return _UNIT_VAR.sub(lambda m: f"({bindings[m.group(1)]})" if m.group(1) in bindings else m.group(0), expr)


def _solve(expr: str, variable: str, target: str, registry: Any) -> str | None:
    """The units of `?variable` that make `expr` equal to `target`, for expressions linear in the variable."""
    try:
        rest = registry.parse_expression(_UNIT_VAR.sub(lambda m: "1" if m.group(1) == variable else m.group(0), expr))
        wanted = registry.parse_expression(target)
        for candidate in (wanted / rest, rest / wanted):
            trial = registry.parse_expression(_substitute(expr, {variable: str(candidate.units)}))
            if (
                trial.dimensionality == wanted.dimensionality
                and abs(float((trial / wanted).to_base_units().magnitude) - 1) < 1e-9
            ):
                return str(candidate.units)
    except Exception:  # noqa: BLE001
        return None
    return None


def _units_of(expr: TypeExpr | None) -> str | None:
    """The units a type carries, on the type itself or on the value type below a map/list/overwrite."""
    if isinstance(expr, Named):
        if expr.units is not None:
            return expr.units
        for arg in reversed(expr.args):
            if not isinstance(arg, Group):
                return _units_of(arg)
    return None


@dataclass
class _Writer:
    port_path: tuple[str | int, ...]
    kind: str  # process | step
    port_type: TypeExpr | None
    store_type: TypeExpr | None


class _Checker:
    def __init__(
        self,
        registry: InterfaceRegistry | None,
        models: dict[str, ModelDecl] | None = None,
        params: dict[str, Param] | None = None,
        interfaces: dict[str, InterfaceDecl] | None = None,
    ) -> None:
        self.registry = registry
        self.models = models or {}
        self.params = params or {}
        self.interfaces = interfaces or {}  # declared inline in the text
        self.diagnostics: list[Diagnostic] = []
        self.index: dict[tuple[str | int, ...], Store | Node | Edge] = {}
        self.writers: dict[tuple[str | int, ...], list[_Writer]] = {}
        self.root_index: dict[tuple[str | int, ...], Store | Node | Edge] = {}
        self.root_writers: dict[tuple[str | int, ...], list[_Writer]] = {}
        self.unit_obligations: list[_UnitObligation] = []

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
            elif isinstance(element, Store):
                self.model_site(element, path)
        self.writer_analysis()
        if not base:
            self.root_index, self.root_writers = self.index, dict(self.writers)
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
        self.unit_obligations = []
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
                self.wire(
                    wire,
                    port_type,
                    path[:-1],
                    port_path,
                    writer=edge.kind if label == "outputs" else None,
                    units=_units_of(port_type),
                )
        if decl is not None:
            for key, value in edge.config.items():
                field = decl.config.get(key)
                if field is None or not isinstance(value, ParamRef) or value.template is not None:
                    continue
                param = self.params.get(value.name)
                field_units = _units_of(field.type)
                param_units = _units_of(param.type) if param is not None else None
                if field_units and param_units:
                    self.unit_obligations.append(
                        _UnitObligation((*path, "config", key), field_units, param_units, f"param {value.name}")
                    )
        self.units(path)

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
        if edge.iface_name and edge.iface_name in self.interfaces:
            declared = self.interfaces[edge.iface_name]
            if declared.dynamic_ports:
                self.report(
                    "I210",
                    "dynamic-ports",
                    "info",
                    path,
                    f"{declared.name}: ports depend on an instance; only the declared ones are checked",
                )
            return declared
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
        units: str | None = None,
    ) -> None:
        """Check one wire; `writer` is the edge kind when this is an output wire (it then writes the store)."""
        if isinstance(wire, dict):
            element = _map_value_type(port_type)
            for sub_port, sub_wire in wire.items():
                self.wire(sub_wire, element, parent, (*port_path, sub_port), writer, units)
            return
        target = self.resolve(wire, parent, port_path)
        if target is None:
            return
        absolute, store_type, declared = target
        if writer is not None:
            self.writers.setdefault(absolute, []).append(_Writer(port_path, writer, port_type, store_type))
        store_units = _units_of(store_type)
        if units is not None and store_units is not None:
            self.unit_obligations.append(_UnitObligation(port_path, units, store_units, "/".join(map(str, absolute))))
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

    # --- model sites -------------------------------------------------------------------------------------------

    def model_site(self, store: Store, path: tuple[str | int, ...]) -> None:
        """`store m : Sort = Header;` admits the header against the sort; `store m : Sort = ?;` is an open site."""
        sort = self.models.get(store.type.name) if isinstance(store.type, Named) else None
        if sort is None or not sort.is_sort:
            return
        if store.site is not None:
            self.report(
                "I301",
                "open-model-site",
                "info",
                path,
                f"open model site sorted by {sort.name}; a model header fills it",
            )
            return
        if not isinstance(store.value, ModelRef):
            return
        header = self.models.get(store.value.name)
        if header is None or header.is_sort:
            self.report("G300", "model-missing", "error", path, f"no model header named '{store.value.name}'")
            return
        self.admit_model(sort, header, path)

    def admit_model(self, sort: ModelDecl, header: ModelDecl, path: tuple[str | int, ...]) -> None:
        """Every member and requirement of the sort must be provided by the header; units bind across the header."""
        self.unit_obligations = []
        who = f"{header.name} (for sort {sort.name})"
        if sort.time_units:
            if header.time_units:
                self.unit_obligations.append(
                    _UnitObligation((*path, "time"), sort.time_units, header.time_units, f"{header.name}.time")
                )
            else:
                self.report(
                    "G301",
                    "model-not-admitted",
                    "error",
                    (*path, "time"),
                    f"{who}: the sort requires a time unit; the header declares none",
                )
        for block in MODEL_BLOCKS:
            required, provided = sort.block(block), header.block(block)
            wildcard = required.get("_")
            for name, field in required.items():
                if name == "_":
                    continue
                if name not in provided:
                    self.report(
                        "G301",
                        "model-not-admitted",
                        "error",
                        (*path, block, name),
                        f"{who}: the sort requires {block[:-1]} '{name}', which the header lacks",
                    )
                    continue
                self.obligation((*path, block, name), field, provided[name], f"{header.name}.{block}.{name}")
            if wildcard is not None:
                for name, field in provided.items():
                    self.obligation((*path, block, name), wildcard, field, f"{header.name}.{block}.{name}")
            extra = sorted(set(provided) - set(required))
            if required and wildcard is None and block not in sort.open_blocks and extra:
                self.report(
                    "G301",
                    "model-not-admitted",
                    "error",
                    (*path, block),
                    f"{who}: the sort admits exactly {sorted(k for k in required)}; the header also has {extra}",
                )
        for key, wanted in sort.meta.items():
            if header.meta.get(key) != wanted:
                self.report(
                    "G301",
                    "model-not-admitted",
                    "error",
                    (*path, "meta", key),
                    f"{who}: the sort requires {key} = {wanted!r}; the header has {header.meta.get(key)!r}",
                )
        self.units(path)

    def obligation(self, at: tuple[str | int, ...], required: ConfigField, provided: ConfigField, label: str) -> None:
        required_units, provided_units = _units_of(required.type), _units_of(provided.type)
        if required_units and provided_units:
            self.unit_obligations.append(_UnitObligation(at, required_units, provided_units, label))
        elif required_units and not provided_units:
            self.report(
                "I232",
                "units-undeclared",
                "info",
                at,
                f"{label} declares no units; '{required_units}' cannot be checked",
            )

    # --- units -------------------------------------------------------------------------------------------------

    def units(self, path: tuple[str | int, ...]) -> None:
        """
        Unit consistency of one edge. A port's units are a unit expression that may contain unit variables
        (`?U`, `?U/?T`): the variables are bound per instance from the stores the ports are wired to, so a
        component that works in any consistent unit system (an SBML solver, say) declares `?U` and `?T` and still
        gets checked. A bound expression that does not match its store's units is reported with the conversion
        factor when the dimensions agree, or as incompatible when they do not.
        """
        if not self.unit_obligations:
            return
        registry = _unit_registry()
        bindings: dict[str, str] = {}
        pending = list(self.unit_obligations)
        for _ in range(len(pending) + 1):  # each round binds at least one variable or stops
            still: list[_UnitObligation] = []
            for ob in pending:
                expr = _substitute(ob.port_units, bindings)
                free = sorted(set(_UNIT_VAR.findall(expr)))
                if not free:
                    self.compare_units(ob, expr, registry)
                elif len(free) == 1:
                    solved = _solve(expr, free[0], ob.store_units, registry)
                    if solved is None:
                        self.report(
                            "I231",
                            "unit-unresolved",
                            "info",
                            ob.port_path,
                            f"cannot solve '{ob.port_units}' for ?{free[0]} from '{ob.store_units}'",
                        )
                    else:
                        bindings[free[0]] = solved
                        self.compare_units(ob, _substitute(ob.port_units, bindings), registry)
                else:
                    still.append(ob)
            if len(still) == len(pending):
                for ob in still:
                    self.report(
                        "I231",
                        "unit-unresolved",
                        "info",
                        ob.port_path,
                        f"'{ob.port_units}' has unbound unit variables; no store pins them",
                    )
                break
            pending = still

    def compare_units(self, ob: _UnitObligation, expr: str, registry: Any) -> None:
        try:
            port_q = registry.parse_expression(expr)
            store_q = registry.parse_expression(ob.store_units)
        except Exception:  # noqa: BLE001 - pint cannot parse one of them
            self.report(
                "I230", "unit-unparsed", "info", ob.port_path, f"cannot parse units '{expr}' or '{ob.store_units}'"
            )
            return
        if port_q.dimensionality != store_q.dimensionality:
            self.report(
                "W201",
                "unit-mismatch",
                "warning",
                ob.port_path,
                f"port units '{expr}' ({port_q.dimensionality}) are incompatible with store '{ob.store}' in '{ob.store_units}' ({store_q.dimensionality})",
            )
            return
        factor = float((port_q / store_q).to_base_units().magnitude)
        if abs(factor - 1.0) > 1e-9:
            self.report(
                "W201",
                "unit-mismatch",
                "warning",
                ob.port_path,
                f"port units '{expr}' but store '{ob.store}' is in '{ob.store_units}': convertible, factor {factor:g}; insert a conversion or align the units",
            )

    # --- emit declarations -------------------------------------------------------------------------------------

    def emitters(self, emitters: list[Emitter]) -> None:
        """
        `emit … { paths }` declarations name observables by path from the root. A path that names nothing is the
        silent-empty-dict trap (process-bigraph's emitter materializes it); a declared store that nothing writes is
        a constant, worth knowing before a long run records it.
        """
        self.index = self.root_index
        try:
            for index, emitter in enumerate(emitters):
                for path in emitter.paths:
                    at = ("emit", index, path.to_slash())
                    target = self.resolve(path, (), at)
                    if target is None:
                        continue
                    absolute, _, declared = target
                    if absolute == ("global_time",):
                        continue  # injected and advanced by the scheduler, never declared
                    if not declared:
                        self.report(
                            "W240",
                            "emit-path-unknown",
                            "warning",
                            at,
                            f"emit path '{path.to_slash()}' names no declared store; the emitter would record an empty value",
                        )
                    elif not self.written(absolute):
                        self.report(
                            "W241",
                            "observable-never-written",
                            "info",
                            at,
                            f"'{path.to_slash()}' is emitted but no edge writes it: it is a constant",
                        )
        finally:
            self.index = {}

    def written(self, path: tuple[str | int, ...]) -> bool:
        """A path is written when a writer targets it, something below it, or something above it."""
        for target in self.root_writers:
            shorter, longer = (path, target) if len(path) <= len(target) else (target, path)
            if tuple(longer[: len(shorter)]) == tuple(shorter):
                return True
        return False

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
    """The type for comparison, without units: units are checked separately, with their own semantics."""
    return _strip_units(_canon_type(to_bigraph(expr), None))


def _strip_units(canon: Any) -> Any:
    if isinstance(canon, dict):
        stripped = {k: _strip_units(v) for k, v in canon.items() if k != "_units"}
        return stripped["_type"] if set(stripped) == {"_type"} and isinstance(stripped["_type"], str) else stripped
    if isinstance(canon, list):
        return [_strip_units(v) for v in canon]
    return canon


def _text(expr: TypeExpr) -> str:
    from process_bigraph_lang.v2.types import to_surface

    return to_surface(expr)
