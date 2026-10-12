"""Static checks against interface declarations, with no process code imported."""

from copy import deepcopy
from typing import Any

from process_bigraph_lang.v2 import read_document
from process_bigraph_lang.v2.check import check_document
from tests.compiler.generator.test_toy_add_floats import add_floats_process_expected_config_template
from tests.v2.helpers import REGISTRY, load_corpus_json


def _codes(doc: dict[str, Any]) -> dict[str, list[str]]:
    diagnostics = check_document(read_document(doc), REGISTRY)
    out: dict[str, list[str]] = {}
    for d in diagnostics:
        out.setdefault(d.code, []).append(d.path)
    return out


def test_clean_document_has_no_findings() -> None:
    assert check_document(read_document(deepcopy(add_floats_process_expected_config_template)), REGISTRY) == []


def test_mistakes_are_found_without_importing_processes() -> None:
    toy = "tests.fixtures.test_registry.toy_library"
    doc = {
        "schema": {"A": "float", "label": "string"},
        "state": {
            "A": 1.0,
            "label": "x",
            "add": {
                "_type": "process",
                "address": f"local:!{toy}.AddFloatsProcess",
                "inputs": {"left_hand_addend": ["A"], "right_hand_addend": ["label"], "extra": ["A"]},
                "outputs": {"result": ["nowhere"]},
            },
            "save": {
                "_type": "step",
                "address": f"local:!{toy}.SaveFloatToFileStep",
                "config": {"output_file_path": "out.txt"},
                "inputs": {"result": ["..", "..", "A"]},
                "interval": 1.0,
            },
            "dfba": {
                "_type": "process",
                "address": "local:DynamicFBA",
                "config": {"model_file": "textbook", "colour": "red"},
            },
            "mystery": {"_type": "step", "address": "local:Mystery", "inputs": {"a": ["A"]}},
        },
    }
    codes = _codes(doc)
    assert codes["S021"] == ["add/inputs/extra"]  # not a port of AddFloatsProcess
    assert codes["W200"] == ["add/inputs/right_hand_addend"]  # float port wired to a string store
    assert codes["W211"] == ["add/outputs/result"]  # no store 'nowhere'
    assert codes["S022"] == ["dfba/config/colour"]  # DynamicFBA declares no such config key
    assert "dfba/config/bounds" in codes["T121"] and "dfba/config/kinetic_params" in codes["T121"]  # required
    assert codes["T130"] == ["save"]  # interval on a step
    assert codes["E110"] == ["save/inputs/result"]  # ../../A escapes the root
    assert codes["S020"] == ["mystery"]  # unknown component: not checked


def test_hybrid_against_generated_headers() -> None:
    doc = read_document(load_corpus_json("hybrid_two_way_exchange.json"))
    diagnostics = check_document(doc, REGISTRY)
    assert not [d for d in diagnostics if d.severity == "error"]
    by_code = {d.code: [x.path for x in diagnostics if x.code == d.code] for d in diagnostics}
    # the recorder reads particle positions that no store declares: process-bigraph creates it silently
    assert "recorder/inputs/particle_positions" in by_code["W211"]
    assert "particles/outputs/particle_positions" in by_code["W211"]
    # the headers say which components have ports that only an instance can tell: now only the Stepper wrapper
    assert set(by_code["I210"]) == {"particles"}
    # the hybrid's stores are untyped dicts, so port types cannot be checked yet
    assert "pde/inputs/fields" in by_code["I220"]


def test_sub_port_wires_use_the_map_value_type() -> None:
    spatio = "tests.fixtures.test_registry.spatio_flux.processes"
    doc = {
        "schema": {"fields": {"glucose": "positive_float", "biomass": "string"}},
        "state": {
            "fields": {"glucose": 1.0, "biomass": "x"},
            "dfba": {
                "_type": "process",
                "address": f"local:!{spatio}.DynamicFBA",
                "config": {
                    "model_file": "textbook",
                    "kinetic_params": {},
                    "substrate_update_reactions": {},
                    "biomass_identifier": "biomass",
                    "bounds": {},
                },
                "inputs": {"substrates": {"glucose": ["fields", "glucose"], "biomass": ["fields", "biomass"]}},
            },
        },
    }
    codes = _codes(doc)
    assert codes.get("W200") == ["dfba/inputs/substrates/biomass"]
    assert "T121" not in codes and "S021" not in codes


# --- writer analysis: how the processes that write one store combine -------------------------------------------

TOY = "tests.fixtures.test_registry.toy_library"


def _writer_doc(store_type: str, *outputs: tuple[str, str, str]) -> dict[str, Any]:
    """A store `x` and one edge per (kind, name, port type) writing it through port `out`."""
    state: dict[str, Any] = {"x": 0.0}
    for kind, name, port_type in outputs:
        state[name] = {
            "_type": kind,
            "address": f"local:{name}",
            "_outputs": {"out": port_type},
            "outputs": {"out": ["x"]},
        }
    return {"schema": {"x": store_type}, "state": state}


def test_additive_writers_are_reported_for_review() -> None:
    codes = _codes(_writer_doc("float", ("process", "a", "float"), ("process", "b", "float")))
    assert codes.get("W220") == ["x"] and "W221" not in codes


def test_overwrite_next_to_another_writer_is_order_dependent() -> None:
    codes = _codes(_writer_doc("float", ("process", "a", "overwrite[float]"), ("process", "b", "float")))
    assert codes.get("W221") == ["x"] and "W220" not in codes
    codes = _codes(_writer_doc("float", ("process", "a", "overwrite[float]"), ("process", "b", "overwrite[float]")))
    assert codes.get("W221") == ["x"]
    # a store declared overwrite replaces on every write, whatever the ports say
    codes = _codes(_writer_doc("overwrite[float]", ("process", "a", "float"), ("process", "b", "float")))
    assert codes.get("W221") == ["x"]


def test_single_writer_is_silent() -> None:
    codes = _codes(_writer_doc("float", ("process", "a", "overwrite[float]")))
    assert not {"W220", "W221", "W223"} & set(codes)


def test_step_publishing_an_array_additively_is_suspicious() -> None:
    doc = {
        "schema": {"fields": "map[array[float]]", "conc": "map[array[float]]"},
        "state": {
            "fields": {},
            "conc": {},
            "adapter": {
                "_type": "step",
                "address": "local:Adapter",
                "_outputs": {"conc": "map[array[float]]"},
                "outputs": {"conc": ["conc"]},
            },
            "good": {
                "_type": "step",
                "address": "local:Good",
                "_outputs": {"conc": "map[overwrite[array[float]]]"},
                "outputs": {"conc": ["fields"]},
            },
            "pde": {
                "_type": "process",
                "address": "local:Pde",
                "_outputs": {"f": "map[array[float]]"},
                "outputs": {"f": ["fields"]},
            },
        },
    }
    codes = _codes(doc)
    assert codes.get("W223") == ["adapter/outputs/conc"]  # the process `pde` and the overwriting step are fine
    assert codes.get("W221") == ["fields"]  # `good` overwrites what `pde` accumulates into


def test_hybrid_writers_are_clean() -> None:
    diagnostics = check_document(read_document(load_corpus_json("hybrid_two_way_exchange.json")), REGISTRY)
    assert not [d for d in diagnostics if d.code in ("W221", "W223")]
