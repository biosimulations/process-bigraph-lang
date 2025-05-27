from copy import deepcopy
from pathlib import Path
from typing import Any

import numpy as np
import process_bigraph as pg  # type: ignore[import-untyped]

from process_bigraph_lang.compiler.converter import assemble_pb
from process_bigraph_lang.compiler.pb_model import PBStore, PBStep, PBModel
from tests.fixtures.test_registry.tellurium import TelluriumStep

TELLURIUM_STEP_ADDR = f"{TelluriumStep.__module__}.{TelluriumStep.__qualname__}"
step_config_template = {
    "composition": {
        "results_store": {"result_array": "array[(10|4),float]", "result_labels": "list[string]"},
        "run_time_store": "float",
        "start_time_store": "float",
        "tellurium": {
            "_type": "step",
            "address": {"_type" : "quote","_default" : f"local:{TELLURIUM_STEP_ADDR}"},
            "_config": {"sbml_model_path": "string","antimony_string": "string", "num_steps": "integer"},
            "_inputs": { "time": "float", "run_time": "float"},
            "_outputs": {
                "results": {
                    "result_array": "array[(10|4),float]",
                    "result_labels": "list[string]",
                },
            },
        },
        "emitter": {
            "_type": "step",
            "address": {"_type": "quote", "_default": "local:ram-emitter"},
            "_config": {"emit": {"_type": "map", "_value": "any"}},
            "_inputs": {"_type": "map", "_value": "any"},
        },

    },
    "state": {
        "start_time_store": 0.0,
        "run_time_store": 10.0,
        "tellurium": {
            "_type": "step",
            "config": {
                "sbml_model_path": "",
                "num_steps": 10,
            },
            "inputs": {
                "time": ["start_time_store"],
                "run_time": ["run_time_store"],
            },
            "outputs": {
                "results": ["results_store"],
            },
        },
        "emitter": {
            "_type": "step",
            "config": {
                "emit": {
                    "floating_species": "tree[float]",
                    "time": "float",
                },
            },
            "inputs": {
                "floating_species": ["floating_species_store"],
                "time": ["start_time_store"],
            },
        },
    },
}


def test_tellurium_step(sbml_path_caravagna2010: Path) -> None:
    core = pg.ProcessTypes()
    core = pg.register_types(core)

    config: dict[str, Any] = deepcopy(step_config_template)
    config["state"]["tellurium"]["config"]["sbml_model_path"] = str(sbml_path_caravagna2010)

    core.register_process(TELLURIUM_STEP_ADDR, TelluriumStep)

    # construct and run the Step network (don't need to call composite.run(), executes in composite.initialize())
    composite = pg.Composite(config=config, core=core)

    # compare results
    expected_array = np.array(
        [
            [0.00000000e00, 1.00000000e00, 1.00000000e00, 1.00000000e00],
            [1.11111111e00, 1.22139854e00, 9.91424317e-01, 7.30381017e-05],
            [2.22222222e00, 1.49181442e00, 9.88489441e-01, 7.07013044e-05],
            [3.33333333e00, 1.82210000e00, 9.92197067e-01, 8.66141627e-05],
            [4.44444444e00, 2.22551055e00, 1.00377879e00, 1.06933141e-04],
            [5.55555556e00, 2.71823565e00, 1.02474669e00, 1.33203548e-04],
            [6.66666667e00, 3.32005101e00, 1.05695535e00, 1.67618426e-04],
            [7.77777778e00, 4.05510603e00, 1.10267689e00, 2.13314251e-04],
            [8.88888889e00, 4.95289849e00, 1.16469371e00, 2.74811708e-04],
            [1.00000000e01, 6.04945927e00, 1.24641134e00, 3.58663961e-04],
        ],
        dtype=np.float64,
    )
    observed_array = np.array(composite.state["results_store"]["result_array"], dtype=np.float64)
    assert observed_array.shape == expected_array.shape
    assert np.allclose(observed_array, expected_array)
    assert composite.state["results_store"]["result_labels"] == ["time", "T", "E", "I"]


def test_generator_tellurium_steps() -> None:
    store_start_time = PBStore(key="start_time_store", path=[], value=0.0, data_type="float")
    store_run_time = PBStore(key="run_time_store", path=[], value=10.0, data_type="float")
    store_result_array = PBStore(
        key="result_array", path=["results_store"], value=None, data_type="array[(10|4),float]"
    )
    store_result_labels = PBStore(key="result_labels", path=["results_store"], value=None, data_type="list[string]")
    step_tellurium = PBStep(
        key="tellurium",
        path=[],
        address=f"local:{TELLURIUM_STEP_ADDR}",
        config_schema=dict(sbml_model_path="string", antimony_string="string", num_steps="integer"),
        input_schema=dict(time="float", run_time="float"),
        output_schema=dict(results=dict(result_array="array[(10|4),float]",result_labels="list[string]")),
        config_state=dict(sbml_model_path="", num_steps=10),
        input_state=dict(time=["start_time_store"], run_time=["run_time_store"]),
        output_state=dict(results=["results_store"]),
    )
    ram_emitter = PBStep(
        key="emitter",
        path=[],
        address="local:ram-emitter",
        config_schema=dict(emit=dict(_type="map", _value="any")),
        input_schema=dict(_type="map", _value="any"),
        output_schema={},
        config_state=dict(emit=dict(floating_species="tree[float]",time="float")),
        input_state=dict(floating_species=["floating_species_store"], time=["start_time_store"]),
        output_state={},
    )

    pb_model = PBModel(
        stores=[store_start_time, store_run_time, store_result_array, store_result_labels],
        steps=[step_tellurium, ram_emitter],
        processes=[],
        types=[],
    )
    generated_config: dict[str, Any] = assemble_pb(pb_model=pb_model)
    assert step_config_template == generated_config
