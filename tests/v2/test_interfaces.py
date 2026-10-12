"""Interface declarations generated from Python classes, the manifest round trip, and `import` resolution."""

import json
from copy import deepcopy
from typing import Any

import pytest

from process_bigraph_lang.v2 import InterfaceRegistry, Printed, decompile, describe_module, render_interfaces
from process_bigraph_lang.v2.langium import langium_cli
from process_bigraph_lang.v2.types import parse_type
from tests.compiler.generator.test_toy_add_floats import add_floats_process_expected_config_template
from tests.v2.helpers import assert_snapshot

TOY = "tests.fixtures.test_registry.toy_library"
SPATIO = "tests.fixtures.test_registry.spatio_flux.processes"
needs_cli = pytest.mark.skipif(langium_cli() is None, reason="no Langium CLI (build dsl/ or install cli-native)")


def test_describe_toy_library() -> None:
    decls = {d.name: d for d in describe_module(TOY)}
    assert set(decls) >= {"AddFloatsStep", "AddFloatsProcess", "SaveFloatToFileStep", "AddComplexNumbersStep"}
    assert "TypedStep" not in decls  # defined in another module: not this module's own
    add = decls["AddFloatsProcess"]
    assert add.kind == "process" and add.address == f"local:!{TOY}.AddFloatsProcess"
    assert add.inputs is not None and set(add.inputs) == {"left_hand_addend", "right_hand_addend"}
    assert add.outputs is not None and add.outputs["result"] == "float"
    assert decls["AddFloatsStep"].kind == "step" and not add.dynamic_ports


def test_describe_marks_dynamic_ports() -> None:
    decls = {d.name: d for d in describe_module(SPATIO)}
    dfba = decls["DynamicFBA"]
    assert dfba.inputs is not None and parse_type(dfba.inputs["substrates"]) == parse_type("map[positive_float]")
    kinetic = dfba.config["kinetic_params"].type
    assert kinetic is not None and parse_type(kinetic) == parse_type("map[tuple[float,float]]")
    assert dfba.doc is not None and dfba.doc.startswith("Performs dynamic FBA")
    diffusion = decls["DiffusionAdvection"]
    assert diffusion.dynamic_ports and diffusion.inputs is None  # ports read self.config


def test_manifest_round_trip() -> None:
    registry = InterfaceRegistry.from_modules(TOY, SPATIO)
    manifest = json.loads(json.dumps(registry.to_manifest(), default=str))
    restored = InterfaceRegistry.from_manifest(manifest)
    assert [d.name for d in restored.decls] == [d.name for d in registry.decls]
    assert json.loads(json.dumps(restored.to_manifest(), default=str)) == manifest


def test_lookup_by_address_and_by_short_name() -> None:
    registry = InterfaceRegistry.from_modules(SPATIO)
    decl = registry.lookup(f"local:!{SPATIO}.DynamicFBA")
    assert decl is not None and decl.name == "DynamicFBA"
    assert registry.lookup("local:DynamicFBA") is decl  # registry name, unique
    assert registry.lookup("local:Nope") is None
    assert registry.lookup("rest:DynamicFBA") is None


@needs_cli
def test_interface_file_snapshot() -> None:
    text = render_interfaces(describe_module(TOY), TOY)
    assert_snapshot("toy_library.interfaces", Printed(text))
    assert f'process AddFloatsProcess at "local:!{TOY}.AddFloatsProcess" {{' in text


@needs_cli
def test_decompiling_against_a_registry_imports_instead_of_declaring() -> None:
    registry = InterfaceRegistry.from_modules(TOY)
    text = decompile(deepcopy(add_floats_process_expected_config_template), registry=registry).text
    assert f"import {TOY}.{{AddFloatsProcess, SaveFloatToFileStep}};" in text
    assert "process add_nums : AddFloatsProcess {" in text and "step print_result : SaveFloatToFileStep {" in text
    assert 'at "local:!' not in text and "ports {" not in text


@needs_cli
def test_edge_ports_that_differ_from_the_interface_are_kept() -> None:
    registry = InterfaceRegistry.from_modules(TOY)
    original: dict[str, Any] = deepcopy(add_floats_process_expected_config_template)
    original["state"]["add_nums"]["_outputs"] = {"result": "integer"}
    text = decompile(original, registry=registry).text
    assert "process add_nums : AddFloatsProcess {" in text and "ports {" in text and "outputs { result: int; }" in text
