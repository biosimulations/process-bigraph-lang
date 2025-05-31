from copy import deepcopy
from typing import Any

import process_bigraph as pg  # type: ignore[import-untyped]

from process_bigraph_lang.compiler.converter import assemble_pb
from process_bigraph_lang.compiler.pb_model import PBStoreSchema, PBStoreState, PBStepSchema, PBStepState, PBModel

op_step_expected_config = {
    "composition": {
        "A": "float",
        "B": "float",
        "C": "float",
        "D": "float",
        "step1": {
            "_type": "step",
            "address": {
                "_type": "quote",
                "_default": "local:!process_bigraph.tests.OperatorStep",
            },
            "_config": {"operator": "string"},
            "_inputs": {"a": "float", "b": "float"},
            "_outputs": {"c": "float"},
        },
        "step2": {
            "_type": "step",
            "address": {
                "_type": "quote",
                "_default": "local:!process_bigraph.tests.OperatorStep",
            },
            "_config": {"operator": "string"},
            "_inputs": {"a": "float", "b": "float"},
            "_outputs": {"c": "float"},
        },
    },
    "state": {
        "A": 13,
        "B": 21,
        "step1": {
            "_type": "step",
            "config": {"operator": "+"},
            "inputs": {"a": ["A"], "b": ["B"]},
            "outputs": {"c": ["C"]},
        },
        "step2": {
            "_type": "step",
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
    store_schema_A = PBStoreSchema(key="A", path=[], default_value=None, data_type="float")
    store_schema_B = PBStoreSchema(key="B", path=[], default_value=None, data_type="float")
    store_schema_C = PBStoreSchema(key="C", path=[], default_value=None, data_type="float")
    store_schema_D = PBStoreSchema(key="D", path=[], default_value=None, data_type="float")
    store_state_A = PBStoreState(key="A", path=[], value=13, store_schema=store_schema_A)
    store_state_B = PBStoreState(key="B", path=[], value=21, store_schema=store_schema_B)
    store_state_C = PBStoreState(key="C", path=[], value=None, store_schema=store_schema_C)
    store_state_D = PBStoreState(key="D", path=[], value=None, store_schema=store_schema_D)
    step_schema_step1 = PBStepSchema(
        key="step1",
        path=[],
        address="local:!process_bigraph.tests.OperatorStep",
        config_schema=dict(operator="string"),
        input_schema=dict(a="float", b="float"),
        output_schema=dict(c="float"),
        default_config_state={},
        default_input_state={},
        default_output_state={},
        collection_info=None,
    )
    step_state_step1 = PBStepState(
        key="step1",
        path=[],
        address="local:!process_bigraph.tests.OperatorStep",
        config_state=dict(operator="+"),
        input_state=dict(a=["A"], b=["B"]),
        output_state=dict(c=["C"]),
        step_schema=step_schema_step1,
    )
    step_schema_step2 = PBStepSchema(
        key="step2",
        path=[],
        address="local:!process_bigraph.tests.OperatorStep",
        config_schema=dict(operator="string"),
        input_schema=dict(a="float", b="float"),
        output_schema=dict(c="float"),
        default_config_state={},
        default_input_state={},
        default_output_state={},
        collection_info=None,
    )
    step_state_step2 = PBStepState(
        key="step2",
        path=[],
        address="local:!process_bigraph.tests.OperatorStep",
        config_state=dict(operator="*"),
        input_state=dict(a=["B"], b=["C"]),
        output_state=dict(c=["D"]),
        step_schema=step_schema_step2,
    )

    pb_model = PBModel(
        store_schemas=[store_schema_A, store_schema_B, store_schema_C, store_schema_D],
        store_states=[store_state_A, store_state_B, store_state_C, store_state_D],
        step_schemas=[step_schema_step1, step_schema_step2],
        step_states=[step_state_step1, step_state_step2],
        process_schemas=[],
        process_states=[],
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
