from copy import deepcopy
from typing import Any

import numpy as np
import process_bigraph as pg  # type: ignore[import-untyped]

from process_bigraph_lang.compiler.converter import assemble_pb
from process_bigraph_lang.compiler.generator import compile_ast
from process_bigraph_lang.compiler.pb_model import (
    PBStoreSchema,
    PBStoreState,
    PBModel,
    PBProcessSchema,
    PBProcessState,
    PBCollectionType,
)
from process_bigraph_lang.dsl.ast_model import ASTModel
from process_bigraph_lang.dsl.langium_pblang import langium_parse_pblang_str
from tests.fixtures.test_registry.toy_library import AddFloatsStep

flat_expected_config_template = {
    "composition": {
        "A": "float",
        "B": "float",
        "C": "float",
        "add_nums_1": {
            "_type": "process",
            "address": {
                "_type": "quote",
                "_default": "local:!tests.fixtures.test_registry.toy_library.AddFloatsProcess",
            },
            "_inputs": {"left_hand_addend": "float", "right_hand_addend": "float"},
            "_outputs": {"result": "float"},
        },
        "add_nums_2": {
            "_type": "process",
            "address": {
                "_type": "quote",
                "_default": "local:!tests.fixtures.test_registry.toy_library.AddFloatsProcess",
            },
            "_inputs": {"left_hand_addend": "float", "right_hand_addend": "float"},
            "_outputs": {"result": "float"},
        },
    },
    "state": {
        "A": 2.07,
        "B": 3.5,
        "add_nums_1": {
            "_type": "process",
            "inputs": {"left_hand_addend": ["A"], "right_hand_addend": ["B"]},
            "outputs": {"result": ["C"]},
        },
        "add_nums_2": {
            "_type": "process",
            "inputs": {"left_hand_addend": ["A"], "right_hand_addend": ["B"]},
            "outputs": {"result": ["C"]},
        },
    },
}


list_expected_config_template = {
    "composition": {
        "A": "float",
        "B": "float",
        "C": "float",
        "adders": {
            "add_nums_1": {
                "_type": "process",
                "address": {
                    "_type": "quote",
                    "_default": "local:!tests.fixtures.test_registry.toy_library.AddFloatsProcess",
                },
                "_inputs": {"left_hand_addend": "float", "right_hand_addend": "float"},
                "_outputs": {"result": "float"},
            },
            "add_nums_2": {
                "_type": "process",
                "address": {
                    "_type": "quote",
                    "_default": "local:!tests.fixtures.test_registry.toy_library.AddFloatsProcess",
                },
                "_inputs": {"left_hand_addend": "float", "right_hand_addend": "float"},
                "_outputs": {"result": "float"},
            },
        },
    },
    "state": {
        "A": 2.07,
        "B": 3.5,
        "adders": {
            "add_nums_1": {
                "_type": "process",
                "inputs": {"left_hand_addend": ["..", "A"], "right_hand_addend": ["..", "B"]},
                "outputs": {"result": ["..", "C"]},
            },
            "add_nums_2": {
                "_type": "process",
                "inputs": {"left_hand_addend": ["..", "A"], "right_hand_addend": ["..", "B"]},
                "outputs": {"result": ["..", "C"]},
            },
        },
    },
}


map_expected_config_template = {
    "composition": {
        "A": "float",
        "B": "float",
        "C": "float",
        "adders": {
            "_type": "map",
            "_value": {
                "_type": "process",
                "address": {
                    "_type": "quote",
                    "_default": "local:!tests.fixtures.test_registry.toy_library.AddFloatsProcess",
                },
                "_inputs": {"left_hand_addend": "float", "right_hand_addend": "float"},
                "_outputs": {"result": "float"},
            },
        },
    },
    "state": {
        "A": 2.07,
        "B": 3.5,
        "adders": {
            "add_nums_1": {
                "_type": "process",
                "inputs": {"left_hand_addend": ["..", "A"], "right_hand_addend": ["..", "B"]},
                "outputs": {"result": ["..", "C"]},
            },
            "add_nums_2": {
                "_type": "process",
                "inputs": {"left_hand_addend": ["..", "A"], "right_hand_addend": ["..", "B"]},
                "outputs": {"result": ["..", "C"]},
            },
        },
    },
}


