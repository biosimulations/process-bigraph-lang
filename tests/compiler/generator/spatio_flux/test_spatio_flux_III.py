from copy import deepcopy
from typing import Any

import numpy as np
import process_bigraph as pg  # type: ignore[import-untyped]

from process_bigraph_lang.compiler.converter import assemble_pb
from process_bigraph_lang.compiler.pb_model import PBStore, PBModel, PBProcess, PBStep
from tests.fixtures.test_registry.spatio_flux import register_types as spatio_flux_register_types


bounds = (10.0, 10.0)
bounds_as_str = ("10.0", "10.0")
n_bins = (10, 10)
n_bins_as_str = ("10", "10")
mol_ids = ["glucose", "acetate", "biomass"]
diffusion_rate = 1e-1
diffusion_dt = 1e-1
advection_coeffs = {"biomass": (0, -0.1)}

DIFF_ADVEC_PROCESS_ADDR = "tests.fixtures.test_registry.spatio_flux.processes.DiffusionAdvection"
step_config_template = {
    "composition": {
        "fields": {
            "acetate": {"_type": "array", "_shape": n_bins, "_data": "positive_float"},
            "biomass": {"_type": "array", "_shape": n_bins, "_data": "positive_float"},
            "glucose": {"_type": "array", "_shape": n_bins, "_data": "positive_float"},
        },
        "diffusion_advection": {
            "_type": "process",
            "address": {"_type": "quote", "_default": f"local:!{DIFF_ADVEC_PROCESS_ADDR}"},
            "_config": {
                "n_bins": "tuple[integer,integer]",
                "bounds": "tuple[float,float]",
                "default_diffusion_rate": {"_type": "float", "_default": 1e-1},
                "default_diffusion_dt": {"_type": "float", "_default": 1e-1},
                "diffusion_coeffs": "map[float]",
                "advection_coeffs": "map[tuple[float,float]]",
            },
            "_inputs": {
                "fields": {
                    "_type": "map",
                    "_value": {"_type": "array", "_shape": n_bins, "_data": "positive_float"},
                }
            },
            "_outputs": {
                "fields": {
                    "_type": "map",
                    "_value": {"_type": "array", "_shape": n_bins, "_data": "positive_float"},
                }
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
        "diffusion_advection": {
            "_type": "process",
            "config": {
                "n_bins": n_bins_as_str,
                "bounds": bounds,
                "default_diffusion_rate": diffusion_rate,
                "default_diffusion_dt": diffusion_dt,
                "advection_coeffs": advection_coeffs,
            },
            "inputs": {"fields": ["fields"]},
            "interval": 1.0,
            "outputs": {"fields": ["fields"]},
            # "shared": None,
        },
        "emitter": {
            "_type": "step",
            "config": {"emit": {"fields": "any", "global_time": "any"}},
            "inputs": {"fields": ["fields"], "global_time": ["global_time"]},
            # "outputs": None,
        },
        "fields": {
            "acetate": np.array(
                [
                    np.array(
                        [float(index_ace_1 + index_ace_0) / 20 for index_ace_1 in range(n_bins[1])], dtype=np.float64
                    )
                    for index_ace_0 in range(n_bins[0])
                ],
                dtype=np.float64,
            ),
            "biomass": np.array(
                [
                    np.array(
                        [float(index_bio_1 + index_bio_0) / 20 for index_bio_1 in range(n_bins[1])], dtype=np.float64
                    )
                    for index_bio_0 in range(n_bins[0])
                ],
                dtype=np.float64,
            ),
            "glucose": np.array(
                [
                    np.array(
                        [float(index_glu_1 + index_glu_0) / 20 for index_glu_1 in range(n_bins[1])], dtype=np.float64
                    )
                    for index_glu_0 in range(n_bins[0])
                ],
                dtype=np.float64,
            ),
        },
    },
}


def test_from_document() -> None:
    core = pg.ProcessTypes()
    core = pg.register_types(core)
    spatio_flux_register_types(core)

    config: dict[str, Any] = deepcopy(step_config_template)

    # construct and run the Step network (don't need to call composite.run(), executes in composite.initialize())
    composite = pg.Composite(config=config, core=core)
    composite.run(interval=120)

    # compare results
    results: dict = composite.state["fields"]
    for row in range(n_bins[0]):
        for col in range(n_bins[1]):
            # assert we're not still at initial conditions (unless it's the average, because diffusion)
            assert (
                float(results["acetate"][row][col]) != (row + col) / 20 or float(results["acetate"][row][col]) == 0.45
            )
            assert (
                float(results["biomass"][row][col]) != (row + col) / 20 or float(results["biomass"][row][col]) == 0.45
            )
            assert (
                float(results["glucose"][row][col]) != (row + col) / 20 or float(results["glucose"][row][col]) == 0.45
            )


def test_from_generator() -> None:
    store_fields_acetate = PBStore(
        key="acetate",
        path=["fields"],
        value=np.array(
            [
                np.array([float(index_ace_1 + index_ace_0) / 20 for index_ace_1 in range(n_bins[1])], dtype=np.float64)
                for index_ace_0 in range(n_bins[0])
            ],
            dtype=np.float64,
        ),
        data_type=dict(_type="array", _shape=n_bins, _data="positive_float"),
    )
    store_fields_biomass = PBStore(
        key="biomass",
        path=["fields"],
        value=np.array(
            [
                np.array([float(index_ace_1 + index_ace_0) / 20 for index_ace_1 in range(n_bins[1])], dtype=np.float64)
                for index_ace_0 in range(n_bins[0])
            ],
            dtype=np.float64,
        ),
        data_type=dict(_type="array", _shape=n_bins, _data="positive_float"),
    )
    store_fields_glucose = PBStore(
        key="glucose",
        path=["fields"],
        value=np.array(
            [
                np.array([float(index_ace_1 + index_ace_0) / 20 for index_ace_1 in range(n_bins[1])], dtype=np.float64)
                for index_ace_0 in range(n_bins[0])
            ],
            dtype=np.float64,
        ),
        data_type=dict(_type="array", _shape=n_bins, _data="positive_float"),
    )
    process_diffusion_advection = PBProcess(
        key="diffusion_advection",
        path=[],
        address=f"local:!{DIFF_ADVEC_PROCESS_ADDR}",
        config_schema=dict(
            n_bins="tuple[integer,integer]",
            bounds="tuple[float,float]",
            default_diffusion_rate=dict(_type="float", _default=1e-1),
            default_diffusion_dt=dict(_type="float", _default=1e-1),
            diffusion_coeffs="map[float]",
            advection_coeffs="map[tuple[float,float]]",
        ),
        input_schema=dict(fields=dict(_type="map", _value=dict(_type="array", _shape=n_bins, _data="positive_float"))),
        output_schema=dict(fields=dict(_type="map", _value=dict(_type="array", _shape=n_bins, _data="positive_float"))),
        config_state=dict(
            n_bins=n_bins_as_str,
            bounds=bounds,
            default_diffusion_rate=diffusion_rate,
            default_diffusion_dt=diffusion_dt,
            advection_coeffs=advection_coeffs,
        ),
        input_state=dict(fields=["fields"]),
        output_state=dict(fields=["fields"]),
        interval=1.0,
    )
    step_emitter = PBStep(
        key="emitter",
        path=[],
        address="local:ram-emitter",
        config_schema=dict(emit=dict(_type="map", _value="any")),
        input_schema=dict(_type="map", _value="any"),
        output_schema={},
        config_state=dict(emit=dict(fields="any", global_time="any")),
        input_state=dict(fields=["fields"], global_time=["global_time"]),
        output_state={},
    )
    pb_model = PBModel(
        stores=[store_fields_acetate, store_fields_biomass, store_fields_glucose],
        steps=[step_emitter],
        processes=[process_diffusion_advection],
        types=[],
    )
    generated_config: dict[str, Any] = assemble_pb(pb_model=pb_model)
    a = deepcopy(step_config_template)
    b = deepcopy(generated_config)
    a["state"]["fields"] = {}
    b["state"]["fields"] = {}
    assert a == b

    core = pg.ProcessTypes()
    core = pg.register_types(core)
    spatio_flux_register_types(core)

    # construct and run the Step network (don't need to call composite.run(), executes in composite.initialize())
    composite = pg.Composite(config=deepcopy(generated_config), core=core)
    composite.run(interval=120)

    # compare results
    results: dict = composite.state["fields"]
    for row in range(n_bins[0]):
        for col in range(n_bins[1]):
            # assert we're not still at initial conditions (unless it's the average, because diffusion)
            assert (
                float(results["acetate"][row][col]) != (row + col) / 20 or float(results["acetate"][row][col]) == 0.45
            )
            assert (
                float(results["biomass"][row][col]) != (row + col) / 20 or float(results["biomass"][row][col]) == 0.45
            )
            assert (
                float(results["glucose"][row][col]) != (row + col) / 20 or float(results["glucose"][row][col]) == 0.45
            )
