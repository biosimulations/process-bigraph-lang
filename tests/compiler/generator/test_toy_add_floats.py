import tempfile
from copy import deepcopy
from pathlib import Path
from typing import Any

import process_bigraph as pg  # type: ignore[import-untyped]

from process_bigraph_lang.compiler.generator import compile_ast
from process_bigraph_lang.compiler.converter import assemble_pb
from process_bigraph_lang.compiler.pb_model import (
    PBStoreSchema,
    PBStoreState,
    PBStepSchema,
    PBStepState,
    PBModel,
    PBProcessSchema,
    PBProcessState,
)
from process_bigraph_lang.dsl.ast_model import ASTModel
from process_bigraph_lang.dsl.langium_pblang import langium_parse_pblang_file
from tests.fixtures.test_registry.toy_library import AddFloatsStep, SaveFloatToFileStep

add_floats_step_expected_config_template = {
    "composition": {
        "A": "float",
        "B": "float",
        "C": "float",
        "add_nums": {
            "_type": "step",
            "address": {"_type": "quote", "_default": "local:!tests.fixtures.test_registry.toy_library.AddFloatsStep"},
            "_inputs": {"left_hand_addend": "float", "right_hand_addend": "float"},
            "_outputs": {"result": "float"},
        },
        "print_result": {
            "_type": "step",
            "address": {
                "_type": "quote",
                "_default": "local:!tests.fixtures.test_registry.toy_library.SaveFloatToFileStep",
            },
            "_config": {"output_file_path": "string"},
            "_inputs": {"result": "float"},
        },
    },
    "state": {
        "A": 2.07,
        "B": 3.5,
        "add_nums": {
            "_type": "step",
            "inputs": {"left_hand_addend": ["A"], "right_hand_addend": ["B"]},
            "outputs": {"result": ["C"]},
        },
        "print_result": {
            "_type": "step",
            "config": {"output_file_path": "output.txt"},
            "inputs": {"result": ["C"]},
        },
    },
}

add_floats_process_expected_config_template = {
    "composition": {
        "A": "float",
        "B": "float",
        "C": "float",
        "add_nums": {
            "_type": "process",
            "address": {
                "_type": "quote",
                "_default": "local:!tests.fixtures.test_registry.toy_library.AddFloatsProcess",
            },
            "_inputs": {"left_hand_addend": "float", "right_hand_addend": "float"},
            "_outputs": {"result": "float"},
        },
        "print_result": {
            "_type": "step",
            "address": {
                "_type": "quote",
                "_default": "local:!tests.fixtures.test_registry.toy_library.SaveFloatToFileStep",
            },
            "_config": {"output_file_path": "string"},
            "_inputs": {"result": "float"},
        },
    },
    "state": {
        "A": 2.07,
        "B": 3.5,
        "add_nums": {
            "_type": "process",
            "inputs": {"left_hand_addend": ["A"], "right_hand_addend": ["B"]},
            "outputs": {"result": ["C"]},
        },
        "print_result": {
            "_type": "step",
            "config": {"output_file_path": "output.txt"},
            "inputs": {"result": ["C"]},
        },
    },
}


def test_add_floats_step_initialization() -> None:
    add_floats_step_expected_config: dict[str, Any] = deepcopy(add_floats_step_expected_config_template)
    with tempfile.TemporaryDirectory() as tmp_dirname:
        output_file_path = Path(tmp_dirname) / "output.txt"
        add_floats_step_expected_config["state"]["out_path"] = output_file_path
        core = pg.ProcessTypes()
        core = pg.register_types(core)
        core.register_process("tests.fixtures.test_registry.toy_library.AddFloatsStep", AddFloatsStep)
        core.register_process("tests.fixtures.test_registry.toy_library.SaveFloatToFileStep", SaveFloatToFileStep)
        composite = pg.Composite(config=deepcopy(add_floats_step_expected_config), core=core)
        composite.run(0.0)
        assert composite.state["C"] == 2.07 + 3.5


