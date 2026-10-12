"""
Documents -> the v2 model.

`read_document` walks the state and schema halves of a `{"schema", "state"}` document in parallel and
classifies every key as a site, an edge, a node (a subtree with edges or sites below it, or a struct-typed
subtree) or a store. It accepts both the authoring form and the form `Composite.save()` writes (`source="saved"`,
auto-detected). `read_composite_spec` reads a CompositeSpec mapping (`*.composite.yaml`): its `parameters`
become `Param`s, `${name}` strings become `ParamRef`s, and `emitters` become `Emitter` declarations.
"""

from __future__ import annotations

from typing import Any

from process_bigraph_lang.v2.model import (
    Address,
    Composite,
    Document,
    Edge,
    Element,
    Emitter,
    Face,
    Node,
    Param,
    ParamRef,
    Site,
    Store,
)
from process_bigraph_lang.v2.paths import Path, wire_from_document
from process_bigraph_lang.v2.types import Struct, TypeExpr, parse_type, to_bigraph
from process_bigraph_lang.v2.values import (
    COMPOSITE_OPTION_KEYS,
    EDGE_KINDS,
    MISSING,
    PARAM_FULL,
    PARAM_INLINE,
    RUNTIME_EDGE_KEYS,
    contains_edge_or_site,
    is_edge_node,
    is_site,
)

_EDGE_KEYS = ("_type", "address", "config", "inputs", "outputs", "_inputs", "_outputs", "interval", "priority")
_NESTED_CONFIG_KEYS = ("state", "schema", "bridge", "interface")


def read_document(doc: dict[str, Any], *, source: str = "auto", params: set[str] | None = None) -> Document:
    """Read a `{"schema", "state"}` document. `source` is `authoring`, `saved` or `auto` (detect the saved form)."""
    schema = doc.get("schema") or {}
    state = doc.get("state") or {}
    if source == "auto":
        source = "saved" if _looks_saved(state) else "authoring"
    reader = _Reader(saved=(source == "saved"), params=params or set())
    document = Document(source=source)  # type: ignore[arg-type]
    document.root = reader.composite(state, schema)
    document.options = {k: doc[k] for k in COMPOSITE_OPTION_KEYS if k in doc}
    document.extras = {k: v for k, v in doc.items() if k not in ("schema", "state") and k not in COMPOSITE_OPTION_KEYS}
    return document


def read_composite_spec(spec: dict[str, Any]) -> Document:
    """Read a CompositeSpec mapping (the content of a `*.composite.yaml`, or `CompositeSpec.to_dict()`)."""
    params = [_param(name, decl) for name, decl in (spec.get("parameters") or {}).items()]
    options = {k: spec[k] for k in COMPOSITE_OPTION_KEYS if k in spec}
    doc = read_document(
        {"schema": spec.get("schema") or {}, "state": spec.get("state") or {}, **options},
        source="composite_spec",
        params={p.name for p in params},
    )
    doc.params = params
    doc.name = spec.get("name")
    doc.description = spec.get("description") or ""
    doc.tags = list(spec.get("tags") or [])
    doc.requires = dict(spec.get("requires") or {})
    doc.emitters = [_emitter(e) for e in spec.get("emitters") or []]
    known = {"schema", "state", "parameters", "name", "description", "tags", "requires", "emitters", *options}
    doc.extras = {k: v for k, v in spec.items() if k not in known}
    return doc


def _param(name: str, decl: Any) -> Param:
    if not isinstance(decl, dict):
        return Param(name, default=decl)
    type_text = decl.get("type")
    return Param(
        name,
        type=parse_type(str(type_text)) if type_text is not None else None,
        default=decl.get("default", MISSING),
        description=str(decl.get("description") or ""),
        choices=list(decl["choices"]) if decl.get("choices") is not None else None,
    )


def _emitter(decl: dict[str, Any]) -> Emitter:
    paths = []
    for path in decl.get("paths") or []:
        parts = [p for p in str(path).replace(".", "/").split("/") if p]
        paths.append(Path(list(parts)))
    config = dict(decl.get("config") or {})
    return Emitter(Address.from_any(decl.get("address") or "local:RAMEmitter"), paths, config)


def _looks_saved(state: Any) -> bool:
    """`Composite.save()` output: dict-form addresses, `_contract`/`instance` keys (a root `global_time` alone is not proof)."""
    return isinstance(state, dict) and any(_has_saved_edge(v) for v in state.values())


def _has_saved_edge(value: Any) -> bool:
    if not isinstance(value, dict):
        return False
    if is_edge_node(value) and (isinstance(value.get("address"), dict) and "protocol" in value["address"]):
        return True
    if "_contract" in value or "instance" in value:
        return True
    return any(_has_saved_edge(v) for v in value.values())


