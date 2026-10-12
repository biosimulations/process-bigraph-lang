"""
A parser for the `.pblang` v2 subset the printer emits, so the round trip can start from text.

`read_text` parses canonical v2 text into a `Document` (the same model the reader produces from a document),
including inline interface declarations, `import`s, params, meta/options, stores, nodes, edges, nested composites,
sites, and the printer's `array(...)` / `file(...)` value forms. The grammar is a Lark LALR grammar; it is the
executable form of the sketch in `docs/v2/design.md` and the acceptance spec for the later Langium grammar.
Not covered yet: expressions (`k * dt`), `replicate`, `{default}` suffixes on types, `when`/`of config.x` faces.
"""

from __future__ import annotations

import json
from typing import Any

import numpy as np
from lark import Lark, Token, Transformer, v_args

from process_bigraph_lang.v2.interfaces import InterfaceRegistry
from process_bigraph_lang.v2.model import (
    Address,
    Composite,
    ConfigField,
    Document,
    Edge,
    Element,
    Emitter,
    ExternalRef,
    Face,
    InterfaceDecl,
    ModelDecl,
    ModelRef,
    Node,
    Param,
    ParamRef,
    Site,
    Store,
)
from process_bigraph_lang.v2.paths import Path, Wire, parse_path, wire_to_document
from process_bigraph_lang.v2.printer import EMITTER_ALIASES
from process_bigraph_lang.v2.reader import _Reader
from process_bigraph_lang.v2.types import Group, Named, Raw, Struct, TypeExpr, UnionType, to_bigraph
from process_bigraph_lang.v2.values import MISSING

