from copy import deepcopy
from typing import Any

import process_bigraph as pg  # type: ignore[import-untyped]

from process_bigraph_lang.compiler.converter import assemble_pb
from process_bigraph_lang.compiler.pb_model import PBStore, PBStep, PBModel

op_step_expected_config = {
    "composition": {
        "A": "float",
        "B": "float",
        "C": "float",
        "D": "float",
    },
    "state": {
        "A": 13,
        "B": 21,
        "step1": {
            "_type": "step",
            "address": "local:!process_bigraph.tests.OperatorStep",
            "config": {"operator": "+"},
            "inputs": {"a": ["A"], "b": ["B"]},
            "outputs": {"c": ["C"]},
        },
        "step2": {
            "_type": "step",
            "address": "local:!process_bigraph.tests.OperatorStep",
            "config": {"operator": "*"},
            "inputs": {"a": ["B"], "b": ["C"]},
            "outputs": {"c": ["D"]},
        },
    },
}


def test_op_step_initialization() -> None:
    core = pg.ProcessTypes()
    core = pg.register_types(core)
    composite = pg.Composite(config=deepcopy(op_step_expected_config), core=core)
    composite.run(0.0)
    assert composite.state["D"] == (13 + 21) * 21


def test_op_step_generator() -> None:
    store_A = PBStore(key="A", path=[], value=13, data_type="float")
    store_B = PBStore(key="B", path=[], value=21, data_type="float")
    store_C = PBStore(key="C", path=[], value=None, data_type="float")
    store_D = PBStore(key="D", path=[], value=None, data_type="float")
    step_step1 = PBStep(
        key="step1",
        path=[],
        address="local:!process_bigraph.tests.OperatorStep",
        config_schema={},
        input_schema={},
        output_schema={},
        config_state=dict(operator="+"),
        input_state=dict(a=["A"], b=["B"]),
        output_state=dict(c=["C"]),
    )
    step_step2 = PBStep(
        key="step2",
        path=[],
        address="local:!process_bigraph.tests.OperatorStep",
        config_schema={},
        input_schema={},
        output_schema={},
        config_state=dict(operator="*"),
        input_state=dict(a=["B"], b=["C"]),
        output_state=dict(c=["D"]),
    )

    pb_model = PBModel(
        stores=[store_A, store_B, store_C, store_D],
        steps=[step_step1, step_step2],
        processes=[],
        types=[],
    )
    generated_config: dict[str, Any] = assemble_pb(pb_model=pb_model)
    assert op_step_expected_config == generated_config

    core = pg.ProcessTypes()
    core = pg.register_types(core)
    composite = pg.Composite(config=deepcopy(generated_config), core=core)
    composite.run(0.0)
    assert composite.state["A"] == 13
    assert composite.state["B"] == 21
    assert composite.state["C"] == (13 + 21)
    assert composite.state["D"] == 21 * (13 + 21)
