from pathlib import Path
from typing import Any

import numpy as np
import process_bigraph as pg  # type: ignore[import-untyped]
import pytest

from process_bigraph_lang.compiler.converter import assemble_pb
from process_bigraph_lang.compiler.generator import compile_ast
from process_bigraph_lang.dsl.langium_pblang import langium_parse_pblang_file, langium_parse_pblang_str

PREAMBLE = """
    type float builtin
    type string builtin
    type int builtin
    type bool builtin
"""


def compile_pblang(pblang: str) -> dict[str, Any]:
    return assemble_pb(compile_ast(langium_parse_pblang_str(PREAMBLE + pblang)))


def test_struct_stores_are_nested_with_field_defaults() -> None:
    doc = compile_pblang("""
        struct Point { x: float; y: float = 2.0; }
        store origin: Point;
        init origin = { x = 1, y = 3.0 };
        let unset: Point;
    """)
    assert doc["schema"] == {
        "origin": {"x": "float", "y": {"_type": "float", "_default": 2.0}},
        "unset": {"x": "float", "y": {"_type": "float", "_default": 2.0}},
    }
    assert doc["state"] == {"origin": {"x": 1.0, "y": 3.0}}


def test_type_schemas() -> None:
    doc = compile_pblang("""
        struct Bounds { lower: float; upper: float; }
        type Conc = float
        let i: int = 1;
        let b: bool = true;
        let c: Conc = 2;
        let xs: array<float> = [1, 2.5];
        let t: (a: float, b: string) = (b = "s", a = 3.0);
        let m: map<string, (km: float, vmax: float)> = { "glc" = (vmax = 2.0, km = 0.5) };
        let bounds: map<string, Bounds> = { "ATPM" = { lower = -1.0, upper = 1.0 } };
    """)
    assert doc["schema"] == {
        "i": "integer",
        "b": "boolean",
        "c": "float",
        "xs": "list[float]",
        "t": "tuple[float,string]",
        "m": "map[tuple[float,float]]",
        "bounds": {"_type": "map", "_value": {"lower": "float", "upper": "float"}},
    }
    assert doc["state"] == {
        "i": 1,
        "b": True,
        "c": 2.0,
        "xs": [1.0, 2.5],
        "t": (3.0, "s"),
        "m": {"glc": (0.5, 2.0)},
        "bounds": {"ATPM": {"lower": -1.0, "upper": 1.0}},
    }


def test_config_arguments_resolve_constant_references() -> None:
    doc = compile_pblang("""
        remote step Save at "pkg.Save" {
            config (path: string, window: (lo: float, hi: float), scale: float)
            inputs (value: float)
        }
        let out: string = "out.txt";
        let limits: (lo: float, hi: float) = (hi = 2.0, lo = 1.0);
        let x: float = 0.0;
        let save: Save = Save(path = out, window = limits, scale = limits.hi);
        connect save inputs (value = x);
    """)
    assert doc["state"]["save"] == {
        "_type": "step",
        "_inputs": {"value": "float"},
        "address": "local:!pkg.Save",
        "config": {"path": "out.txt", "window": (1.0, 2.0), "scale": 2.0},
        "inputs": {"value": ["x"]},
    }


def test_nested_edges_use_relative_paths() -> None:
    doc = compile_pblang("""
        remote process Grow at "pkg.Grow" { inputs (size: float) outputs (size: float) }
        struct Cell { size: float; grow: Grow; }
        let cell: Cell = { size = 1.0, grow = Grow() };
        let total: float = 0.0;
        connect cell.grow inputs (size = cell.size) outputs (size = total);
    """)
    assert doc["schema"] == {"cell": {"size": "float"}, "total": "float"}
    assert doc["state"]["cell"] == {
        "size": 1.0,
        "grow": {
            "_type": "process",
            "_inputs": {"size": "float"},
            "_outputs": {"size": "float"},
            "address": "local:!pkg.Grow",
            "inputs": {"size": ["size"]},
            "outputs": {"size": ["..", "total"]},
        },
    }


def test_destructuring_let_declares_one_store_per_binding() -> None:
    doc = compile_pblang("""
        let (first: string, last: string): (first: string, last: string) = (last = "Lovelace", first = "Ada");
    """)
    assert doc["schema"] == {"first": "string", "last": "string"}
    assert doc["state"] == {"first": "Ada", "last": "Lovelace"}


def test_port_connected_twice_is_an_error() -> None:
    with pytest.raises(ValueError, match="Port 'size' of 'g' is connected more than once"):
        compile_pblang("""
            remote process Grow at "pkg.Grow" { inputs (size: float) outputs (size: float) }
            let a: float = 1.0;
            let g: Grow = Grow();
            connect g inputs (size = a) outputs (size = a);
            connect g inputs (size = a) outputs (size = a);
        """)


def test_non_string_map_keys_are_an_error() -> None:
    with pytest.raises(ValueError, match="map key type must be 'string'"):
        compile_pblang("""
            let m: map<int, float> = { 1 = 1.0 };
        """)


