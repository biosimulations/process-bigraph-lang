"""
Read `.pbl` text through the Langium grammar: the JSON AST the DSL CLI writes, bound to the v2 model.

`read_langium(path)` and `read_text(text)` run the Langium CLI (`cli-native generate`, the same binary v1 uses,
built once by Deno at wheel-build time; or `node dsl/bin/cli.js` in a development checkout) and bind the JSON it
writes into a `Document`. The grammar lives in `dsl/src/language/pblang-v2.langium`; there is no second parser.
"""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import numpy as np

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
from process_bigraph_lang.v2.paths import Path as WirePath
from process_bigraph_lang.v2.paths import Wire, wire_to_document
from process_bigraph_lang.v2.printer import EMITTER_ALIASES
from process_bigraph_lang.v2.reader import _Reader
from process_bigraph_lang.v2.types import Group, Named, Raw, Struct, TypeExpr, UnionType, to_bigraph
from process_bigraph_lang.v2.values import MISSING

_ROOT = Path(__file__).resolve().parent.parent
_ALIAS_ADDRESSES = {alias: f"local:{name}" for name, alias in EMITTER_ALIASES.items()}


def langium_cli() -> list[str] | None:
    """The command that runs the DSL CLI, or None when neither the native binary nor a built checkout exists."""
    for candidate in (_ROOT / "bin").glob("cli-native*"):
        return [str(candidate)]
    script = _ROOT.parent / "dsl" / "bin" / "cli.js"
    if script.exists() and (_ROOT.parent / "dsl" / "out").exists():
        return ["node", str(script)]
    return None


def read_langium(path: str | os.PathLike[str], *, registry: InterfaceRegistry | None = None) -> Document:
    """Parse a `.pbl` file with the Langium grammar and bind it to the v2 model."""
    return bind_langium(generate_ast(path), registry=registry)


def read_text(text: str, *, registry: InterfaceRegistry | None = None) -> Document:
    """Parse v2 text (written to a temporary `.pbl` file for the CLI)."""
    with tempfile.TemporaryDirectory() as tmp:
        source = Path(tmp) / "document.pbl"
        source.write_text(text, encoding="utf-8")
        return read_langium(source, registry=registry)


