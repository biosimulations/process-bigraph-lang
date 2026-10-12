from typing import Any

import pytest

from process_bigraph_lang.v2.reader import read_composite_spec, read_document
from process_bigraph_lang.v2.writer import write_composite_spec
from process_bigraph_lang.v2.model import Address, Edge, Node, ParamRef, Site, Store
from process_bigraph_lang.v2.paths import Path
from process_bigraph_lang.v2.types import Named, Struct
from process_bigraph_lang.v2.values import MISSING


def test_stores_nodes_and_edges() -> None:
    doc = read_document({
        "schema": {"A": "float", "C": "float", "fields": {"glucose": "positive_float"}},
        "state": {
            "A": 2.07,
            "fields": {"glucose": 10},
            "counts": {},
            "adder": {"_type": "process", "address": "local:!pkg.mod.Add", "inputs": {"a": ["A"]}, "interval": 0.5},
        },
    })
    children = doc.root.children
    assert (
        isinstance(children["A"], Store)
        and children["A"].value == 2.07
        and children["A"].type == Named("float", source="float")
    )
    assert isinstance(children["C"], Store) and children["C"].value is MISSING  # schema only
    fields = children["fields"]
    assert isinstance(fields, Node) and isinstance(fields.children["glucose"], Store)
    assert fields.children["glucose"].type == Named("positive_float", source="positive_float")
    assert isinstance(children["counts"], Store) and children["counts"].value == {}  # an untyped dict is a store
    adder = children["adder"]
    assert isinstance(adder, Edge) and adder.kind == "process" and adder.interval == 0.5
    assert isinstance(adder.address, Address)
    assert adder.address == Address("local", "!pkg.mod.Add") and adder.address.module == "pkg.mod"
    assert adder.inputs == {"a": Path(["A"])} and adder.ports is None and adder.config == {}


def test_sites_and_address_sites() -> None:
    doc = read_document({
        "schema": {},
        "state": {
            "rate": {"_type": "site", "_sort": "float", "_default": 0.5},
            "p": {"x": {"_type": "site", "_sort": "float"}},
            "s": {
                "_type": "process",
                "address": {"_type": "site", "_sort": {"_type": "link", "_inputs": {"x": "float"}}},
            },
        },
    })
    rate = doc.root.children["rate"]
    assert isinstance(rate, Store) and rate.site == Site(Named("float", source="float"), 0.5)
    p = doc.root.children["p"]
    assert isinstance(p, Node) and isinstance(p.children["x"], Store) and p.children["x"].site is not None
    s = doc.root.children["s"]
    assert isinstance(s, Edge) and isinstance(s.address, Site)


def test_map_of_edges_keeps_its_type() -> None:
    schema = {"adders": {"_type": "map", "_value": {"_type": "process", "_inputs": {"a": "float"}}}}
    state = {"adders": {"one": {"_type": "process", "address": "local:X"}}}
    doc = read_document({"schema": schema, "state": state})
    adders = doc.root.children["adders"]
    assert isinstance(adders, Node) and adders.type is not None and isinstance(adders.children["one"], Edge)


def test_nested_composite() -> None:
    agent = {
        "_type": "process",
        "address": "local:Composite",
        "config": {
            "state": {"mass": 1.0, "grow": {"_type": "process", "address": "local:Grow", "inputs": {"mass": ["mass"]}}},
            "bridge": {"inputs": {"mass": ["mass"]}},
            "run_steps_on_init": True,
        },
        "inputs": {"mass": ["mass"]},
    }
    doc = read_document({"schema": {}, "state": {"agent": agent, "mass": 1.0}})
    cell = doc.root.children["agent"]
    assert isinstance(cell, Edge) and cell.is_composite and cell.inner is not None
    assert isinstance(cell.inner.children["grow"], Edge) and cell.bridge == {"inputs": {"mass": ["mass"]}}
    assert cell.config == {"run_steps_on_init": True}


def test_saved_form_is_detected_and_cleaned() -> None:
    saved = {
        "schema": {
            "A": "float",
            "global_time": "float",
            "add": {
                "_type": "process",
                "address": "local:!m.Add",
                "_inputs": "a:float|b:float",
                "inputs": "wires",
                "interval": 1.0,
            },
        },
        "state": {
            "A": 1.0,
            "global_time": 2.0,
            "add": {
                "address": {"protocol": "local", "data": "!m.Add"},
                "config": {},
                "_inputs": "a:float|b:float",
                "inputs": {"a": ["A"]},
                "interval": 1.0,
                "_contract": {"face": {}},
                "instance": object(),
            },
        },
    }
    doc = read_document(saved)
    assert doc.source == "saved"
    assert set(doc.root.children) == {"A", "add"}
    add = doc.root.children["add"]
    assert isinstance(add, Edge) and add.kind == "process" and add.address == Address("local", "!m.Add")
    assert add.ports is not None and add.ports.inputs is not None and set(add.ports.inputs) == {"a", "b"}
    assert add.ports.outputs is None and add.extras == {}


def test_extra_keys_and_options_are_kept() -> None:
    doc = read_document({
        "schema": {},
        "state": {"e": {"_type": "step", "address": "local:X", "note": "hi", "_triggers": [["a"]]}},
        "global_time_precision": 6,
        "composition": {"legacy": True},
    })
    e = doc.root.children["e"]
    assert isinstance(e, Edge) and e.extras == {"note": "hi", "_triggers": [["a"]]}
    assert doc.options == {"global_time_precision": 6} and doc.extras == {"composition": {"legacy": True}}


def test_edge_without_kind_is_an_error() -> None:
    with pytest.raises(ValueError, match="neither a _type nor a schema entry"):
        read_document({"schema": {}, "state": {"x": {"address": "local:X"}}})


def test_composite_spec_parameters_and_emitters() -> None:
    spec: dict[str, Any] = {
        "name": "demo",
        "description": "A demo.",
        "tags": ["t"],
        "requires": {"processes": ["X"]},
        "parameters": {"dt": {"type": "float", "default": 0.1, "description": "step"}, "label": {"type": "string"}},
        "emitters": [{"address": "local:ParquetEmitter", "paths": ["a", "b/c"]}],
        "state": {
            "x": {"_type": "process", "address": "local:X", "interval": "${dt}", "config": {"name": "run_${label}"}}
        },
        "default_n_steps": 10,
    }
    doc = read_composite_spec(spec)
    assert doc.source == "composite_spec" and doc.name == "demo" and [p.name for p in doc.params] == ["dt", "label"]
    x = doc.root.children["x"]
    assert (
        isinstance(x, Edge) and x.interval == ParamRef("dt") and x.config == {"name": ParamRef("label", "run_${label}")}
    )
    assert doc.emitters[0].paths == [Path(["a"]), Path(["b", "c"])] and doc.extras == {"default_n_steps": 10}
    back = write_composite_spec(doc)
    assert back["parameters"] == spec["parameters"] and back["emitters"] == spec["emitters"]
    assert back["state"] == spec["state"] and back["default_n_steps"] == 10


def test_struct_schema_without_state_is_a_typed_store() -> None:
    doc = read_document({"schema": {"pt": {"x": "float", "y": "float"}}, "state": {}})
    pt = doc.root.children["pt"]
    assert isinstance(pt, Store) and isinstance(pt.type, Struct) and pt.value is MISSING
