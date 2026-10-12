from typing import Any

import pytest

from process_bigraph_lang.v2.types import Group, Named, Raw, Struct, UnionType, parse_type, to_bigraph, to_surface
from process_bigraph_lang.v2.values import MISSING

# (bigraph-schema form, DSL spelling): every row parses, prints its spelling and renders back to its source
TABLE: list[tuple[Any, str]] = [
    ("float", "float"),
    ("integer", "int"),
    ("boolean", "bool"),
    ("string", "string"),
    ("list[float]", "list<float>"),
    ("map[float]", "map<string, float>"),
    ("map[string,float]", "map<string, float>"),
    ("tuple[float,float]", "tuple<float, float>"),
    ("maybe[float]", "maybe<float>"),
    ("overwrite[array[float]]", "overwrite<array<float>>"),
    ("enum[a,b]", "enum<a, b>"),
    ("range[0,1]", "range<0, 1>"),
    ("array[(3|4),float]", "array<float>[3, 4]"),
    ("a:float|b:integer", "{ a: float; b: int; }"),
    ("A~B", "A | B"),
    ("float{3.5}", "float{3.5}"),
    ("positive_float", "positive_float"),
    ({"_type": "map", "_value": "positive_float"}, "map<string, positive_float>"),
    ({"_type": "list", "_element": {"x": "float"}}, "list<{ x: float; }>"),
    ({"_type": "float", "_default": 2.0}, "float{2.0}"),
    ({"_type": "positive_array", "_shape": (10, 10), "_data": "float"}, "positive_array<float>[10, 10]"),
    ({"_type": "array", "_shape": [3, 3], "_data": "float", "_units": "uM"}, 'array<float>[3, 3] @ "uM"'),
    ({"x": "float", "y": {"_type": "integer", "_default": 3}}, "{ x: float; y: int{3}; }"),
    ({"_type": "link", "_inputs": {"x": "float"}, "_outputs": {"y": "float"}}, "link<{ x: float; }, { y: float; }>"),
    ({"_type": "process", "_inputs": {"x": "float"}}, "process"),
]


@pytest.mark.parametrize(("source", "surface"), TABLE)
def test_parse_print_and_render_back(source: Any, surface: str) -> None:
    expr = parse_type(source)
    assert to_surface(expr) == surface
    assert to_bigraph(expr) == source


def test_parsed_shapes() -> None:
    assert parse_type("list[float]") == Named("list", [Named("float")], source="list[float]")
    assert parse_type("A~B") == UnionType([Named("A"), Named("B")], source="A~B")
    assert parse_type("a:float|b:integer") == Struct(
        {"a": Named("float"), "b": Named("integer")}, source="a:float|b:integer"
    )
    array = parse_type("array[(3|4),float]")
    assert isinstance(array, Named) and array.args == [Group([3, 4]), Named("float")]
    assert parse_type("float{3.5}") == Named("float", default=3.5, source="float{3.5}")
    raw = parse_type({"_type": "float", "_units": "mM", "_min": 0})
    assert isinstance(raw, Raw)


def test_render_without_source_uses_string_form_when_possible() -> None:
    assert to_bigraph(Named("list", [Named("float")])) == "list[float]"
    assert to_bigraph(Named("map", [Named("string"), Named("float")])) == "map[string,float]"
    assert to_bigraph(Named("int")) == "integer"
    assert to_bigraph(Named("array", [Group([3, 4]), Named("float")])) == {
        "_type": "array",
        "_shape": [3, 4],
        "_data": "float",
    }
    assert to_bigraph(Struct({"a": Named("float")})) == {"a": "float"}
    assert to_bigraph(Named("float", default=1.0)) == {"_type": "float", "_default": 1.0}
    assert to_bigraph(Named("list", [Struct({"a": Named("float")})])) == {"_type": "list", "_element": {"a": "float"}}
    assert to_bigraph(UnionType([Named("A"), Named("B")])) == "A~B"


def test_missing_default_is_distinct_from_none() -> None:
    assert parse_type("float").default is MISSING  # type: ignore[union-attr]
    assert parse_type({"_type": "float", "_default": None}).default is None  # type: ignore[union-attr]