def test_add_floats_step_generator() -> None:
    add_floats_step_expected_config: dict[str, Any] = deepcopy(add_floats_step_expected_config_template)
    with tempfile.TemporaryDirectory() as tmp_dirname:
        output_file_path = Path(tmp_dirname) / "output.txt"
        add_floats_step_expected_config["state"]["print_result"]["config"]["output_file_path"] = str(output_file_path)

        store_schema_A = PBStoreSchema(key="A", path=[], default_value=None, data_type="float")
        store_schema_B = PBStoreSchema(key="B", path=[], default_value=None, data_type="float")
        store_schema_C = PBStoreSchema(key="C", path=[], default_value=None, data_type="float")
        store_state_A = PBStoreState(key="A", path=[], value=2.07, store_schema=store_schema_A)
        store_state_B = PBStoreState(key="B", path=[], value=3.5, store_schema=store_schema_B)
        store_state_C = PBStoreState(key="C", path=[], value=None, store_schema=store_schema_C)
        step_schema_add_nums = PBStepSchema(
            key="add_nums",
            path=[],
            address="local:!tests.fixtures.test_registry.toy_library.AddFloatsStep",
            config_schema={},
            input_schema=dict(left_hand_addend="float", right_hand_addend="float"),
            output_schema=dict(result="float"),
            default_config_state={},
            default_input_state={},
            default_output_state={},
            collection_info=None,
        )
        step_state_add_nums = PBStepState(
            key="add_nums",
            path=[],
            address="local:!tests.fixtures.test_registry.toy_library.AddFloatsStep",
            config_state={},
            input_state=dict(left_hand_addend=["A"], right_hand_addend=["B"]),
            output_state=dict(result=["C"]),
            step_schema=step_schema_add_nums,
        )
        step_schema_print_result = PBStepSchema(
            key="print_result",
            path=[],
            address="local:!tests.fixtures.test_registry.toy_library.SaveFloatToFileStep",
            config_schema=dict(output_file_path="string"),
            input_schema=dict(result="float"),
            output_schema={},
            default_config_state={},
            default_input_state={},
            default_output_state={},
            collection_info=None,
        )
        step_state_print_result = PBStepState(
            key="print_result",
            path=[],
            address="local:!tests.fixtures.test_registry.toy_library.SaveFloatToFileStep",
            config_state=dict(output_file_path=str(output_file_path)),
            input_state=dict(result=["C"]),
            output_state={},
            step_schema=step_schema_print_result,
        )
        pb_model = PBModel(
            store_schemas=[store_schema_A, store_schema_B, store_schema_C],
            store_states=[store_state_A, store_state_B, store_state_C],
            step_schemas=[step_schema_add_nums, step_schema_print_result],
            step_states=[step_state_add_nums, step_state_print_result],
            process_schemas=[],
            process_states=[],
            types=[],
        )
        generated_config: dict[str, Any] = assemble_pb(pb_model=pb_model)
        assert add_floats_step_expected_config == generated_config

        core = pg.ProcessTypes()
        core = pg.register_types(core)
        core.register_process("tests.fixtures.test_registry.toy_library.addFloatsStep", AddFloatsStep)
        core.register_process("tests.fixtures.test_registry.toy_library.SaveFloatToFileStep", SaveFloatToFileStep)

        composite = pg.Composite(config=deepcopy(generated_config), core=core)
        composite.run(0.0)
        assert composite.state["A"] == 2.07
        assert composite.state["B"] == 3.5
        assert composite.state["C"] == 2.07 + 3.5


def test_add_floats_process_initialization() -> None:
    add_floats_step_expected_config: dict[str, Any] = deepcopy(add_floats_process_expected_config_template)
    with tempfile.TemporaryDirectory() as tmp_dirname:
        output_file_path = Path(tmp_dirname) / "output.txt"
        add_floats_step_expected_config["state"]["print_result"]["config"]["output_file_path"] = str(output_file_path)
        core = pg.ProcessTypes()
        core = pg.register_types(core)
        core.register_process("tests.fixtures.test_registry.toy_library.AddFloatsStep", AddFloatsStep)
        core.register_process("tests.fixtures.test_registry.toy_library.SaveFloatToFileStep", SaveFloatToFileStep)
        composite = pg.Composite(config=deepcopy(add_floats_step_expected_config), core=core)
        composite.run(10.0)
        assert composite.state["C"] == (2.07 + 3.5) * 10