class _Reader:
    def __init__(self, *, saved: bool, params: set[str]) -> None:
        self.saved = saved
        self.params = params

    # --- tree ----------------------------------------------------------------------------------------------------

    def composite(self, state: dict[str, Any], schema: Any) -> Composite:
        composite = Composite()
        if isinstance(schema, str):  # a saved nested composite renders its schema as a string
            parsed = parse_type(schema)
            schema = {k: to_bigraph(v) for k, v in parsed.fields.items()} if isinstance(parsed, Struct) else {}
        elif not isinstance(schema, dict):
            schema = {}
        keys = list(state) + [k for k in schema if k not in state]
        for key in keys:
            if key == "global_time" and self.saved:
                continue
            element = self.element(str(key), state.get(key, MISSING), schema.get(key, MISSING))
            if element is None:
                composite.schema_extras[str(key)] = schema[key]
            else:
                composite.children[str(key)] = element
        return composite

    def element(self, key: str, state: Any, schema: Any) -> Element | None:
        if is_site(state):
            return Store(key, type=self.type_of(schema), site=self.site(state))
        if is_edge_node(state) or (_schema_is_edge(schema) and isinstance(state, dict)):
            return self.edge(key, state if isinstance(state, dict) else {}, schema)
        if isinstance(state, dict) and (contains_edge_or_site(state) or _schema_is_struct(schema)):
            node = Node(key, type=parse_type(schema) if _schema_is_edge_map(schema) else None)
            child_schema = schema if _schema_is_struct(schema) else {}
            node.children = self.composite(state, child_schema).children
            return node
        if state is MISSING:
            if _schema_is_edge(schema):
                return self.edge(key, {}, schema)
            return Store(key, type=self.type_of(schema)) if schema is not MISSING else None
        return Store(key, type=self.type_of(schema), value=self.value(state))

    def type_of(self, schema: Any) -> TypeExpr | None:
        if schema is MISSING or schema is None:
            return None
        return parse_type(schema)

    def site(self, site: dict[str, Any]) -> Site:
        sort = site.get("_sort", "node")
        return Site(parse_type(sort), default=self.value(site["_default"]) if "_default" in site else MISSING)

    # --- edges ---------------------------------------------------------------------------------------------------

    def edge(self, key: str, node: dict[str, Any], schema: Any) -> Edge:
        kind = (
            node.get("_type") or (schema.get("_type") if isinstance(schema, dict) else None) or _guess_kind(key, node)
        )
        address = self.address(node.get("address"))
        edge = Edge(key, str(kind), address)
        config = node.get("config")
        if isinstance(config, dict) and isinstance(address, Address) and address.is_composite:
            edge.inner = self.composite(config.get("state") or {}, config.get("schema") or {})
            edge.bridge = config.get("bridge")
            edge.interface = config.get("interface")
            config = {k: v for k, v in config.items() if k not in _NESTED_CONFIG_KEYS}
        edge.config = self.value(config) if isinstance(config, dict) else {}
        edge.inputs = {str(k): wire_from_document(v) for k, v in (node.get("inputs") or {}).items()}
        edge.outputs = {str(k): wire_from_document(v) for k, v in (node.get("outputs") or {}).items()}
        if node.get("interval") is not None:
            edge.interval = self.value(node["interval"])
        if node.get("priority") is not None:
            edge.priority = node["priority"]
        edge.ports = self.ports(node, schema)
        edge.extras = {
            str(k): self.value(v) for k, v in node.items() if k not in _EDGE_KEYS and k not in RUNTIME_EDGE_KEYS
        }
        return edge

    def address(self, address: Any) -> Address | Site | ParamRef | None:
        if address is None:
            return None
        if is_site(address):
            return self.site(address)
        if isinstance(address, str) and PARAM_FULL.match(address) and self.params:
            return ParamRef(PARAM_FULL.match(address).group(1))  # type: ignore[union-attr]
        return Address.from_any(address)

    def ports(self, node: dict[str, Any], schema: Any) -> Face | None:
        face = Face()
        found = False
        for key, attr in (("_inputs", "inputs"), ("_outputs", "outputs")):
            ports = node.get(key, schema.get(key) if isinstance(schema, dict) else None)
            if ports is None:
                continue
            found = True
            setattr(face, attr, _port_types(ports))
        return face if found else None

    # --- values --------------------------------------------------------------------------------------------------

    def value(self, value: Any) -> Any:
        if isinstance(value, str) and self.params:
            full = PARAM_FULL.match(value)
            if full:
                return ParamRef(full.group(1))
            if PARAM_INLINE.search(value):
                return ParamRef(PARAM_INLINE.search(value).group(1), template=value)  # type: ignore[union-attr]
            return value
        if isinstance(value, dict):
            return {k: self.value(v) for k, v in value.items()}
        if isinstance(value, list):
            return [self.value(v) for v in value]
        if isinstance(value, tuple):
            return tuple(self.value(v) for v in value)
        return value


def _port_types(ports: Any) -> dict[str, TypeExpr]:
    if isinstance(ports, str):
        parsed = parse_type(ports)
        if isinstance(parsed, Struct):
            return dict(parsed.fields)
        return {} if ports.strip() == "" else {"_": parsed}
    if isinstance(ports, dict):
        return {str(k): parse_type(v) for k, v in ports.items()}
    return {}


def _schema_is_edge(schema: Any) -> bool:
    return isinstance(schema, dict) and schema.get("_type") in EDGE_KINDS


def _schema_is_edge_map(schema: Any) -> bool:
    return isinstance(schema, dict) and schema.get("_type") == "map" and _schema_is_edge(schema.get("_value"))


def _schema_is_struct(schema: Any) -> bool:
    return isinstance(schema, dict) and bool(schema) and not any(str(k).startswith("_") for k in schema)


def _guess_kind(key: str, node: dict[str, Any]) -> str:
    if "interval" in node:
        return "process"
    if "priority" in node or "_triggers" in node:
        return "step"
    raise ValueError(f"edge '{key}' has neither a _type nor a schema entry saying whether it is a step or a process")