def test_compiles_abc_fixture(model_path_abc: Path) -> None:
    doc = assemble_pb(compile_ast(langium_parse_pblang_file(model_path_abc)))
    assert doc["state"]["medium"] == {"glucose": 3.0, "calcium": 0.5}
    assert doc["state"]["proc2"] == {
        "_type": "process",
        "_inputs": {"glucose": "float", "calcium": "float"},
        "_outputs": {"glucose": "float", "calcium": "float"},
        "address": "local:!my_processes.Process1",
        "config": {"calcium_growth": 0.1, "glucose_growth": 0.1, "dt": 0.1, "alpha": 0.1},
        "inputs": {"glucose": ["cell", "glucose"], "calcium": ["cell", "calcium"]},
        "outputs": {"glucose": ["cell", "glucose"], "calcium": ["cell", "calcium"]},
    }


def test_compiled_document_runs_in_process_bigraph() -> None:
    doc = compile_pblang("""
        remote process Add at "tests.fixtures.test_registry.toy_library.AddFloatsProcess" {
            inputs (left_hand_addend: float, right_hand_addend: float)
            outputs (result: float)
        }
        struct Operands { a: float; b: float; }
        let operands: Operands = { a = 2.07, b = 3.5 };
        let total: float = 0.0;
        let add: Add = Add();
        connect add inputs (left_hand_addend = operands.a, right_hand_addend = operands.b) outputs (result = total);
    """)
    assert doc["state"]["add"]["address"] == "local:!tests.fixtures.test_registry.toy_library.AddFloatsProcess"
    composite = pg.Composite(doc, core=pg.allocate_core())
    composite.run(10.0)
    assert np.allclose(composite.state["total"], (2.07 + 3.5) * 10)
    assert composite.state["operands"] == {"a": 2.07, "b": 3.5}


def test_open_values_compile_to_template_sites() -> None:
    doc = compile_pblang("""
        struct Point { x: float; y: float = 2.0; }
        remote process Scale { config (rate: float) inputs (x: float) outputs (y: float) }
        let rate: float = ?(0.5);
        let p: Point = { x = ?, y = ?(3.0) };
        let whole: Point = ?;
        let s: Scale = Scale(rate = ?);
        connect s inputs (x = p.x) outputs (y = p.y);
    """)
    # open stores are typed by their site's _sort only (a schema entry would hide the open site)
    assert doc["schema"] == {}
    face = {"_type": "link", "_inputs": {"x": "float"}, "_outputs": {"y": "float"}}
    assert doc["state"] == {
        "rate": {"_type": "site", "_sort": "float", "_default": 0.5},
        "p": {"x": {"_type": "site", "_sort": "float"}, "y": {"_type": "site", "_sort": "float", "_default": 3.0}},
        "whole": {"_type": "site", "_sort": {"x": "float", "y": "float"}},
        "s": {
            "_type": "process",
            "_inputs": {"x": "float"},
            "_outputs": {"y": "float"},
            "address": {"_type": "site", "_sort": face},
            "config": {"rate": {"_type": "site", "_sort": "float"}},
            "inputs": {"x": ["p", "x"]},
            "outputs": {"y": ["p", "y"]},
        },
    }


TEMPLATE_PBLANG = """
    remote process Adder {
        inputs (left_hand_addend: float, right_hand_addend: float)
        outputs (result: float)
    }
    struct Operands { a: float; b: float; }
    let operands: Operands = { a = ?, b = ?(3.5) };
    let total: float = 0.0;
    let add: Adder = Adder();
    connect add inputs (left_hand_addend = operands.a, right_hand_addend = operands.b) outputs (result = total);
"""


def _template_core() -> Any:
    from tests.fixtures.test_registry.toy_library import AddFloatsProcess

    core = pg.allocate_core()
    # face checking resolves a filler's ports through the link registry, so fill by registered name
    core.register_link("AddFloatsProcess", AddFloatsProcess)
    return core


def test_filled_template_runs_in_process_bigraph() -> None:
    from process_bigraph.templates import open_sites, template_document  # type: ignore[import-untyped]

    doc = compile_pblang(TEMPLATE_PBLANG)
    core = _template_core()
    template = core.access(doc["state"])
    assert sorted(open_sites(template)) == [("add", "address"), ("operands", "a"), ("operands", "b")]

    state = template_document(core, template, {"operands/a": 2.07, "add/address": "local:AddFloatsProcess"})
    composite = pg.Composite({"schema": doc["schema"], "state": state}, core=_template_core())
    composite.run(10.0)
    assert composite.state["operands"] == {"a": 2.07, "b": 3.5}
    assert np.allclose(composite.state["total"], (2.07 + 3.5) * 10)


def test_unfilled_template_does_not_run() -> None:
    from process_bigraph.templates import template_document

    doc = compile_pblang(TEMPLATE_PBLANG)
    core = _template_core()
    with pytest.raises(ValueError, match="required site\\(s\\) left unfilled: 'add/address', 'operands/a'"):
        template_document(core, core.access(doc["state"]), {})
    with pytest.raises(ValueError, match="not ground"):
        pg.Composite(compile_pblang("let a: float = ?;"), core=_template_core())
    # process-bigraph 1.8.4 realizes edges before its groundness check, so an open *address*
    # fails inside realize_link rather than with the "not ground" message
    with pytest.raises(Exception):  # noqa: B017
        pg.Composite(doc, core=_template_core())