GRAMMAR = r"""
start: header? statement*
header: "module" qualified ";"
statement: import_names | import_module | param | meta | options | interface | model_decl | composite_root | emit

model_decl: [doc] "model" NAME ["from" STRING] "{" model_item* "}"
model_item: "time" "@" STRING ";"            -> model_time
          | "compartments" model_block       -> model_compartments
          | "species" model_block            -> model_species
          | "parameters" model_block         -> model_parameters
          | "meta" kvblock                   -> model_meta
model_block: "{" field* [ELLIPSIS] "}"

import_names: "import" MODULE_BRACE NAME ("," NAME)* "}" ";"
import_module: "import" qualified ";"
qualified: NAME ("." NAME)*

param: [doc] "param" NAME ":" type ["=" value] ["choices" list_lit] ";"
meta: "meta" kvblock
options: "options" kvblock

interface: [doc] IFACE_KIND NAME ["at" STRING] "{" iface_item* "}"
IFACE_KIND: "process" | "step" | "adapter"
iface_item: "config" "{" field* "}"     -> iface_config
          | "inputs" face_body          -> iface_inputs
          | "outputs" face_body         -> iface_outputs
face_body: "{" field* "}"               -> face_fields
         | "{" ELLIPSIS "}"             -> face_open
field: [doc] key ":" type ["=" value] ";"

composite_root: [doc] "composite" [key] "{" node_decl* "}"
node_decl: store | node | edge | schema_block
store: [doc] "store" key [":" type] ["=" value] ";"
node: [doc] "node" key [":" type] "{" node_decl* "}"
edge: [doc] EDGE_KIND key edge_type [every] [priority] "{" edge_item* "}"       -> plain_edge
    | [doc] "composite" key [every] ["at" STRING] "{" comp_item* "}"             -> composite_edge
    | [doc] "shared" "process" key edge_type "{" edge_item* "}"                  -> shared_edge
EDGE_KIND: "process" | "step"
edge_type: ":" NAME ["at" address]      -> typed_edge
         | "at" address                  -> untyped_edge
         | ":" "shared" key              -> shared_ref
address: STRING | site | PARAM
every: "every" scalar
priority: "priority" scalar
scalar: NUMBER | PARAM
edge_item: "config" kvblock             -> config_block
         | "inputs" wireblock           -> inputs_block
         | "outputs" wireblock          -> outputs_block
         | "ports" "{" [ports_inputs] [ports_outputs] "}"  -> ports_block
ports_inputs: "inputs" "{" field* "}"
ports_outputs: "outputs" "{" field* "}"
         | "extra" kvblock              -> extra_block
comp_item: edge_item
         | "bridge" wireblock           -> bridge_block
         | "interface" kvblock          -> interface_block
         | "options" kvblock            -> options_block
         | "composite" "{" node_decl* "}"  -> inner_block
schema_block: "schema" kvblock
wireblock: "{" [wire ("," wire)* ","?] "}"
wire: key "->" PATH                     -> wire_path
    | key wireblock                     -> wire_sub

emit: "emit" (NAME | STRING) "{" [PATH ("," PATH)*] "}" ["with" kvblock] ";"

kvblock: "{" [kv ("," kv)* ","?] "}"
kv: key "=" value
key: NAME | STRING

?value: NUMBER            -> number
      | STRING            -> string
      | NAME              -> ref
      | "true"            -> true
      | "false"           -> false
      | "null"            -> null
      | PARAM             -> paramref
      | site
      | kvblock
      | list_lit
      | tuple_lit
      | array_lit
      | file_lit
site: "?" ["(" value ")"] ["as" type]
list_lit: "[" [value ("," value)* ","?] "]"
tuple_lit: "(" [value ("," value)* ","?] ")"
array_lit: "array" "(" (list_lit | file_lit) ("," NAME "=" value)* ")"
file_lit: "file" "(" STRING ")"

type: type_prim ("|" type_prim)*
type_prim: "link" "<" struct_type "," struct_type ">"                      -> link_type
         | NAME ["<" type_arg ("," type_arg)* ">"] [shape] ["@" STRING]    -> named_type
         | struct_type
         | STRING                                                           -> raw_type
struct_type: "{" field* "}"
type_arg: type | NUMBER -> number_arg
shape: "[" dim ("," dim)* "]"
dim: NUMBER | "_" | NAME

doc: DOC+

DOC: /\/\/\/[^\n]*/
ELLIPSIS: "..."
MODULE_BRACE.2: /[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)*\.\{/
COMMENT: /\/\/(?!\/)[^\n]*/
NAME: /[A-Za-z_][A-Za-z0-9_]*/
STRING: /"(\\.|[^"\\])*"/
NUMBER: /-?(\d+\.\d*|\.\d+)([eE][+-]?\d+)?|-?\d+([eE][+-]?\d+)?/
PARAM: /\$\{[A-Za-z_][A-Za-z0-9_]*\}/
PATH: /(\.\.\/)*(\.\.|\*|[A-Za-z_][A-Za-z0-9_]*|"(\\.|[^"\\])*")((\.(\*|[A-Za-z_][A-Za-z0-9_]*|"(\\.|[^"\\])*"))|(\[\d+\]))*/
%import common.WS
%ignore WS
%ignore COMMENT
"""

_PARSER = Lark(GRAMMAR, parser="lalr", maybe_placeholders=True)
_ALIAS_ADDRESSES = {alias: f"local:{name}" for name, alias in EMITTER_ALIASES.items()}


def read_text(text: str, *, registry: InterfaceRegistry | None = None) -> Document:
    """Parse canonical `.pblang` v2 text into a `Document`. `registry` supplies the faces of imported interfaces."""
    tree = _PARSER.parse(text)
    builder = _Builder(registry)
    builder.transform(tree)
    return builder.document


def _tok(token: Any) -> str:
    return str(token)


def _string(token: Any) -> str:
    return str(json.loads(str(token)))


def _number(token: Any) -> int | float:
    text = str(token)
    return float(text) if any(c in text for c in ".eE") else int(text)


class _Doc(str):
    """A `///` doc comment attached to the next declaration."""


