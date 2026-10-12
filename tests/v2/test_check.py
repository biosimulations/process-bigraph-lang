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
    # the headers say which components have ports that only an instance can tell
    assert set(by_code["I210"]) == {"particles", "recorder"}
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