def generate_ast(path: str | os.PathLike[str]) -> dict[str, Any]:
    """The JSON AST of a `.pbl` file, as `cli-native generate` writes it (`$type`, `$ref`, `$refText` kept)."""
    command = langium_cli()
    if command is None:
        raise RuntimeError("no Langium CLI: build dsl/ (npm run build) or install the cli-native binary")
    source = Path(path).resolve()
    with tempfile.TemporaryDirectory() as tmp:
        result = subprocess.run(
            [*command, "generate", str(source), "--destination", tmp, "--lenient"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError(f"Langium CLI failed on {source}: {result.stderr.strip() or result.stdout.strip()}")
        produced = next(Path(tmp).glob("*.json"))
        loaded: dict[str, Any] = json.loads(produced.read_text(encoding="utf-8"))
        return loaded


def bind_langium(ast: dict[str, Any], *, registry: InterfaceRegistry | None = None) -> Document:
    """Bind a Langium JSON AST (`V2Module`) to a `Document`."""
    if ast.get("$type") != "V2Module":
        raise ValueError(f"not a v2 module: {ast.get('$type')}")
    return _LangiumBinder(registry).module(ast)


def _doc(node: dict[str, Any]) -> str | None:
    docs = node.get("docs") or []
    return " ".join(str(d)[3:].strip() for d in docs) if docs else None


def _ref_name(ref: Any) -> str | None:
    return ref.get("$refText") if isinstance(ref, dict) else None


class _Builder:
    """Builds the model from parsed pieces: edge heads and items, stores, meta, late `${param}` substitution."""

    def __init__(self, registry: InterfaceRegistry | None = None) -> None:
        self.registry = registry
        self.document = Document()
        self.imports: dict[str, str] = {}  # interface name -> module
        self.interfaces: dict[str, InterfaceDecl] = {}
        self._reader = _Reader(saved=False, params=set())

    def meta(self, entries: dict[str, Any]) -> None:
        entries = dict(entries)
        self.document.tags = list(entries.pop("tags", []) or [])
        self.document.requires = dict(entries.pop("requires", {}) or {})
        self.document.extras.update(entries)

    def options(self, entries: dict[str, Any]) -> None:
        self.document.options.update(entries)

    def store(self, doc: str | None, key: str, type_: TypeExpr | None, value: Any) -> Store:
        store = Store(key, type=type_, doc=doc)
        if isinstance(value, Site) and value.default is MISSING and type_ is not None and _is_unsorted(value.sort):
            store.site = Site(type_, MISSING)  # `store m : ODEModel = ?;` is a model site sorted by its type
            return store
        if isinstance(value, Site):
            sort = value.sort if not _is_unsorted(value.sort) else (type_ or Named("node"))
            store.site = Site(sort, value.default)
        elif value is not None:
            store.value = value
        return store

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


def _is_unsorted(sort: TypeExpr) -> bool:
    return isinstance(sort, Named) and sort.name == "__unsorted__"


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


def _face_sort(decl: InterfaceDecl | None) -> TypeExpr:
    face: dict[str, Any] = {"_type": "link"}
    if decl is not None and decl.inputs is not None:
        face["_inputs"] = {k: to_bigraph(v) for k, v in decl.inputs.items()}
    if decl is not None and decl.outputs is not None:
        face["_outputs"] = {k: to_bigraph(v) for k, v in decl.outputs.items()}
    return Raw(face)


class _LangiumBinder:
    """Walks the Langium JSON AST and builds the model through `_Builder`."""

    def __init__(self, registry: InterfaceRegistry | None) -> None:
        self.builder = _Builder(registry)
        self.document = self.builder.document

    # --- module --------------------------------------------------------------------------------------------------

    def module(self, ast: dict[str, Any]) -> Document:
        self.document.module = ast.get("name")
        for statement in ast.get("statements") or []:
            body = statement["body"]
            doc = _doc(statement)
            kind = body["$type"]
            if kind == "V2Import":
                self.import_(body)
            elif kind == "V2Param":
                self.param(body, doc)
            elif kind == "V2Meta":
                self.builder.meta(self.dict_(body["block"]))
            elif kind == "V2Options":
                self.builder.options(self.dict_(body["block"]))
            elif kind == "V2Interface":
                self.interface(body, doc)
            elif kind == "V2ModelDecl":
                self.model(body, doc)
            elif kind == "V2Composite":
                self.document.name = body.get("name")
                self.document.description = doc or ""
                self.document.root = self.composite(body.get("decls") or [])
            elif kind == "V2Emit":
                self.emit(body)
        names = self.document.param_names
        if names:
            self.builder._reader.params = names
            self.builder._substitute(self.document.root)
        return self.document

    def import_(self, node: dict[str, Any]) -> None:
        if node.get("modulePath"):
            module = str(node["modulePath"])[:-2]  # strip the `.{`
            for imported in node.get("names") or []:
                self.builder.imports[imported["name"]] = module

    def param(self, node: dict[str, Any], doc: str | None) -> None:
        default = self.value(node["default"]) if node.get("default") is not None else MISSING
        self.document.params.append(
            Param(
                node["name"],
                type=self.type_(node["type"]),
                default=MISSING if isinstance(default, Site) else default,
                description=doc or "",
                choices=list(self.value(node["choices"])) if node.get("choices") is not None else None,
            )
        )

    def emit(self, node: dict[str, Any]) -> None:
        if node.get("address") is not None:
            address = Address.from_any(node["address"])
        else:
            alias = node["alias"]
            address = Address.from_any(_ALIAS_ADDRESSES.get(alias, f"local:{alias}"))
        paths = [self.path(p) for p in node.get("paths") or []]
        config = self.dict_(node["config"]) if node.get("config") is not None else {}
        self.document.emitters.append(Emitter(address, paths, config))

    # --- interfaces and models ---------------------------------------------------------------------------------

    def interface(self, node: dict[str, Any], doc: str | None) -> None:
        decl = InterfaceDecl(
            node["name"],
            node["kind"],
            address=Address.from_any(node["address"]) if node.get("address") else None,
            doc=doc,
        )
        decl.config = {f["name"]: self.field(f) for f in node.get("config") or []}
        for label in ("inputs", "outputs"):
            face = node.get(label)
            if face is None:
                continue
            if face.get("open"):
                decl.dynamic_ports = True
            else:
                ports = {f["name"]: self.field(f) for f in face.get("fields") or []}
                setattr(decl, label, {k: f.type for k, f in ports.items() if f.type is not None})
        self.builder.interfaces[decl.name] = decl
        self.document.interfaces.append(decl)

    def model(self, node: dict[str, Any], doc: str | None) -> None:
        decl = ModelDecl(node["name"], node.get("source"), doc=doc)
        for item in node.get("items") or []:
            kind = item["$type"]
            if kind == "V2ModelTime":
                decl.time_units = item["units"]
            elif kind == "V2ModelMeta":
                decl.meta = self.dict_(item["block"])
            else:
                decl.block(item["kind"]).update({f["name"]: self.field(f) for f in item.get("fields") or []})
                if item.get("open"):
                    decl.open_blocks.add(item["kind"])
        self.document.models.append(decl)

    def field(self, node: dict[str, Any]) -> ConfigField:
        default = self.value(node["default"]) if node.get("default") is not None else MISSING
        return ConfigField(self.type_(node["type"]), default, _doc(node))

    # --- tree ----------------------------------------------------------------------------------------------------

    def composite(self, decls: list[dict[str, Any]]) -> Composite:
        composite = Composite()
        for decl in decls:
            body = decl["body"]
            doc = _doc(decl)
            kind = body["$type"]
            element: Element | None = None
            if kind == "V2Store":
                element = self.store(body, doc)
            elif kind == "V2Node":
                element = Node(body["name"], self.composite(body.get("decls") or []).children, self.opt_type(body), doc)
            elif kind in ("V2PlainEdge", "V2SharedEdge", "V2CompositeEdge"):
                element = self.edge(body, doc)
            elif kind == "V2SchemaBlock":
                composite.schema_extras.update(self.dict_(body["block"]))
            if element is not None:
                composite.children[element.name] = element
        return composite

    def store(self, node: dict[str, Any], doc: str | None) -> Store:
        type_ = self.opt_type(node)
        value = self.value(node["value"]) if node.get("value") is not None else None
        return self.builder.store(doc, node["name"], type_, value)

    def edge(self, node: dict[str, Any], doc: str | None) -> Edge:
        kind = node["$type"]
        if kind == "V2CompositeEdge":
            address = Address.from_any(node["address"] if node.get("address") else "local:Composite")
            edge = Edge(node["name"], "process", address, doc=doc)
            edge.interval = self.scalar(node.get("interval"))
            edge.inner = Composite()
        else:
            edge = Edge(node["name"], "shared_process" if kind == "V2SharedEdge" else node["kind"], doc=doc)
            self.builder._apply_edge_type(edge, self.head(node["head"]))
            if kind == "V2PlainEdge":
                edge.interval = self.scalar(node.get("interval"))
                edge.priority = self.scalar(node.get("priority"))
        self.builder._apply_items(edge, tuple(self.item(i) for i in node.get("items") or []))
        return edge

    def head(self, node: dict[str, Any]) -> tuple[str, Any, Any]:
        if node.get("sharedRef") is not None:
            return "shared_ref", node["sharedRef"], None
        address = self.address(node.get("address"))
        iface = _ref_name(node.get("iface"))
        if iface is not None:
            return "typed", iface, address
        return "untyped", None, address

    def address(self, node: dict[str, Any] | None) -> Any:
        if node is None:
            return None
        if node.get("site") is not None:
            return self.value(node["site"])
        if node.get("param") is not None:
            return ParamRef(str(node["param"])[2:-1])
        return Address.from_any(node["literal"])

    def scalar(self, node: dict[str, Any] | None) -> Any:
        if node is None:
            return None
        if node.get("param") is not None:
            return ParamRef(str(node["param"])[2:-1])
        if node.get("float") is not None:
            return float(node["float"])
        return int(node["int"])

    def item(self, node: dict[str, Any]) -> tuple[str, Any]:
        kind = node["$type"]
        if kind == "V2ConfigBlock":
            return "config", self.dict_(node["block"])
        if kind == "V2InputsBlock":
            return "inputs", self.wires(node["block"])
        if kind == "V2OutputsBlock":
            return "outputs", self.wires(node["block"])
        if kind == "V2PortsBlock":
            inputs = {f["name"]: self.field(f).type for f in node["inputs"]} if node.get("inputs") is not None else None
            outputs = (
                {f["name"]: self.field(f).type for f in node["outputs"]} if node.get("outputs") is not None else None
            )
            return "ports", Face(
                {k: v for k, v in inputs.items() if v is not None} if inputs is not None else None,
                {k: v for k, v in outputs.items() if v is not None} if outputs is not None else None,
            )
        if kind == "V2ExtraBlock":
            return "extra", self.dict_(node["block"])
        if kind == "V2BridgeBlock":
            return "bridge", self.wires(node["block"])
        if kind == "V2InterfaceBlock":
            return "interface", self.dict_(node["block"])
        if kind == "V2OptionsBlock":
            return "options", self.dict_(node["block"])
        if kind == "V2InnerBlock":
            return "inner", self.composite(node.get("decls") or [])
        raise ValueError(f"unexpected edge item {kind}")

    def wires(self, block: dict[str, Any]) -> dict[str, Wire]:
        out: dict[str, Wire] = {}
        for wire in block.get("wires") or []:
            out[wire["port"]] = self.path(wire["path"]) if wire.get("path") is not None else self.wires(wire["block"])
        return out

    def path(self, node: dict[str, Any]) -> WirePath:
        steps: list[str | int] = []
        for segment in node.get("segments") or []:
            if segment["$type"] == "V2Index":
                steps.append(int(segment["index"]))
            elif segment.get("up"):
                steps.append("..")
            elif segment.get("star"):
                steps.append("*")
            else:
                steps.append(segment["key"])
        return WirePath(steps)

    # --- values --------------------------------------------------------------------------------------------------

    def dict_(self, block: dict[str, Any]) -> dict[str, Any]:
        return {entry["key"]: self.value(entry["value"]) for entry in block.get("entries") or []}

    def value(self, node: dict[str, Any]) -> Any:
        kind = node["$type"]
        if kind == "V2IntLiteral":
            return int(node["value"])
        if kind == "V2FloatLiteral":
            return float(node["value"])
        if kind == "V2StringLiteral":
            return node["value"]
        if kind == "V2BoolLiteral":
            return node["value"] == "true"
        if kind == "V2NullLiteral":
            return None
        if kind == "V2ParamRef":
            return ParamRef(str(node["value"])[2:-1])
        if kind == "V2SiteValue":
            default = self.value(node["default"]) if node.get("default") is not None else MISSING
            sort = self.type_(node["sort"]) if node.get("sort") is not None else _UNSORTED
            return Site(sort, default)
        if kind == "V2DictLiteral":
            return self.dict_(node)
        if kind == "V2ListLiteral":
            return [self.value(v) for v in node.get("items") or []]
        if kind == "V2TupleLiteral":
            return tuple(self.value(v) for v in node.get("items") or [])
        if kind == "V2ArrayLiteral":
            options = {e["key"]: self.value(e["value"]) for e in node.get("options") or []}
            data = self.value(node["data"])
            if isinstance(data, ExternalRef):
                shape = tuple(int(s) for s in options.get("shape", ())) or None
                return ExternalRef(data.path, "array", dtype=options.get("dtype"), shape=shape)
            return np.asarray(data, dtype=options.get("dtype")) if options.get("dtype") else np.asarray(data)
        if kind == "V2FileLiteral":
            path = node["path"]
            return ExternalRef(path, "json" if path.endswith(".json") else "text")
        if kind == "V2ModelRef":
            return ModelRef(_ref_name(node.get("model")) or "")
        raise ValueError(f"unexpected value {kind}")

    # --- types ---------------------------------------------------------------------------------------------------

    def opt_type(self, node: dict[str, Any]) -> TypeExpr | None:
        return self.type_(node["type"]) if node.get("type") is not None else None

    def type_(self, node: dict[str, Any]) -> TypeExpr:
        options = [self.primary(p) for p in node.get("options") or []]
        return options[0] if len(options) == 1 else UnionType(options)

    def primary(self, node: dict[str, Any]) -> TypeExpr:
        kind = node["$type"]
        if kind == "V2NamedType":
            args: list[TypeExpr] = []
            dims = node.get("dims") or []
            if dims:
                args.append(
                    Group([int(d["size"]) if d.get("size") is not None else str(d.get("name", "_")) for d in dims])
                )
            for arg in node.get("args") or []:
                if arg.get("type") is not None:
                    args.append(self.type_(arg["type"]))
                else:
                    number = arg.get("int") if arg.get("int") is not None else arg.get("float")
                    args.append(Named(str(number)))
            return Named(node["name"], args, units=node.get("units"))
        if kind == "V2LinkType":
            return Raw({
                "_type": "link",
                "_inputs": to_bigraph(self.struct(node["inputs"])),
                "_outputs": to_bigraph(self.struct(node["outputs"])),
            })
        if kind == "V2StructType":
            return self.struct(node)
        text = node["raw"]
        try:
            return Raw(json.loads(text))
        except ValueError:
            return Named(text)

    def struct(self, node: dict[str, Any]) -> Struct:
        fields = {f["name"]: self.field(f) for f in node.get("fields") or []}
        return Struct({k: f.type for k, f in fields.items() if f.type is not None})


__all__ = ["bind_langium", "generate_ast", "langium_cli", "read_langium", "read_text"]