def test_flat_initialization() -> None:
    flat_expected_config: dict[str, Any] = deepcopy(flat_expected_config_template)
    core = pg.ProcessTypes()
    core = pg.register_types(core)
    core.register_process("tests.fixtures.test_registry.toy_library.AddFloatsStep", AddFloatsStep)
    composite = pg.Composite(config=deepcopy(flat_expected_config), core=core)
    composite.run(10.0)
    assert np.allclose(composite.state["C"], (2.07 + 3.5) * 10 * 2)


def test_list_initialization() -> None:
    list_expected_config: dict[str, Any] = deepcopy(list_expected_config_template)
    core = pg.ProcessTypes()
    core = pg.register_types(core)
    core.register_process("tests.fixtures.test_registry.toy_library.AddFloatsStep", AddFloatsStep)
    composite = pg.Composite(config=deepcopy(list_expected_config), core=core)
    composite.run(10.0)
    assert np.allclose(composite.state["C"], (2.07 + 3.5) * 10 * 2)


def test_map_initialization() -> None:
    map_expected_config: dict[str, Any] = deepcopy(map_expected_config_template)
    core = pg.ProcessTypes()
    core = pg.register_types(core)
    core.register_process("tests.fixtures.test_registry.toy_library.AddFloatsStep", AddFloatsStep)
    composite = pg.Composite(config=deepcopy(map_expected_config), core=core)
    composite.run(10.0)
    assert np.allclose(composite.state["C"], (2.07 + 3.5) * 10 * 2)


def test_flat_generator() -> None:
    flattened_expected_config: dict[str, Any] = deepcopy(flat_expected_config_template)
    store_schema_A = PBStoreSchema(key="A", path=[], default_value=None, data_type="float")
    store_schema_B = PBStoreSchema(key="B", path=[], default_value=None, data_type="float")
    store_schema_C = PBStoreSchema(key="C", path=[], default_value=None, data_type="float")
    store_state_A = PBStoreState(key="A", path=[], value=2.07, store_schema=store_schema_A)
    store_state_B = PBStoreState(key="B", path=[], value=3.5, store_schema=store_schema_B)
    store_state_C = PBStoreState(key="C", path=[], value=None, store_schema=store_schema_C)
    process_schema_add_nums_1 = PBProcessSchema(
        key="add_nums_1",
        path=[],
        address="tests.fixtures.test_registry.toy_library.AddFloatsProcess",
        config_schema={},
        input_schema=dict(left_hand_addend="float", right_hand_addend="float"),
        output_schema=dict(result="float"),
        default_config_state={},
        default_input_state={},
        default_output_state={},
        collection_info=None,
    )
    process_state_add_nums_1 = PBProcessState(
        key="add_nums_1",
        path=[],
        address="tests.fixtures.test_registry.toy_library.AddFloatsProcess",
        config_state={},
        input_state=dict(left_hand_addend=["A"], right_hand_addend=["B"]),
        output_state=dict(result=["C"]),
        process_schema=process_schema_add_nums_1,
    )
    process_schema_add_nums_2 = PBProcessSchema(
        key="add_nums_2",
        path=[],
        address="tests.fixtures.test_registry.toy_library.AddFloatsProcess",
        config_schema={},
        input_schema=dict(left_hand_addend="float", right_hand_addend="float"),
        output_schema=dict(result="float"),
        default_config_state={},
        default_input_state={},
        default_output_state={},
        collection_info=None,
    )
    process_state_add_nums_2 = PBProcessState(
        key="add_nums_2",
        path=[],
        address="tests.fixtures.test_registry.toy_library.AddFloatsProcess",
        config_state={},
        input_state=dict(left_hand_addend=["A"], right_hand_addend=["B"]),
        output_state=dict(result=["C"]),
        process_schema=process_schema_add_nums_2,
    )
    pb_model = PBModel(
        store_schemas=[store_schema_A, store_schema_B, store_schema_C],
        store_states=[store_state_A, store_state_B, store_state_C],
        step_schemas=[],
        step_states=[],
        process_schemas=[process_schema_add_nums_1, process_schema_add_nums_2],
        process_states=[process_state_add_nums_1, process_state_add_nums_2],
        types=[],
    )
    generated_config: dict[str, Any] = assemble_pb(pb_model=pb_model)
    assert flattened_expected_config == generated_config

    core = pg.ProcessTypes()
    core = pg.register_types(core)
    core.register_process("tests.fixtures.test_registry.toy_library.addFloatsStep", AddFloatsStep)

    composite = pg.Composite(config=deepcopy(generated_config), core=core)
    composite.run(10)
    assert composite.state["A"] == 2.07
    assert composite.state["B"] == 3.5
    assert np.allclose(composite.state["C"], (2.07 + 3.5) * 10 * 2)