@v_args(inline=True)
class _Builder(Transformer):
    def __init__(self, registry: InterfaceRegistry | None = None) -> None:
        super().__init__()
        self.registry = registry
        self.document = Document()
        self.imports: dict[str, str] = {}  # interface name -> module
        self.interfaces: dict[str, InterfaceDecl] = {}
        self._reader = _Reader(saved=False, params=set())

    # --- module --------------------------------------------------------------------------------------------------

    def start(self, *items: Any) -> Document:
        names = self.document.param_names
        if names:
            self._reader.params = names
            self.document.root = self._substitute(self.document.root)
        return self.document

    def header(self, qualified: str) -> None:
        return None

    def qualified(self, *names: Any) -> str:
        return ".".join(_tok(n) for n in names)

    def statement(self, item: Any) -> Any:
        return item

    def import_names(self, module: Any, *names: Any) -> None:
        for name in names:
            self.imports[_tok(name)] = _tok(module)[:-2]  # strip the trailing ".{"

    def import_module(self, module: str) -> None:
        return None

    def doc(self, *tokens: Any) -> _Doc:
        return _Doc(" ".join(_tok(t)[3:].strip() for t in tokens))  # the printer wraps long lines

    def param(self, doc: _Doc | None, name: Any, type_: TypeExpr, default: Any, choices: Any) -> None:
        site = isinstance(default, Site)
        self.document.params.append(
            Param(
                _tok(name),
                type=type_,
                default=MISSING if default is None or site else default,
                description=str(doc) if doc else "",
                choices=list(choices) if choices is not None else None,
            )
        )

    def meta(self, entries: dict[str, Any]) -> None:
        entries = dict(entries)
        self.document.tags = list(entries.pop("tags", []) or [])
        self.document.requires = dict(entries.pop("requires", {}) or {})
        self.document.extras.update(entries)

    def options(self, entries: dict[str, Any]) -> None:
        self.document.options.update(entries)

    def emit(self, target: Any, *rest: Any) -> None:
        paths = [parse_path(_tok(p)) for p in rest if isinstance(p, Token) and p.type == "PATH"]
        config = next((r for r in rest if isinstance(r, dict)), {})
        if target.type == "STRING":
            address = Address.from_any(_string(target))
        else:
            address = Address.from_any(_ALIAS_ADDRESSES.get(_tok(target), f"local:{_tok(target)}"))
        self.document.emitters.append(Emitter(address, paths, dict(config)))

    # --- interfaces ----------------------------------------------------------------------------------------------

    def interface(self, doc: _Doc | None, kind: Any, name: Any, address: Any, *items: Any) -> None:
        decl = InterfaceDecl(
            _tok(name),
            _tok(kind),
            address=Address.from_any(_string(address)) if address is not None else None,
            doc=str(doc) if doc else None,
        )
        for label, payload in items:
            if label == "config":
                decl.config = payload
            elif label == "inputs":
                decl.inputs, decl.dynamic_ports = payload if payload is not None else (None, True)
            else:
                decl.outputs, decl.dynamic_ports = payload if payload is not None else (None, True)
        self.interfaces[decl.name] = decl
        self.document.interfaces.append(decl)

    def iface_config(self, *fields: tuple[str, ConfigField]) -> tuple[str, dict[str, ConfigField]]:
        return "config", dict(fields)

    def iface_inputs(self, body: Any) -> tuple[str, Any]:
        return "inputs", body

    def iface_outputs(self, body: Any) -> tuple[str, Any]:
        return "outputs", body

    def face_fields(self, *fields: tuple[str, ConfigField]) -> tuple[dict[str, TypeExpr], bool]:
        return {k: f.type for k, f in fields if f.type is not None}, False

    def face_open(self, _ellipsis: Any) -> None:
        return None

    # --- models --------------------------------------------------------------------------------------------------

    def model_decl(self, doc: _Doc | None, name: Any, source: Any, *items: tuple[str, Any]) -> None:
        decl = ModelDecl(_tok(name), _string(source) if source is not None else None, doc=str(doc) if doc else None)
        for label, payload in items:
            if label == "time":
                decl.time_units = payload
            elif label == "meta":
                decl.meta = dict(payload)
            else:
                fields, open_block = payload
                decl.block(label).update(fields)
                if open_block:
                    decl.open_blocks.add(label)
        self.document.models.append(decl)

    def model_time(self, units: Any) -> tuple[str, str]:
        return "time", _string(units)

    def model_compartments(self, block: Any) -> tuple[str, Any]:
        return "compartments", block

    def model_species(self, block: Any) -> tuple[str, Any]:
        return "species", block

    def model_parameters(self, block: Any) -> tuple[str, Any]:
        return "parameters", block

    def model_meta(self, entries: dict[str, Any]) -> tuple[str, Any]:
        return "meta", entries

    def model_block(self, *items: Any) -> tuple[dict[str, ConfigField], bool]:
        fields = {k: f for k, f in (i for i in items if isinstance(i, tuple))}
        return fields, any(isinstance(i, Token) and i.type == "ELLIPSIS" for i in items)

    def ref(self, token: Any) -> ModelRef:
        return ModelRef(_tok(token))

    def field(self, doc: _Doc | None, key: str, type_: TypeExpr, default: Any) -> tuple[str, ConfigField]:
        return key, ConfigField(type_, MISSING if default is None else default, str(doc) if doc else None)

    # --- tree ----------------------------------------------------------------------------------------------------

    def composite_root(self, doc: _Doc | None, name: str | None, *decls: Element | tuple[str, dict[str, Any]]) -> None:
        self.document.name = name
        self.document.description = str(doc) if doc else ""
        self.document.root = self._composite(decls)

    def _composite(self, decls: tuple[Any, ...]) -> Composite:
        composite = Composite()
        for decl in decls:
            if isinstance(decl, tuple) and decl[0] == "schema":
                composite.schema_extras.update(decl[1])
            elif isinstance(decl, (Store, Node, Edge)):
                composite.children[decl.name] = decl
        return composite

    def node_decl(self, item: Any) -> Any:
        return item

    def schema_block(self, entries: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        return "schema", entries

    def store(self, doc: _Doc | None, key: str, type_: TypeExpr | None, value: Any) -> Store:
        store = Store(key, type=type_, doc=str(doc) if doc else None)
        if isinstance(value, Site) and value.default is MISSING and type_ is not None and _is_unsorted(value.sort):
            store.site = Site(type_, MISSING)  # `store m : ODEModel = ?;` is a model site sorted by its type
            return store
        if isinstance(value, Site):
            sort = value.sort if not _is_unsorted(value.sort) else (type_ or Named("node"))
            store.site = Site(sort, value.default)
        elif value is not None:
            store.value = value
        return store

    def node(self, doc: _Doc | None, key: str, type_: TypeExpr | None, *decls: Any) -> Node:
        return Node(key, self._composite(decls).children, type=type_, doc=str(doc) if doc else None)

    def plain_edge(
        self, doc: _Doc | None, kind: Any, key: str, edge_type: Any, every: Any, priority: Any, *items: Any
    ) -> Edge:
        edge = Edge(key, _tok(kind), doc=str(doc) if doc else None)
        self._apply_edge_type(edge, edge_type)
        edge.interval = every
        edge.priority = priority
        self._apply_items(edge, items)
        return edge

    def shared_edge(self, doc: _Doc | None, key: str, edge_type: Any, *items: Any) -> Edge:
        edge = Edge(key, "shared_process", doc=str(doc) if doc else None)
        self._apply_edge_type(edge, edge_type)
        self._apply_items(edge, items)
        return edge

    def composite_edge(self, doc: _Doc | None, key: str, every: Any, address: Any, *items: Any) -> Edge:
        edge = Edge(key, "process", Address.from_any(_string(address) if address is not None else "local:Composite"))
        edge.doc = str(doc) if doc else None
        edge.interval = every
        edge.inner = Composite()
        self._apply_items(edge, items)
        return edge

    def _apply_edge_type(self, edge: Edge, edge_type: tuple[str, Any, Any]) -> None:
        label, name, address = edge_type
        if label == "shared_ref":
            edge.kind = "shared_process_ref"
            edge.extras["process_id"] = name
            return
        edge.iface_name = name
        decl = self.interfaces.get(name) if name is not None else None
        if name is not None and decl is None and name in self.imports:
            imported = Address("local", f"!{self.imports[name]}.{name}")
            decl = self.registry.lookup(imported) if self.registry is not None else None
            if decl is None:
                decl = InterfaceDecl(name, edge.kind, imported, module=self.imports[name])
        if address is None:
            edge.address = decl.address if decl is not None else None
        elif isinstance(address, Site):
            sort = address.sort if not _is_unsorted(address.sort) else _face_sort(decl)
            edge.address = Site(sort, address.default)
        else:
            edge.address = address
        if decl is not None and decl.module is None and (decl.inputs is not None or decl.outputs is not None):
            edge.ports = Face(
                dict(decl.inputs) if decl.inputs is not None else None,
                dict(decl.outputs) if decl.outputs is not None else None,
            )

    def _apply_items(self, edge: Edge, items: tuple[tuple[str, Any], ...]) -> None:
        for label, payload in items:
            if label == "config":
                edge.config.update(_plain(payload))
            elif label == "inputs":
                edge.inputs = payload
            elif label == "outputs":
                edge.outputs = payload
            elif label == "ports":
                edge.ports = payload
            elif label == "extra":
                edge.extras.update(payload)
            elif label == "bridge":
                edge.bridge = {k: wire_to_document(v) for k, v in payload.items()}
            elif label == "interface":
                edge.interface = payload
            elif label == "options":
                edge.config.update(payload)
            elif label == "inner":
                edge.inner = payload

    def typed_edge(self, name: Any, address: Any) -> tuple[str, str, Any]:
        return "typed", _tok(name), address

    def untyped_edge(self, address: Any) -> tuple[str, None, Any]:
        return "untyped", None, address

    def shared_ref(self, key: str) -> tuple[str, str, None]:
        return "shared_ref", key, None

    def address(self, item: Any) -> Any:
        if isinstance(item, Site):
            return item
        if isinstance(item, Token) and item.type == "PARAM":
            return ParamRef(_tok(item)[2:-1])
        return Address.from_any(_string(item))

    def every(self, value: Any) -> Any:
        return value

    def priority(self, value: Any) -> Any:
        return value

    def scalar(self, token: Any) -> Any:
        return ParamRef(_tok(token)[2:-1]) if token.type == "PARAM" else _number(token)

    def comp_item(self, item: Any) -> Any:
        return item

    def edge_item(self, item: Any) -> Any:
        return item

    def config_block(self, entries: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        return "config", entries

    def inputs_block(self, wires: dict[str, Wire]) -> tuple[str, dict[str, Wire]]:
        return "inputs", wires

    def outputs_block(self, wires: dict[str, Wire]) -> tuple[str, dict[str, Wire]]:
        return "outputs", wires

    def extra_block(self, entries: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        return "extra", entries

    def bridge_block(self, wires: dict[str, Wire]) -> tuple[str, dict[str, Wire]]:
        return "bridge", wires

    def interface_block(self, entries: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        return "interface", entries

    def options_block(self, entries: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        return "options", entries

    def inner_block(self, *decls: Any) -> tuple[str, Composite]:
        return "inner", self._composite(decls)

    def ports_block(self, inputs: Any, outputs: Any) -> tuple[str, Face]:
        return "ports", Face(inputs, outputs)

    def ports_inputs(self, *fields: tuple[str, ConfigField]) -> dict[str, TypeExpr]:
        return {k: f.type for k, f in fields if f.type is not None}

    def ports_outputs(self, *fields: tuple[str, ConfigField]) -> dict[str, TypeExpr]:
        return {k: f.type for k, f in fields if f.type is not None}

    def wireblock(self, *wires: Any) -> dict[str, Wire]:
        return {k: v for k, v in wires if k is not None} if wires and wires[0] is not None else {}

    def wire_path(self, key: str, path: Any) -> tuple[str, Path]:
        return key, parse_path(_tok(path))

    def wire_sub(self, key: str, wires: dict[str, Wire]) -> tuple[str, dict[str, Wire]]:
        return key, wires

    # --- values --------------------------------------------------------------------------------------------------

    def kvblock(self, *entries: Any) -> dict[str, Any]:
        return {k: v for k, v in entries if k is not None} if entries and entries[0] is not None else {}

    def kv(self, key: str, value: Any) -> tuple[str, Any]:
        return key, value

    def key(self, token: Any) -> str:
        return _string(token) if token.type == "STRING" else _tok(token)

    def number(self, token: Any) -> int | float:
        return _number(token)

    def string(self, token: Any) -> str:
        return _string(token)

    def true(self) -> bool:
        return True

    def false(self) -> bool:
        return False

    def null(self) -> None:
        return None

    def paramref(self, token: Any) -> ParamRef:
        return ParamRef(_tok(token)[2:-1])

    def site(self, default: Any, sort: TypeExpr | None) -> Site:
        return Site(sort if sort is not None else _UNSORTED, MISSING if default is None else default)

    def list_lit(self, *items: Any) -> list[Any]:
        return [] if items and items[0] is None and len(items) == 1 else list(items)

    def tuple_lit(self, *items: Any) -> tuple[Any, ...]:
        return () if items and items[0] is None and len(items) == 1 else tuple(items)

    def array_lit(self, data: Any, *options: Any) -> Any:
        opts = {_tok(options[i]): options[i + 1] for i in range(0, len(options), 2)}
        dtype = opts.get("dtype")
        if isinstance(data, ExternalRef):
            shape = tuple(int(s) for s in opts.get("shape", ())) or None
            return ExternalRef(data.path, "array", dtype=dtype, shape=shape)
        return np.asarray(data, dtype=dtype) if dtype else np.asarray(data)

    def file_lit(self, path: Any) -> ExternalRef:
        name = _string(path)
        return ExternalRef(name, "json" if name.endswith(".json") else "text")

    # --- types ---------------------------------------------------------------------------------------------------

    def type(self, *prims: TypeExpr) -> TypeExpr:
        return prims[0] if len(prims) == 1 else UnionType(list(prims))

    def named_type(self, name: Any, *rest: Any) -> TypeExpr:
        args: list[TypeExpr] = []
        units: str | None = None
        for item in rest:
            if isinstance(item, Group):
                args.insert(0, item)
            elif isinstance(item, Token) and item.type == "STRING":
                units = _string(item)
            elif item is not None:
                args.append(item)
        return Named(_tok(name), args, units=units)

    def shape(self, *dims: int | str) -> Group:
        return Group(list(dims))

    def number_arg(self, token: Any) -> TypeExpr:
        return Named(_tok(token))

    def type_arg(self, item: TypeExpr) -> TypeExpr:
        return item

    def dim(self, token: Any = None) -> int | str:
        if token is None:
            return "_"
        text = _tok(token)
        return int(text) if text.lstrip("-").isdigit() else text

    def link_type(self, inputs: Struct, outputs: Struct) -> TypeExpr:
        return Raw({"_type": "link", "_inputs": to_bigraph(inputs), "_outputs": to_bigraph(outputs)})

    def struct_type(self, *fields: tuple[str, ConfigField]) -> Struct:
        return Struct({k: f.type for k, f in fields if f.type is not None})

    def raw_type(self, token: Any) -> TypeExpr:
        text = _string(token)
        try:
            return Raw(json.loads(text))
        except ValueError:
            return Named(text)

    def type_prim(self, item: Any) -> Any:
        return item

    # --- helpers -------------------------------------------------------------------------------------------------

    def _substitute(self, composite: Composite) -> Composite:
        """`${name}` strings become ParamRefs once the params are known (reuses the reader's rule)."""
        for element in composite.children.values():
            if isinstance(element, Store) and element.value is not MISSING:
                element.value = self._reader.value(element.value)
            elif isinstance(element, Node):
                self._substitute(Composite(element.children))
            elif isinstance(element, Edge):
                element.config = self._reader.value(element.config)
                if isinstance(element.interval, str):
                    element.interval = self._reader.value(element.interval)
                if element.inner is not None:
                    self._substitute(element.inner)
        return composite


_UNSORTED = Named("__unsorted__")


def _plain(value: Any) -> Any:
    """Config values keep sites as plain dicts, as the reader does."""
    if isinstance(value, Site):
        sort = value.sort if not _is_unsorted(value.sort) else Named("node")
        node: dict[str, Any] = {"_type": "site", "_sort": to_bigraph(sort)}
        if value.default is not MISSING:
            node["_default"] = _plain(value.default)
        return node
    if isinstance(value, dict):
        return {k: _plain(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_plain(v) for v in value]
    if isinstance(value, tuple):
        return tuple(_plain(v) for v in value)
    return value


def _is_unsorted(sort: TypeExpr) -> bool:
    return isinstance(sort, Named) and sort.name == "__unsorted__"


def _face_sort(decl: InterfaceDecl | None) -> TypeExpr:
    face: dict[str, Any] = {"_type": "link"}
    if decl is not None and decl.inputs is not None:
        face["_inputs"] = {k: to_bigraph(v) for k, v in decl.inputs.items()}
    if decl is not None and decl.outputs is not None:
        face["_outputs"] = {k: to_bigraph(v) for k, v in decl.outputs.items()}
    return Raw(face)
