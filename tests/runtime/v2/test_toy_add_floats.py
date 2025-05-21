import tempfile
from copy import deepcopy
from pathlib import Path
from typing import Any

import process_bigraph as pg  # type: ignore[import-untyped]
from process_bigraph_lang.dsl.ast_model import ASTModel
from process_bigraph_lang.main import generate_model_ast
from process_bigraph_lang.runtime.v2.generator import generate
from process_bigraph_lang.runtime.v2.pb_model import PBStore, PBStep, PBModel, PBProcess
from tests.fixtures.test_registry.toy_library import AddFloatsStep, SaveFloatToFileStep
from process_bigraph_lang.runtime.v2.compiler import compile as pblang_compiler

add_floats_step_expected_config_template = {
    "composition": {
        "A": "float",
        "B": "float",
        "C": "float",
        # "out_path": "path",
        # "add_nums": {
        #     "_type": "step",
        #     "address": "local:!tests.fixtures.test_registry.toy_library.AddFloatsStep",
        #     "inputs": {"left_hand_addend": "float", "right_hand_addend": "float"},
        #     "outputs": {"result": "float"},
        # },
        # "print_result": {
        #     "_type": "step",
        #     "address": "local:!tests.fixtures.test_registry.toy_library.SaveFloatToFileStep",
        #     "config": {"output_file_path": "string"},
        #     "inputs": {"result": "float"},
        # },
    },
    "state": {
        "A": 2.07,
        "B": 3.5,
        "add_nums": {
            "_type": "step",
            "address": "local:!tests.fixtures.test_registry.toy_library.AddFloatsStep",
            "inputs": {"left_hand_addend": ["A"], "right_hand_addend": ["B"]},
            "outputs": {"result": ["C"]},
        },
        "print_result": {
            "_type": "step",
            "address": "local:!tests.fixtures.test_registry.toy_library.SaveFloatToFileStep",
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
        # "add_nums": {
        #     "_type": "process",
        #     "address": "local:!tests.fixtures.test_registry.toy_library.AddFloatsProcess",
        #     "inputs": {"left_hand_addend": "float", "right_hand_addend": "float"},
        #     "outputs": {"result": "float"},
        # },
        # "print_result": {
        #     "_type": "step",
        #     "address": "local:!tests.fixtures.test_registry.toy_library.SaveFloatToFileStep",
        #     "config": {"output_file_path": "string"},
        #     "inputs": {"result": "float"},
        # },
    },
    "state": {
        "A": 2.07,
        "B": 3.5,
        "add_nums": {
            "_type": "process",
            "address": "local:!tests.fixtures.test_registry.toy_library.AddFloatsProcess",
            "inputs": {"left_hand_addend": ["A"], "right_hand_addend": ["B"]},
            "outputs": {"result": ["C"]},
        },
        "print_result": {
            "_type": "step",
            "address": "local:!tests.fixtures.test_registry.toy_library.SaveFloatToFileStep",
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

        store_A = PBStore(key="A", path=[], value=2.07, data_type="float")
        store_B = PBStore(key="B", path=[], value=3.5, data_type="float")
        store_C = PBStore(key="C", path=[], value=None, data_type="float")
        step_add_nums = PBStep(
            key="add_nums",
            path=[],
            address="local:!tests.fixtures.test_registry.toy_library.AddFloatsStep",
            config_schema={},
            input_schema={},
            output_schema={},
            config_state={},
            input_state=dict(left_hand_addend=["A"], right_hand_addend=["B"]),
            output_state=dict(result=["C"]),
        )
        step_print_result = PBStep(
            key="print_result",
            path=[],
            address="local:!tests.fixtures.test_registry.toy_library.SaveFloatToFileStep",
            config_schema={},
            input_schema={},
            output_schema={},
            config_state=dict(output_file_path=str(output_file_path)),
            input_state=dict(result=["C"]),
            output_state={},
        )
        pb_model = PBModel(
            stores=[store_A, store_B, store_C],
            steps=[step_add_nums, step_print_result],
            processes=[],
            types=[],
        )
        generated_config: dict[str, Any] = generate(pb_model=pb_model)
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

        store_A = PBStore(key="A", path=[], value=2.07, data_type="float")
        store_B = PBStore(key="B", path=[], value=3.5, data_type="float")
        store_C = PBStore(key="C", path=[], value=None, data_type="float")
        process_add_nums = PBProcess(
            key="add_nums",
            path=[],
            address="tests.fixtures.test_registry.toy_library.AddFloatsProcess",
            config_schema={},
            input_schema={},
            output_schema={},
            config_state={},
            input_state=dict(left_hand_addend=["A"], right_hand_addend=["B"]),
            output_state=dict(result=["C"]),
        )
        step_print_result = PBStep(
            key="print_result",
            path=[],
            address="tests.fixtures.test_registry.toy_library.SaveFloatToFileStep",
            config_schema={},
            input_schema={},
            output_schema={},
            config_state=dict(output_file_path=str(output_file_path)),
            input_state=dict(result=["C"]),
            output_state={},
        )
        pb_model = PBModel(
            stores=[store_A, store_B, store_C],
            steps=[step_print_result],
            processes=[process_add_nums],
            types=[],
        )
        generated_config: dict[str, Any] = generate(pb_model=pb_model)
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
        ast_model: ASTModel = generate_model_ast(model_pblang_path)
        pb_model: PBModel = pblang_compiler(ast_model)  # remove reference to process instance
        pb_dict = generate(pb_model)
        assert add_floats_step_expected_config_template == pb_dict