def test_add_floats_process_generator() -> None:
    add_floats_step_expected_config: dict[str, Any] = deepcopy(add_floats_process_expected_config_template)
    with tempfile.TemporaryDirectory() as tmp_dirname:
        output_file_path = Path(tmp_dirname) / "output.txt"
        add_floats_step_expected_config["state"]["print_result"]["config"]["output_file_path"] = str(output_file_path)

        store_schema_A = PBStoreSchema(key="A", path=[], default_value=None, data_type="float")
        store_schema_B = PBStoreSchema(key="B", path=[], default_value=None, data_type="float")
        store_schema_C = PBStoreSchema(key="C", path=[], default_value=None, data_type="float")
        store_state_A = PBStoreState(key="A", path=[], value=2.07, store_schema=store_schema_A)
        store_state_B = PBStoreState(key="B", path=[], value=3.5, store_schema=store_schema_B)
        store_state_C = PBStoreState(key="C", path=[], value=None, store_schema=store_schema_C)
        process_schema_add_nums = PBProcessSchema(
            key="add_nums",
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
        process_state_add_nums = PBProcessState(
            key="add_nums",
            path=[],
            address="tests.fixtures.test_registry.toy_library.AddFloatsProcess",
            config_state={},
            input_state=dict(left_hand_addend=["A"], right_hand_addend=["B"]),
            output_state=dict(result=["C"]),
            process_schema=process_schema_add_nums,
        )
        step_schema_print_result = PBStepSchema(
            key="print_result",
            path=[],
            address="tests.fixtures.test_registry.toy_library.SaveFloatToFileStep",
            config_schema=dict(output_file_path="string"),
            input_schema=dict(result="float"),
            output_schema={},
            default_config_state={},
            default_input_state={},
            default_output_state={},
            collection_info=None,
        )
        step_state_print_result = PBStepState(
            key="print_result",
            path=[],
            address="tests.fixtures.test_registry.toy_library.SaveFloatToFileStep",
            config_state=dict(output_file_path=str(output_file_path)),
            input_state=dict(result=["C"]),
            output_state={},
            step_schema=step_schema_print_result,
        )
        pb_model = PBModel(
            store_schemas=[store_schema_A, store_schema_B, store_schema_C],
            store_states=[store_state_A, store_state_B, store_state_C],
            step_schemas=[step_schema_print_result],
            step_states=[step_state_print_result],
            process_schemas=[process_schema_add_nums],
            process_states=[process_state_add_nums],
            types=[],
        )
        generated_config: dict[str, Any] = assemble_pb(pb_model=pb_model)
        assert add_floats_step_expected_config == generated_config

        core = pg.ProcessTypes()
        core = pg.register_types(core)
        core.register_process("tests.fixtures.test_registry.toy_library.addFloatsStep", AddFloatsStep)
        core.register_process("tests.fixtures.test_registry.toy_library.SaveFloatToFileStep", SaveFloatToFileStep)

        composite = pg.Composite(config=deepcopy(generated_config), core=core)
        composite.run(10)
        assert composite.state["A"] == 2.07
        assert composite.state["B"] == 3.5
        assert composite.state["C"] == (2.07 + 3.5) * 10


add_floats_step_pblang = """
    type float builtin
    type string builtin

    step add_nums path tests.fixtures.test_registry.toy_library.AddFloatsStep
        var left_hand_addend : float
        var right_hand_addend : float
        var result : float
        inputs left_hand_addend right_hand_addend
        outputs result

    step print_result path tests.fixtures.test_registry.toy_library.SaveFloatToFileStep
        param output_file_path: string
        var result : float
        inputs result

    param out_path: string = "output.txt"
    store A: float = 2.07
    store B: float = 3.5
    store C: float

    set (C) as add_nums[](A, B)
    set () as print_result[out_path](C)
"""


def test_add_floats_parser() -> None:
    with tempfile.TemporaryDirectory() as tmp_dirname:
        model_pblang_path = Path(tmp_dirname) / "model.pblang"
        with open(model_pblang_path, "w") as file:
            file.write(add_floats_step_pblang)
        ast_model: ASTModel = langium_parse_pblang_file(model_pblang_path)
        pb_model: PBModel = compile_ast(ast_model)  # remove reference to process instance
        pb_dict = assemble_pb(pb_model)
        assert add_floats_step_expected_config_template == pb_dict
