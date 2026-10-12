"""
Type expressions as data, for the normalizer and for `describe`: `parse_type` accepts both bigraph-schema
forms, the string grammar (`list[float]`, `a:float|b:integer`, `A~B`, `array[(3|4),float]`, `float{3.5}`) and
the dict form (`{"_type": "map", "_value": ...}`), and keeps the original (`source`) so that `to_bigraph` is
lossless. The DSL spelling of a type lives in TypeScript (`dsl/src/language/v2/types.ts`).
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any, Final

from bigraph_schema.parse import parse_expression  # type: ignore[import-untyped]


class _Missing:
    """The absence of a default (distinct from `None`)."""

    _instance: _Missing | None = None

    def __new__(cls) -> _Missing:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __repr__(self) -> str:
        return "MISSING"

    def __bool__(self) -> bool:
        return False


MISSING: Final = _Missing()


@dataclass
class Named:
    """A (possibly parametric) named type: `float`, `list[float]`, `map[string,float]`, `array[(3|4),float]`."""

    name: str
    args: list[TypeExpr] = field(default_factory=list)
    default: Any = MISSING
    units: str | None = None
    source: Any = None


@dataclass
class Struct:
    """A dict schema: `a:float|b:integer` or `{"a": "float", "b": "integer"}`."""

    fields: dict[str, TypeExpr]
    source: Any = None


@dataclass
class UnionType:
    """A union: `A~B`."""

    options: list[TypeExpr]
    source: Any = None


@dataclass
class Group:
    """A shape group inside an array type: `(3|4)`."""

    items: list[int | str]


@dataclass
class Raw:
    """A dict-form type with attributes that have no dedicated representation; kept verbatim."""

    attrs: dict[str, Any]
    source: Any = None


TypeExpr = Named | Struct | UnionType | Group | Raw

_PARAM_KEYS: dict[str, tuple[str, ...]] = {
    "list": ("_element",),
    "set": ("_element",),
    "tree": ("_leaf",),
    "map": ("_key", "_value"),
    "tuple": ("_values",),
    "enum": ("_values",),
    "union": ("_options",),
    "maybe": ("_value",),
    "overwrite": ("_value",),
    "const": ("_value",),
    "quote": ("_value",),
}
_ARRAY_KEYS = ("_shape", "_data", "_units")
_BIGRAPH_NAMES = {"int": "integer", "bool": "boolean"}
_TRAILING_DEFAULT = re.compile(r"^([^{}]*)\{(.*)\}$")


def parse_type(spec: Any) -> TypeExpr:
    """Parse a bigraph-schema type (string or dict form) into a `TypeExpr` that remembers its source."""
    if isinstance(spec, str):
        return _from_string(spec)
    if isinstance(spec, dict):
        return _from_dict(spec)
    raise TypeError(f"not a type expression: {spec!r}")


def _from_string(text: str) -> TypeExpr:
    source = text
    stripped = text.strip()
    default: Any = MISSING
    match = _TRAILING_DEFAULT.match(stripped)
    if match:
        stripped, default = match.group(1), _literal(match.group(2))
    expr = _from_parsed(parse_expression(stripped))
    if default is not MISSING and isinstance(expr, Named):
        expr.default = default
    if not isinstance(expr, Group):
        expr.source = source
    return expr


def _literal(text: str) -> Any:
    try:
        return json.loads(text)
    except ValueError:
        return text


def _from_parsed(parsed: Any) -> TypeExpr:
    if isinstance(parsed, str):
        return Named(parsed)
    if isinstance(parsed, list):
        name, params = parsed
        return Named(str(name), [_from_parsed(p) for p in params])
    if isinstance(parsed, tuple):
        return Group([_dim(p) for p in parsed])
    if isinstance(parsed, dict):
        if "_union" in parsed:
            return UnionType([_from_parsed(p) for p in parsed["_union"]])
        return Struct({str(k): _from_parsed(v) for k, v in parsed.items()})
    raise TypeError(f"unexpected parse result: {parsed!r}")


def _dim(value: Any) -> int | str:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return int(value)
    text = str(value)
    return int(text) if text.lstrip("-").isdigit() else text


def _from_dict(spec: dict[str, Any]) -> TypeExpr:
    if "_type" not in spec:
        if any(str(k).startswith("_") for k in spec):
            return Raw(dict(spec), source=spec)
        return Struct({str(k): parse_type(v) for k, v in spec.items()}, source=spec)
    name = spec["_type"]
    if not isinstance(name, str):
        return Raw(dict(spec), source=spec)
    if any(c in name for c in "[{|~") and set(spec) <= {"_type", "_default"}:
        inner = _from_string(name)  # `{"_type": "list[string]", "_default": []}`
        if isinstance(inner, Named) and "_default" in spec:
            inner.default = spec["_default"]
        if not isinstance(inner, Group):
            inner.source = spec
        return inner
    keys = set(spec) - {"_type", "_default", "_units"}
    args: list[TypeExpr] = []
    units: str | None = spec.get("_units")
    if name in _PARAM_KEYS and keys <= set(_PARAM_KEYS[name]):
        for key in _PARAM_KEYS[name]:
            if key not in spec:
                continue
            if key in ("_values", "_options"):
                args.extend(Named(str(v)) if name == "enum" else parse_type(v) for v in spec[key])
            else:
                args.append(parse_type(spec[key]))
    elif keys and keys <= set(_ARRAY_KEYS):
        if "_shape" in spec:
            args.append(Group([_dim(d) for d in spec["_shape"]]))
        if "_data" in spec:
            args.append(parse_type(spec["_data"]))
    elif keys:
        return Raw(dict(spec), source=spec)
    return Named(name, args, default=spec.get("_default", MISSING), units=units, source=spec)


def to_bigraph(expr: TypeExpr) -> Any:
    """Render a `TypeExpr` as a bigraph-schema type (the original form when it came from one)."""
    if not isinstance(expr, Group) and expr.source is not None:
        return expr.source
    if isinstance(expr, Named):
        return _named_to_bigraph(expr)
    if isinstance(expr, Struct):
        return {k: to_bigraph(v) for k, v in expr.fields.items()}
    if isinstance(expr, UnionType):
        rendered = [to_bigraph(o) for o in expr.options]
        if all(isinstance(r, str) for r in rendered):
            return "~".join(rendered)
        return {"_type": "union", "_options": rendered}
    if isinstance(expr, Group):
        return "(" + "|".join(str(i) for i in expr.items) + ")"
    return expr.attrs


def _named_to_bigraph(expr: Named) -> Any:
    name = _BIGRAPH_NAMES.get(expr.name, expr.name)
    shape = next((a for a in expr.args if isinstance(a, Group)), None)
    others = [to_bigraph(a) for a in expr.args if not isinstance(a, Group)]
    rendered: Any
    if not expr.args:
        rendered = name
    elif shape is not None:
        rendered = {"_type": name, "_shape": list(shape.items)}
        if others:
            rendered["_data"] = others[0]
    elif all(isinstance(r, str) for r in others):
        rendered = f"{name}[{','.join(others)}]"
    elif name in ("list", "set"):
        rendered = {"_type": name, "_element": others[0]}
    elif name == "tree":
        rendered = {"_type": name, "_leaf": others[0]}
    elif name == "map":
        rendered = {"_type": name, "_value": others[-1]}
        if len(others) == 2:
            rendered["_key"] = others[0]
    elif name in ("tuple", "enum"):
        rendered = {"_type": name, "_values": others}
    elif name == "union":
        rendered = {"_type": name, "_options": others}
    else:
        rendered = {"_type": name, "_value": others[0]}
    if expr.units is not None:
        rendered = (
            {**rendered, "_units": expr.units}
            if isinstance(rendered, dict)
            else {"_type": rendered, "_units": expr.units}
        )
    if expr.default is not MISSING:
        if isinstance(rendered, dict):
            return {**rendered, "_default": expr.default}
        return {"_type": rendered, "_default": expr.default}
    return rendered
