import tempfile
from copy import deepcopy
from pathlib import Path
from typing import Any

import process_bigraph as pg  # type: ignore[import-untyped]
from process_bigraph_lang.runtime.v2.generator import generate
from process_bigraph_lang.runtime.v2.pb_model import PBStore, PBStep, PBModel
from tests.fixtures.test_registry.toy_library import AddFloatsStep, SaveFloatToFileStep

add_floats_step_expected_config_template = {
    "composition": {
        "A": "float",
        "B": "float",
        "C": "float",
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


def test_add_floats_step_initialization() -> None:
    add_floats_step_expected_config: dict[str, Any] = deepcopy(add_floats_step_expected_config_template)
    with tempfile.TemporaryDirectory() as tmp_dirname:
        output_file_path = Path(tmp_dirname) / "output.txt"
        add_floats_step_expected_config["state"]["print_result"]["config"]["output_file_path"] = str(output_file_path)
        core = pg.ProcessTypes()
        core = pg.register_types(core)
        core.register_process("tests.fixtures.test_registry.toy_library.AddFloatsStep", AddFloatsStep)
        core.register_process("tests.fixtures.test_registry.toy_library.SaveFloatToFileStep", SaveFloatToFileStep)
        composite = pg.Composite(config=deepcopy(add_floats_step_expected_config), core=core)
        composite.run(0.0)
        assert composite.state["C"] == 2.07 + 3.5


def test_add_floats_generator() -> None:
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
            config={},
            inputs=dict(left_hand_addend=["A"], right_hand_addend=["B"]),
            outputs=dict(result=["C"]),
        )
        step_print_result = PBStep(
            key="print_result",
            path=[],
            address="local:!tests.fixtures.test_registry.toy_library.SaveFloatToFileStep",
            config=dict(output_file_path=str(output_file_path)),
            inputs=dict(result=["C"]),
            outputs={},
        )
        pb_model = PBModel(
            stores=[store_A, store_B, store_C],
            steps=[step_add_nums, step_print_result],
            processes=[],
            types=[],
            composite_defs=[],
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
