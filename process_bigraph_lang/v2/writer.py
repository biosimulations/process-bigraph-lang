"""
The v2 model -> documents.

`write_document` produces the process-bigraph 1.x `{"schema", "state"}` document (plus composite options
at the top level); `write_composite_spec` produces a CompositeSpec mapping ready for `yaml.safe_dump`.
Both are the exact inverse of the reader for every form it accepts.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from process_bigraph_lang.v2.model import (
    Address,
    Composite,
    Document,
    Edge,
    ExternalRef,
    Node,
    Param,
    ParamRef,
    Site,
    Store,
)
from process_bigraph_lang.v2.paths import wire_to_document
from process_bigraph_lang.v2.types import to_bigraph
from process_bigraph_lang.v2.values import MISSING

AssetLoader = Callable[[ExternalRef], Any]


def write_document(doc: Document, *, assets: AssetLoader | None = None) -> dict[str, Any]:
    """The `{"schema", "state", **options}` document. `assets` loads values the printer externalized."""
    schema, state = _composite(doc.root, assets)
    out: dict[str, Any] = {"schema": schema, "state": state}
    out.update(doc.options)
    return out


def write_composite_spec(doc: Document, *, assets: AssetLoader | None = None) -> dict[str, Any]:
    """A CompositeSpec mapping: `name`, `description`, `tags`, `requires`, `parameters`, `emitters`, `schema`, `state`."""
    out: dict[str, Any] = {}
    if doc.name:
        out["name"] = doc.name
    if doc.description:
        out["description"] = doc.description
    if doc.tags:
        out["tags"] = list(doc.tags)
    if doc.requires:
        out["requires"] = dict(doc.requires)
    if doc.params:
        out["parameters"] = {p.name: _param(p) for p in doc.params}
    if doc.emitters:
        out["emitters"] = [
            {
                "address": str(e.address),
                "paths": [p.to_slash() for p in e.paths],
                **({"config": _value(e.config, assets)} if e.config else {}),
            }
            for e in doc.emitters
        ]
    document = write_document(doc, assets=assets)
    if document["schema"]:
        out["schema"] = document["schema"]
    out["state"] = document["state"]
    for key, value in doc.options.items():
        out[key] = value
    out.update(doc.extras)
    return out


def _param(param: Param) -> dict[str, Any]:
    decl: dict[str, Any] = {}
    if param.type is not None:
        decl["type"] = to_bigraph(param.type)
    if param.default is not MISSING:
        decl["default"] = param.default
    if param.description:
        decl["description"] = param.description
    if param.choices is not None:
        decl["choices"] = list(param.choices)
    return decl


def _composite(composite: Composite, assets: AssetLoader | None) -> tuple[dict[str, Any], dict[str, Any]]:
    schema: dict[str, Any] = {}
    state: dict[str, Any] = {}
    for key, element in composite.children.items():
        if isinstance(element, Store):
            if element.site is not None:
                state[key] = _site(element.site, assets)  # an open store has no schema entry (process-bigraph#213)
                continue
            if element.type is not None:
                schema[key] = to_bigraph(element.type)
            if element.value is not MISSING:
                state[key] = _value(element.value, assets)
        elif isinstance(element, Node):
            child_schema, child_state = _composite(Composite(element.children), assets)
            if element.type is not None:
                schema[key] = to_bigraph(element.type)
            elif child_schema:
                schema[key] = child_schema
            state[key] = child_state
        else:
            state[key] = _edge(element, assets)
    schema.update(composite.schema_extras)
    return schema, state


def _edge(edge: Edge, assets: AssetLoader | None) -> dict[str, Any]:
    node: dict[str, Any] = {"_type": edge.kind}
    if edge.ports is not None:
        if edge.ports.inputs is not None:
            node["_inputs"] = {k: to_bigraph(v) for k, v in edge.ports.inputs.items()}
        if edge.ports.outputs is not None:
            node["_outputs"] = {k: to_bigraph(v) for k, v in edge.ports.outputs.items()}
    if edge.address is not None:
        node["address"] = _address(edge.address, assets)
    config: dict[str, Any] = {}
    if edge.inner is not None:
        inner_schema, inner_state = _composite(edge.inner, assets)
        config["state"] = inner_state
        if inner_schema:
            config["schema"] = inner_schema
    if edge.bridge is not None:
        config["bridge"] = edge.bridge
    if edge.interface is not None:
        config["interface"] = edge.interface
    config.update(edge.config)
    if config:
        node["config"] = _value(config, assets)
    if edge.inputs:
        node["inputs"] = {k: wire_to_document(w) for k, w in edge.inputs.items()}
    if edge.outputs:
        node["outputs"] = {k: wire_to_document(w) for k, w in edge.outputs.items()}
    if edge.interval is not None:
        node["interval"] = _value(edge.interval, assets)
    if edge.priority is not None:
        node["priority"] = edge.priority
    for key, value in edge.extras.items():
        node[key] = _value(value, assets)
    return node


def _address(address: Address | Site | ParamRef, assets: AssetLoader | None) -> Any:
    if isinstance(address, Site):
        return _site(address, assets)
    if isinstance(address, ParamRef):
        return _value(address, assets)
    return str(address)


def _site(site: Site, assets: AssetLoader | None) -> dict[str, Any]:
    node: dict[str, Any] = {"_type": "site", "_sort": to_bigraph(site.sort)}
    if site.default is not MISSING:
        node["_default"] = _value(site.default, assets)
    return node


def _value(value: Any, assets: AssetLoader | None) -> Any:
    if isinstance(value, ParamRef):
        return value.template if value.template is not None else "${" + value.name + "}"
    if isinstance(value, ExternalRef):
        if assets is None:
            raise ValueError(f"value kept in sidecar '{value.path}' but no asset loader was given")
        return assets(value)
    if isinstance(value, Site):
        return _site(value, assets)
    if isinstance(value, dict):
        return {k: _value(v, assets) for k, v in value.items()}
    if isinstance(value, list):
        return [_value(v, assets) for v in value]
    if isinstance(value, tuple):
        return tuple(_value(v, assets) for v in value)
    return value