def test_list_generator() -> None:
    list_expected_config: dict[str, Any] = deepcopy(list_expected_config_template)
    store_schema_A = PBStoreSchema(key="A", path=[], default_value=None, data_type="float")
    store_schema_B = PBStoreSchema(key="B", path=[], default_value=None, data_type="float")
    store_schema_C = PBStoreSchema(key="C", path=[], default_value=None, data_type="float")
    store_state_A = PBStoreState(key="A", path=[], value=2.07, store_schema=store_schema_A)
    store_state_B = PBStoreState(key="B", path=[], value=3.5, store_schema=store_schema_B)
    store_state_C = PBStoreState(key="C", path=[], value=None, store_schema=store_schema_C)
    process_schema_add_nums_1 = PBProcessSchema(
        key="add_nums_1",
        path=["adders"],
        address="tests.fixtures.test_registry.toy_library.AddFloatsProcess",
        config_schema={},
        input_schema=dict(left_hand_addend="float", right_hand_addend="float"),
        output_schema=dict(result="float"),
        default_config_state={},
        default_input_state={},
        default_output_state={},
        collection_info=None,
    )
    process_state_add_nums_1 = PBProcessState(
        key="add_nums_1",
        path=["adders"],
        address="tests.fixtures.test_registry.toy_library.AddFloatsProcess",
        config_state={},
        input_state=dict(left_hand_addend=["..", "A"], right_hand_addend=["..", "B"]),
        output_state=dict(result=["..", "C"]),
        process_schema=process_schema_add_nums_1,
    )
    process_schema_add_nums_2 = PBProcessSchema(
        key="add_nums_2",
        path=["adders"],
        address="tests.fixtures.test_registry.toy_library.AddFloatsProcess",
        config_schema={},
        input_schema=dict(left_hand_addend="float", right_hand_addend="float"),
        output_schema=dict(result="float"),
        default_config_state={},
        default_input_state={},
        default_output_state={},
        collection_info=None,
    )
    process_state_add_nums_2 = PBProcessState(
        key="add_nums_2",
        path=["adders"],
        address="tests.fixtures.test_registry.toy_library.AddFloatsProcess",
        config_state={},
        input_state=dict(left_hand_addend=["..", "A"], right_hand_addend=["..", "B"]),
        output_state=dict(result=["..", "C"]),
        process_schema=process_schema_add_nums_2,
    )
    pb_model = PBModel(
        store_schemas=[store_schema_A, store_schema_B, store_schema_C],
        store_states=[store_state_A, store_state_B, store_state_C],
        step_schemas=[],
        step_states=[],
        process_schemas=[process_schema_add_nums_1, process_schema_add_nums_2],
        process_states=[process_state_add_nums_1, process_state_add_nums_2],
        types=[],
    )
    generated_config: dict[str, Any] = assemble_pb(pb_model=pb_model)
    assert list_expected_config == generated_config

    core = pg.ProcessTypes()
    core = pg.register_types(core)
    core.register_process("tests.fixtures.test_registry.toy_library.addFloatsStep", AddFloatsStep)

    composite = pg.Composite(config=deepcopy(generated_config), core=core)
    composite.run(10)
    assert composite.state["A"] == 2.07
    assert composite.state["B"] == 3.5
    assert np.allclose(composite.state["C"], (2.07 + 3.5) * 10 * 2)


