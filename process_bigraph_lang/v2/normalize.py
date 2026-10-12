"""
Equivalence of composite documents modulo representation.

Two documents are equivalent when they realize the same composite. `normalize_document` rewrites a document
into one canonical shape: types are pushed through bigraph-schema (`core.access` + `core.render(defaults=True)`),
addresses become `protocol:data` strings, wires become lists, tuples and arrays become lists, runtime keys
(`instance`, `_contract`, the root `global_time`) are dropped, and the edge entries of the schema half are folded
into the state half. `equivalent` compares two normalized documents; `diff_documents` explains a difference.
"""

from __future__ import annotations

import difflib
import json
import math
import re
from typing import Any

import numpy as np

from process_bigraph_lang.v2.values import COMPOSITE_OPTION_KEYS, EDGE_KINDS, RUNTIME_EDGE_KEYS, is_edge_node, is_site

_EdgeTable = dict[tuple[str, ...], dict[str, Any]]


def normalize_document(doc: dict[str, Any], core: Any) -> dict[str, Any]:
    """The canonical shape of a document (see the module docstring). `core` is a bigraph-schema core."""
    table: _EdgeTable = {}
    raw_schema = doc.get("schema") or {}
    schema = _norm_schema(raw_schema, core, (), table)
    state = _norm_state(doc.get("state") or {}, raw_schema, core, (), table)
    options = {k: _canon(doc[k], core) for k in COMPOSITE_OPTION_KEYS if k in doc}
    return {"schema": schema if isinstance(schema, dict) else {}, "state": state, "options": options}


def equivalent(a: dict[str, Any], b: dict[str, Any], core: Any) -> bool:
    return deep_equal(normalize_document(a, core), normalize_document(b, core))


def diff_documents(a: dict[str, Any], b: dict[str, Any], core: Any, limit: int = 200) -> str:
    """A readable account of how two documents differ after normalization (empty when equivalent)."""
    left, right = normalize_document(a, core), normalize_document(b, core)
    flat_left, flat_right = _flatten(left), _flatten(right)
    lines: list[str] = []
    for key in sorted(set(flat_left) | set(flat_right)):
        if key not in flat_right:
            lines.append(f"- {key}: {_show(flat_left[key])}")
        elif key not in flat_left:
            lines.append(f"+ {key}: {_show(flat_right[key])}")
        elif not deep_equal(flat_left[key], flat_right[key]):
            lines.append(f"~ {key}: {_show(flat_left[key])} -> {_show(flat_right[key])}")
    if len(lines) > limit:
        lines = [*lines[:limit], f"... {len(lines) - limit} more"]
    if not lines and not deep_equal(left, right):
        dump_left = json.dumps(left, indent=2, sort_keys=True, default=str).splitlines()
        dump_right = json.dumps(right, indent=2, sort_keys=True, default=str).splitlines()
        lines = list(difflib.unified_diff(dump_left, dump_right, "a", "b", lineterm=""))
    return "\n".join(lines)


def deep_equal(a: Any, b: Any, *, strict: bool = False, rel_tol: float = 1e-9) -> bool:
    """
    Structural equality that tolerates numpy arrays and float noise.

    With `strict=False` (the normalizer's mode) tuples equal lists and ints equal floats; with `strict=True`
    container types and numeric types must match exactly (the v1 parity tests use this).
    """
    if isinstance(a, np.ndarray) or isinstance(b, np.ndarray):
        if strict and not (isinstance(a, np.ndarray) and isinstance(b, np.ndarray)):
            return False
        return deep_equal(_to_list(a), _to_list(b), strict=False, rel_tol=rel_tol)
    if isinstance(a, dict) and isinstance(b, dict):
        return set(a) == set(b) and all(deep_equal(a[k], b[k], strict=strict, rel_tol=rel_tol) for k in a)
    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        if strict and type(a) is not type(b):
            return False
        return len(a) == len(b) and all(deep_equal(x, y, strict=strict, rel_tol=rel_tol) for x, y in zip(a, b))
    if isinstance(a, bool) or isinstance(b, bool):
        return a is b or (isinstance(a, bool) and isinstance(b, bool) and a == b)
    if _is_number(a) and _is_number(b):
        if strict and (isinstance(a, float) != isinstance(b, float)):
            return False
        return math.isclose(float(a), float(b), rel_tol=rel_tol, abs_tol=0.0)
    return bool(a == b)


