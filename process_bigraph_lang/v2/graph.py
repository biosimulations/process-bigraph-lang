"""
A wiring graph from a document and interface declarations alone: what a viewer like loom needs, without
importing any process code.

`document_graph` returns plain JSON: `nodes` (edges of the composite with their interface, config keys, port
types and docs), `stores` (declared or merely wired), `edges` (one per wired port, resolved to an absolute store
path) and, for nested composites, the inner graph under `children`. Port types come from the node's own
`_inputs`/`_outputs` when present, else from the registry's declaration for its address.
"""

from __future__ import annotations

from typing import Any

from process_bigraph_lang.v2.interfaces import InterfaceRegistry
from process_bigraph_lang.v2.model import Address, Composite, Edge, InterfaceDecl, Node, Site, Store
from process_bigraph_lang.v2.paths import Path, Wire
from process_bigraph_lang.v2.types import TypeExpr, to_surface
from process_bigraph_lang.v2.values import MISSING


def document_graph(doc: Any, registry: InterfaceRegistry | None = None) -> dict[str, Any]:
    """The graph of a `Document` (or of a `Composite`): nodes, stores, edges, nested children."""
    composite = doc.root if hasattr(doc, "root") else doc
    return _Grapher(registry).composite(composite)


class _Grapher:
    def __init__(self, registry: InterfaceRegistry | None) -> None:
        self.registry = registry

    def composite(self, composite: Composite) -> dict[str, Any]:
        index: dict[str, Store | Node | Edge] = {}
        self.index(composite, (), index)
        stores: dict[str, dict[str, Any]] = {}
        nodes: list[dict[str, Any]] = []
        edges: list[dict[str, Any]] = []
        for path, element in index.items():
            if isinstance(element, Store):
                stores[path] = {
                    "id": path,
                    "type": _type_text(element.type or (element.site.sort if element.site else None)),
                    "declared": True,
                    "open": element.site is not None,
                }
            elif isinstance(element, Node) and not any(isinstance(c, Edge) for c in element.children.values()):
                stores.setdefault(path, {"id": path, "type": _type_text(element.type), "declared": True, "open": False})
        for path, element in index.items():
            if not isinstance(element, Edge):
                continue
            decl = self.declaration(element)
            node = self.node(path, element, decl)
            nodes.append(node)
            parent = path.rsplit("/", 1)[0] if "/" in path else ""
            for direction, wires in (("input", element.inputs), ("output", element.outputs)):
                ports = node["ports"][direction + "s"]
                for port, wire in wires.items():
                    for sub_port, target in _flatten(port, wire):
                        store_id = _resolve(parent, target)
                        if store_id is not None and store_id not in stores:
                            stores[store_id] = {"id": store_id, "type": None, "declared": False, "open": False}
                        edges.append({
                            "node": path,
                            "port": sub_port,
                            "store": store_id,
                            "direction": direction,
                            "type": (ports or {}).get(port),
                        })
            if element.inner is not None:
                node["children"] = self.composite(element.inner)
        return {"nodes": nodes, "stores": list(stores.values()), "edges": edges}

    def index(self, composite: Composite, path: tuple[str, ...], index: dict[str, Store | Node | Edge]) -> None:
        for key, element in composite.children.items():
            here = (*path, key)
            index["/".join(here)] = element
            if isinstance(element, Node):
                self.index(Composite(element.children), here, index)

    def declaration(self, edge: Edge) -> InterfaceDecl | None:
        if self.registry is None or not isinstance(edge.address, Address) or edge.address.is_composite:
            return None
        return self.registry.lookup(edge.address)

    def node(self, path: str, edge: Edge, decl: InterfaceDecl | None) -> dict[str, Any]:
        inputs = (
            edge.ports.inputs
            if edge.ports is not None and edge.ports.inputs is not None
            else (decl.inputs if decl else None)
        )
        outputs = (
            edge.ports.outputs
            if edge.ports is not None and edge.ports.outputs is not None
            else (decl.outputs if decl else None)
        )
        address: Any = (
            str(edge.address)
            if isinstance(edge.address, Address)
            else ("?" if isinstance(edge.address, Site) else None)
        )
        return {
            "id": path,
            "kind": "composite" if edge.is_composite else edge.kind,
            "interface": decl.name if decl else None,
            "address": address,
            "interval": edge.interval if not isinstance(edge.interval, (dict, list)) else None,
            "config_keys": sorted(edge.config),
            "ports": {"inputs": _ports_text(inputs), "outputs": _ports_text(outputs)},
            "dynamic_ports": bool(decl.dynamic_ports) if decl else False,
            "doc": decl.doc if decl else None,
        }


def _flatten(port: str, wire: Wire) -> list[tuple[str, Path]]:
    if isinstance(wire, dict):
        return [
            (f"{port}/{sub}", target)
            for sub_port, sub_wire in wire.items()
            for sub, target in _flatten(sub_port, sub_wire)
        ]
    return [(port, wire)]


def _resolve(parent: str, path: Path) -> str | None:
    absolute = [p for p in parent.split("/") if p]
    for step in path.steps:
        if step == "..":
            if not absolute:
                return None
            absolute.pop()
        elif step == "*":
            return None
        elif isinstance(step, int):
            absolute.append(f"[{step}]")
        else:
            absolute.append(step)
    return "/".join(absolute)


def _ports_text(ports: dict[str, TypeExpr] | None) -> dict[str, str] | None:
    if ports is None:
        return None
    return {k: to_surface(v) for k, v in ports.items()}


def _type_text(expr: TypeExpr | None) -> str | None:
    return to_surface(expr) if expr is not None and expr is not MISSING else None