def test_map_generator() -> None:
    map_expected_config: dict[str, Any] = deepcopy(map_expected_config_template)
    store_schema_A = PBStoreSchema(key="A", path=[], default_value=None, data_type="float")
    store_schema_B = PBStoreSchema(key="B", path=[], default_value=None, data_type="float")
    store_schema_C = PBStoreSchema(key="C", path=[], default_value=None, data_type="float")
    store_state_A = PBStoreState(key="A", path=[], value=2.07, store_schema=store_schema_A)
    store_state_B = PBStoreState(key="B", path=[], value=3.5, store_schema=store_schema_B)
    store_state_C = PBStoreState(key="C", path=[], value=None, store_schema=store_schema_C)
    process_schema_adders_map = PBProcessSchema(
        key="adders",
        path=[],
        address="tests.fixtures.test_registry.toy_library.AddFloatsProcess",
        config_schema={},
        input_schema=dict(left_hand_addend="float", right_hand_addend="float"),
        output_schema=dict(result="float"),
        default_config_state={},
        default_input_state={},
        default_output_state={},
        collection_info=PBCollectionType(coll_type="map"),
    )
    process_state_add_nums_1 = PBProcessState(
        key="add_nums_1",
        path=["adders"],
        address="tests.fixtures.test_registry.toy_library.AddFloatsProcess",
        config_state={},
        input_state=dict(left_hand_addend=["..", "A"], right_hand_addend=["..", "B"]),
        output_state=dict(result=["..", "C"]),
        process_schema=process_schema_adders_map,
    )
    process_state_add_nums_2 = PBProcessState(
        key="add_nums_2",
        path=["adders"],
        address="tests.fixtures.test_registry.toy_library.AddFloatsProcess",
        config_state={},
        input_state=dict(left_hand_addend=["..", "A"], right_hand_addend=["..", "B"]),
        output_state=dict(result=["..", "C"]),
        process_schema=process_schema_adders_map,
    )
    pb_model = PBModel(
        store_schemas=[store_schema_A, store_schema_B, store_schema_C],
        store_states=[store_state_A, store_state_B, store_state_C],
        step_schemas=[],
        step_states=[],
        process_schemas=[process_schema_adders_map],
        process_states=[process_state_add_nums_1, process_state_add_nums_2],
        types=[],
    )
    generated_config: dict[str, Any] = assemble_pb(pb_model=pb_model)
    assert map_expected_config == generated_config

    core = pg.ProcessTypes()
    core = pg.register_types(core)
    core.register_process("tests.fixtures.test_registry.toy_library.addFloatsStep", AddFloatsStep)

    composite = pg.Composite(config=deepcopy(generated_config), core=core)
    composite.run(10)
    assert composite.state["A"] == 2.07
    assert composite.state["B"] == 3.5
    assert np.allclose(composite.state["C"], (2.07 + 3.5) * 10 * 2)


flat_pblang = """
    type float builtin
    type string builtin

    proc Grow path tests.fixtures.test_registry.toy_library.AddFloatsProcess
        var left_hand_addend : float
        var right_hand_addend : float
        var result : float
        inputs left_hand_addend right_hand_addend
        outputs result

    store A: float = 2.07
    store B: float = 3.5
    store C: float
    store add_nums_1: update (C) using Grow[](A, B)
    store add_nums_2: update (C) using Grow[](A, B)
"""


def test_flat_parser() -> None:
    ast_model: ASTModel = langium_parse_pblang_str(flat_pblang)
    pb_model: PBModel = compile_ast(ast_model)  # remove reference to process instance
    pb_dict = assemble_pb(pb_model)
    assert flat_expected_config_template == pb_dict


list_pblang = """
    type float builtin
    type string builtin

    proc Grow path tests.fixtures.test_registry.toy_library.AddFloatsProcess
        var left_hand_addend : float
        var right_hand_addend : float
        var result : float
        inputs left_hand_addend right_hand_addend
        outputs result

    store A: float = 2.07
    store B: float = 3.5
    store C: float
    store adders: {
        add_nums_1: update (C) using Grow[](A, B),
        add_nums_2: update (C) using Grow[](A, B)
    }
"""


def test_list_parser() -> None:
    ast_model: ASTModel = langium_parse_pblang_str(list_pblang)
    pb_model: PBModel = compile_ast(ast_model)  # remove reference to process instance
    pb_dict = assemble_pb(pb_model)
    assert list_expected_config_template == pb_dict