# --- schema half -------------------------------------------------------------------------------------------------


def _norm_schema(schema: Any, core: Any, path: tuple[str, ...], table: _EdgeTable) -> Any:
    if isinstance(schema, dict) and schema.get("_type") in EDGE_KINDS:
        table[path] = {k: schema[k] for k in ("_type", "_inputs", "_outputs") if k in schema}
        return None
    if isinstance(schema, dict) and "_type" not in schema:
        out: dict[str, Any] = {}
        for key in sorted(schema, key=str):
            if not path and key == "global_time":
                continue
            value = _norm_schema(schema[key], core, (*path, str(key)), table)
            if value is not None:
                out[str(key)] = value
        return out
    return _canon_type(schema, core)


def _canon_type(spec: Any, core: Any) -> Any:
    try:
        rendered = core.render(core.access(spec), defaults=True)
    except Exception:  # noqa: BLE001 - an unknown dict-form type; fall back to a plain canonical dict
        return _canon(spec, core)
    if isinstance(rendered, str) and ("|" in rendered or ":" in rendered):
        try:
            rendered = core.render(core.access(rendered), defaults=True)
        except Exception:  # noqa: BLE001
            pass
    if isinstance(rendered, str):
        rendered = _split_default(rendered)
    return _canon(rendered, core)


_TRAILING_DEFAULT = re.compile(r"^([^{}]*)\{(.*)\}$")


def _split_default(rendered: str) -> Any:
    """`float{3.5}` -> `{"_type": "float", "_default": 3.5}`, so both default spellings collide."""
    match = _TRAILING_DEFAULT.match(rendered.strip())
    if not match:
        return rendered
    try:
        default = json.loads(match.group(2))
    except ValueError:
        default = match.group(2)
    return {"_type": match.group(1), "_default": default}


def _canon_ports(ports: Any, core: Any) -> Any:
    if isinstance(ports, str):
        try:
            ports = core.render(core.access(ports), defaults=True)
        except Exception:  # noqa: BLE001
            return ports
    if isinstance(ports, dict):
        return {str(k): _canon_type(v, core) for k, v in sorted(ports.items(), key=lambda kv: str(kv[0]))}
    return _canon(ports, core)


# --- state half --------------------------------------------------------------------------------------------------


def _norm_state(state: Any, schema: Any, core: Any, path: tuple[str, ...], table: _EdgeTable) -> Any:
    if is_site(state):
        return _canon_site(state, core)
    if isinstance(state, dict) and (is_edge_node(state) or path in table):
        return _canon_edge(state, core, path, table)
    if isinstance(state, dict) and not (isinstance(schema, dict) and "_type" in schema):
        out: dict[str, Any] = {}
        sub_schema = schema if isinstance(schema, dict) else {}
        keys = set(state) | {k for k in sub_schema if (*path, str(k)) not in table}
        for key in sorted(keys, key=str):
            if not path and key == "global_time":
                continue
            if key in state:
                out[str(key)] = _norm_state(state[key], sub_schema.get(key), core, (*path, str(key)), table)
            else:
                default = _schema_default(sub_schema[key], core)
                if default is not None:
                    out[str(key)] = _norm_state(default, sub_schema[key], core, (*path, str(key)), table)
        return out
    return _canon(state, core)


def _schema_default(schema: Any, core: Any) -> Any:
    """What process-bigraph materializes for a schema entry that has no state (a saved document contains it)."""
    if isinstance(schema, dict) and schema.get("_type") in EDGE_KINDS:
        return None
    try:
        default = core.default(core.access(schema))
    except Exception:  # noqa: BLE001
        return None
    return default[1] if isinstance(default, tuple) and len(default) == 2 else default


