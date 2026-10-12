"""Interface declarations generated from Python classes, the manifest round trip, and `import` resolution."""

import json
from copy import deepcopy
from typing import Any

from process_bigraph_lang.v2 import (
    InterfaceRegistry,
    describe_module,
    print_document,
    print_interfaces,
    read_document,
)
from process_bigraph_lang.v2.model import Address
from process_bigraph_lang.v2.printer import Printed
from process_bigraph_lang.v2.types import to_surface
from tests.compiler.generator.test_toy_add_floats import add_floats_process_expected_config_template
from tests.v2.helpers import assert_snapshot

TOY = "tests.fixtures.test_registry.toy_library"
SPATIO = "tests.fixtures.test_registry.spatio_flux.processes"


def test_describe_toy_library() -> None:
    decls = {d.name: d for d in describe_module(TOY)}
    assert set(decls) >= {"AddFloatsStep", "AddFloatsProcess", "SaveFloatToFileStep", "AddComplexNumbersStep"}
    assert "TypedStep" not in decls  # defined in another module: not this module's own
    add = decls["AddFloatsProcess"]
    assert add.kind == "process" and add.address == Address("local", f"!{TOY}.AddFloatsProcess")
    assert add.inputs is not None and set(add.inputs) == {"left_hand_addend", "right_hand_addend"}
    assert add.outputs is not None and to_surface(add.outputs["result"]) == "float"
    assert decls["AddFloatsStep"].kind == "step" and not add.dynamic_ports


def test_describe_marks_dynamic_ports() -> None:
    decls = {d.name: d for d in describe_module(SPATIO)}
    dfba = decls["DynamicFBA"]
    assert dfba.inputs is not None and to_surface(dfba.inputs["substrates"]) == "map<string, positive_float>"
    kinetic = dfba.config["kinetic_params"].type
    assert kinetic is not None and to_surface(kinetic) == "map<string, tuple<float, float>>"
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
    decl = registry.lookup(Address.from_any(f"local:!{SPATIO}.DynamicFBA"))
    assert decl is not None and decl.name == "DynamicFBA"
    assert registry.lookup(Address.from_any("local:DynamicFBA")) is decl  # registry name, unique
    assert registry.lookup(Address.from_any("local:Nope")) is None
    assert registry.lookup(Address.from_any("rest:DynamicFBA")) is None


def test_interface_file_snapshot() -> None:
    text = print_interfaces(describe_module(TOY), TOY)
    assert_snapshot("toy_library.interfaces", Printed(text))
    assert f'process AddFloatsProcess at "local:!{TOY}.AddFloatsProcess" {{' in text


def test_printing_against_a_registry_imports_instead_of_declaring() -> None:
    registry = InterfaceRegistry.from_modules(TOY)
    doc = read_document(deepcopy(add_floats_process_expected_config_template))
    text = print_document(doc, registry=registry).text
    assert f"import {TOY}.{{AddFloatsProcess, SaveFloatToFileStep}};" in text
    assert "process add_nums : AddFloatsProcess {" in text and "step print_result : SaveFloatToFileStep {" in text
    assert 'at "local:!' not in text and "ports {" not in text


def test_edge_ports_that_differ_from_the_interface_are_kept() -> None:
    registry = InterfaceRegistry.from_modules(TOY)
    original: dict[str, Any] = deepcopy(add_floats_process_expected_config_template)
    original["state"]["add_nums"]["_outputs"] = {"result": "integer"}
    text = print_document(read_document(original), registry=registry).text
    assert "process add_nums : AddFloatsProcess {" in text and "ports {" in text and "outputs { result: int; }" in text
