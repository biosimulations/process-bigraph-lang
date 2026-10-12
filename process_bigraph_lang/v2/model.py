"""
The v2 object model: what a `.pblang` v2 module denotes (see `docs/v2/design.md`, section 1).

The model is a tree of stores, plain nodes and edges, plus the module-level parameters, emitter
declarations and composite options. It is the pivot of the round trip: documents and CompositeSpec
mappings are read into it, and text, documents and mappings are written from it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

from process_bigraph_lang.v2.paths import Path, Wire
from process_bigraph_lang.v2.types import TypeExpr
from process_bigraph_lang.v2.values import MISSING


@dataclass
class Address:
    """`protocol:data`, e.g. `local:!pkg.mod.Class` (portable import) or `local:RAMEmitter` (registry name)."""

    protocol: str
    data: str

    @classmethod
    def from_any(cls, address: Any) -> Address:
        if isinstance(address, Address):
            return address
        if isinstance(address, dict):
            return cls(str(address["protocol"]), str(address["data"]))
        if isinstance(address, str):
            protocol, sep, data = address.partition(":")
            return cls(protocol, data) if sep else cls("local", address)
        raise TypeError(f"not an address: {address!r}")

    def __str__(self) -> str:
        return f"{self.protocol}:{self.data}"

    @property
    def is_import(self) -> bool:
        return self.protocol == "local" and self.data.startswith("!")

    @property
    def short_name(self) -> str:
        return self.data.lstrip("!").rsplit(".", 1)[-1]

    @property
    def module(self) -> str | None:
        if not self.is_import or "." not in self.data:
            return None
        return self.data[1:].rsplit(".", 1)[0]

    @property
    def is_composite(self) -> bool:
        return self.protocol == "local" and self.short_name == "Composite"


@dataclass
class ParamRef:
    """A reference to a module parameter: `${dt}` on its own, or embedded in a string template."""

    name: str
    template: str | None = None


@dataclass
class ExternalRef:
    """A large value kept in a sidecar file (`file("…")` / `array(file("…"))`)."""

    path: str
    kind: Literal["array", "text", "json"]
    dtype: str | None = None
    shape: tuple[int, ...] | None = None


@dataclass
class Site:
    """An open value: `?`, `?(default)`, `? as sort`. Its sort is a type, or a link face for address/model sites."""

    sort: TypeExpr
    default: Any = MISSING


@dataclass
class Face:
    """Port types, as `_inputs`/`_outputs` on an edge or as an interface declaration. `None` = not declared."""

    inputs: dict[str, TypeExpr] | None = None
    outputs: dict[str, TypeExpr] | None = None


@dataclass
class ConfigField:
    """One entry of an interface's `config { name: type = default; }`."""

    type: TypeExpr | None = None
    default: Any = MISSING
    doc: str | None = None


@dataclass
class InterfaceDecl:
    """
    A process/step interface (`process Name at "…" { config {…} inputs {…} outputs {…} }`), as found in a
    generated interface file, a manifest, or derived from an edge's `_inputs`/`_outputs`.
    """

    name: str
    kind: str  # process | step | adapter
    address: Address | None = None
    module: str | None = None  # the module an `import` line names; None for an inline declaration
    config: dict[str, ConfigField] = field(default_factory=dict)
    inputs: dict[str, TypeExpr] | None = None
    outputs: dict[str, TypeExpr] | None = None
    doc: str | None = None
    dynamic_ports: bool = False  # inputs()/outputs() could not be evaluated without an instance

    @property
    def face(self) -> Face:
        return Face(self.inputs, self.outputs)


@dataclass
class Store:
    """A leaf of the tree: a typed value, or an open site. `value is MISSING` means declared only."""

    name: str
    type: TypeExpr | None = None
    value: Any = MISSING
    site: Site | None = None
    doc: str | None = None


@dataclass
class Node:
    """A plain subtree (`node x { … }`), optionally typed (a map of edges, a struct)."""

    name: str
    children: dict[str, Element] = field(default_factory=dict)
    type: TypeExpr | None = None
    doc: str | None = None


@dataclass
class Edge:
    """A step or process (or a nested composite, or a shared process) at a position in the tree."""

    name: str
    kind: str  # process | step | shared_process | shared_process_ref
    address: Address | Site | ParamRef | None = None
    config: dict[str, Any] = field(default_factory=dict)
    inputs: dict[str, Wire] = field(default_factory=dict)
    outputs: dict[str, Wire] = field(default_factory=dict)
    interval: float | ParamRef | None = None
    priority: float | None = None
    triggers: list[Path] | None = None
    ports: Face | None = None
    inner: Composite | None = None  # a nested composite: `config.state` / `config.schema`
    bridge: dict[str, Any] | None = None  # `config.bridge` of a nested composite
    interface: dict[str, Any] | None = None  # `config.interface` of a nested composite
    extras: dict[str, Any] = field(default_factory=dict)  # any other node keys, verbatim
    doc: str | None = None

    @property
    def is_composite(self) -> bool:
        return isinstance(self.address, Address) and self.address.is_composite


Element = Store | Node | Edge


@dataclass
class Composite:
    """The children of the root, or of a nested composite. Insertion order is source order."""

    children: dict[str, Element] = field(default_factory=dict)
    schema_extras: dict[str, Any] = field(default_factory=dict)  # schema entries that classify as nothing


@dataclass
class Param:
    """A module parameter (`param dt: float = 0.01;`), the DSL form of a CompositeSpec parameter."""

    name: str
    type: TypeExpr | None = None
    default: Any = MISSING
    description: str = ""
    choices: list[Any] | None = None


@dataclass
class Emitter:
    """A CompositeSpec `emitters:` declaration (`emit parquet { a, b.c }`)."""

    address: Address
    paths: list[Path] = field(default_factory=list)
    config: dict[str, Any] = field(default_factory=dict)


@dataclass
class Document:
    """A whole v2 module."""

    root: Composite = field(default_factory=Composite)
    name: str | None = None
    description: str = ""
    tags: list[str] = field(default_factory=list)
    requires: dict[str, Any] = field(default_factory=dict)
    params: list[Param] = field(default_factory=list)
    emitters: list[Emitter] = field(default_factory=list)
    options: dict[str, Any] = field(default_factory=dict)
    source: Literal["authoring", "saved", "composite_spec"] = "authoring"
    extras: dict[str, Any] = field(default_factory=dict)  # unknown top-level / CompositeSpec keys

    @property
    def param_names(self) -> set[str]:
        return {p.name for p in self.params}