def _canon_edge(node: dict[str, Any], core: Any, path: tuple[str, ...], table: _EdgeTable) -> dict[str, Any]:
    info = table.get(path, {})
    out: dict[str, Any] = {"_type": node.get("_type") or info.get("_type")}
    address = node.get("address")
    if address is not None:
        out["address"] = _canon_address(address, core)
    for key in ("_inputs", "_outputs"):
        ports = node.get(key, info.get(key))
        if ports is not None:
            out[key] = _canon_ports(ports, core)
    config = node.get("config")
    if isinstance(config, dict) and _is_composite_address(address):
        config = dict(config)
        inner_table: _EdgeTable = {}
        inner_schema = config.get("schema") or {}
        config["schema"] = _norm_schema(inner_schema, core, (), inner_table) or {}
        config["state"] = _norm_state(config.get("state") or {}, inner_schema, core, (), inner_table)
    if config:
        out["config"] = _canon(config, core)
    for key in ("inputs", "outputs", "_triggers"):
        if node.get(key):
            out[key] = _canon_wires(node[key])
    # a process without an interval runs every 1.0: the default is not a difference
    if (
        node.get("interval") is not None
        and not _is_number(node["interval"])
        or (_is_number(node.get("interval")) and not math.isclose(float(node["interval"]), 1.0))
    ):
        out["interval"] = _canon(node["interval"], core)
    if node.get("priority") is not None:
        out["priority"] = _canon(node["priority"], core)
    for key, value in node.items():
        if key in out or key in RUNTIME_EDGE_KEYS or key in ("_type", "address", "config", "inputs", "outputs"):
            continue
        if key in ("_inputs", "_outputs", "_triggers", "interval", "priority"):
            continue
        out[str(key)] = _canon(value, core)
    return out


def _is_composite_address(address: Any) -> bool:
    text = _canon_address(address, None) if address is not None else ""
    return isinstance(text, str) and text.split(":", 1)[-1].lstrip("!").rsplit(".", 1)[-1] == "Composite"


def _canon_address(address: Any, core: Any) -> Any:
    if is_site(address):
        return _canon_site(address, core)
    if isinstance(address, dict) and "protocol" in address:
        return f"{address['protocol']}:{address.get('data', '')}"
    if isinstance(address, str) and ":" not in address:
        return f"local:{address}"
    return address


def _canon_site(site: dict[str, Any], core: Any) -> dict[str, Any]:
    out: dict[str, Any] = {"_type": "site"}
    if "_sort" in site:
        sort = site["_sort"]
        out["_sort"] = _canon_type(sort, core) if core is not None else _canon(sort, core)
    if "_default" in site:
        out["_default"] = _canon(site["_default"], core)
    return out


def _canon_wires(wires: Any) -> Any:
    if isinstance(wires, dict):
        return {str(k): _canon_wires(v) for k, v in sorted(wires.items(), key=lambda kv: str(kv[0]))}
    if isinstance(wires, str):
        return [wires]
    if isinstance(wires, (list, tuple)):
        return [int(s) if isinstance(s, (int, np.integer)) and not isinstance(s, bool) else str(s) for s in wires]
    return wires


# --- values ------------------------------------------------------------------------------------------------------


def _canon(value: Any, core: Any) -> Any:
    if is_site(value):
        return _canon_site(value, core)
    if isinstance(value, dict):
        return {str(k): _canon(v, core) for k, v in sorted(value.items(), key=lambda kv: str(kv[0]))}
    if isinstance(value, (list, tuple)):
        return [_canon(v, core) for v in value]
    if isinstance(value, np.ndarray):
        return _canon(value.tolist(), core)
    if isinstance(value, np.generic):
        return value.item()
    return value


def _to_list(value: Any) -> Any:
    return value.tolist() if isinstance(value, np.ndarray) else value


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float, np.integer, np.floating)) and not isinstance(value, bool)


def _flatten(tree: Any, prefix: str = "") -> dict[str, Any]:
    if isinstance(tree, dict) and tree:
        out: dict[str, Any] = {}
        for key, value in tree.items():
            out.update(_flatten(value, f"{prefix}/{key}" if prefix else str(key)))
        return out
    if isinstance(tree, list) and tree and any(isinstance(v, (dict, list)) for v in tree):
        out = {}
        for index, value in enumerate(tree):
            out.update(_flatten(value, f"{prefix}[{index}]"))
        return out
    return {prefix: tree}


def _show(value: Any) -> str:
    text = json.dumps(value, default=str)
    return text if len(text) <= 120 else text[:117] + "..."
