from copy import deepcopy
from typing import Any


import process_bigraph as pg  # type: ignore[import-untyped]

from process_bigraph_lang.compiler.converter import assemble_pb
from process_bigraph_lang.compiler.pb_model import PBStore, PBModel, PBProcess, PBStep
from tests.fixtures.test_registry.spatio_flux_library import apply_to_core as apply_spatio_types_and_processes_to_core

D_FBA_PROCESS_ADDR = "spatio_flux.processes.DynamicFBA"
step_config_template = {
    "composition": {
        "fields": {"acetate": "positive_float", "biomass": "positive_float", "glucose": "positive_float"},
        "dFBA": {
            "_type": "process",
            "address": {"_type": "quote", "_default": f"local:!{D_FBA_PROCESS_ADDR}"},
            "_config": {
                "model_file": "string",
                "kinetic_params": "map[tuple[float,float]]",
                "substrate_update_reactions": "map[string]",
                "biomass_identifier": "string",
                "bounds": "map[bounds]",
            },
            "_inputs": {"substrates": {"_type": "map", "_value": "positive_float"}},
            "_outputs": {"substrates": {"_type": "map", "_value": "positive_float"}},
        },
        "emitter": {
            "_type": "step",
            "address": {"_type": "quote", "_default": "local:ram-emitter"},
            "_config": {"emit": {"_type": "map", "_value": "any"}},
            "_inputs": {"_type": "map", "_value": "any"},
        },
    },
    "state": {
        "dFBA": {
            "_type": "process",
            "config": {
                "biomass_identifier": "biomass",
                "bounds": {"ATPM": {"lower": 1.0, "upper": 1.0}, "EX_o2_e": {"lower": -2.0, "upper": None}},
                "kinetic_params": {"acetate": (0.5, 2.0), "glucose": (0.5, 1.0)},
                "model_file": "textbook",
                "substrate_update_reactions": {"acetate": "EX_ac_e", "glucose": "EX_glc__D_e"},
            },
            "inputs": {
                "substrates": {
                    "acetate": ["fields", "acetate"],
                    "biomass": ["fields", "biomass"],
                    "glucose": ["fields", "glucose"],
                }
            },
            "interval": 1.0,
            "outputs": {
                "substrates": {
                    "acetate": ["fields", "acetate"],
                    "biomass": ["fields", "biomass"],
                    "glucose": ["fields", "glucose"],
                }
            },
            # "shared": None,
        },
        "emitter": {
            "_type": "step",
            "config": {"emit": {"fields": "any", "global_time": "any"}},
            "inputs": {"fields": ["fields"], "global_time": ["global_time"]},
            # "outputs": None,
        },
        "fields": {"acetate": 0.807561836566412, "biomass": 0.1, "glucose": 10},
    },
}


def test_spatio_flux_one_from_document() -> None:
    core = pg.ProcessTypes()
    core = pg.register_types(core)
    apply_spatio_types_and_processes_to_core(core)

    config: dict[str, Any] = deepcopy(step_config_template)

    # construct and run the Step network (don't need to call composite.run(), executes in composite.initialize())
    composite = pg.Composite(config=config, core=core)
    composite.run(interval=60)

    # compare results
    results: dict = composite.state["fields"]
    assert float(results["acetate"]) == 0.0
    assert float(results["biomass"]) == 0.987918808708276
    assert float(results["glucose"]) == 0.0


def test_spatio_flux_one_from_generator() -> None:
    store_fields_acetate = PBStore(key="acetate", path=["fields"], value=0.807561836566412, data_type="positive_float")
    store_fields_biomass = PBStore(key="biomass", path=["fields"], value=0.1, data_type="positive_float")
    store_fields_glucose = PBStore(key="glucose", path=["fields"], value=10, data_type="positive_float")
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
    process_dFBA = PBProcess(
        key="dFBA",
        path=[],
        address="spatio_flux.processes.DynamicFBA",
        config_schema=dict(
            model_file="string",
            kinetic_params="map[tuple[float,float]]",
            substrate_update_reactions="map[string]",
            biomass_identifier="string",
            bounds="map[bounds]",
        ),
        input_schema=dict(substrates=dict(_type="map", _value="positive_float")),
        output_schema=dict(substrates=dict(_type="map", _value="positive_float")),
        config_state=dict(
            biomass_identifier="biomass",
            bounds=dict(ATPM=dict(lower=1.0, upper=1.0), EX_o2_e=dict(lower=-2.0, upper=None)),
            kinetic_params=dict(acetate=(0.5, 2.0), glucose=(0.5, 1.0)),
            model_file="textbook",
            substrate_update_reactions=dict(acetate="EX_ac_e", glucose="EX_glc__D_e"),
        ),
        input_state=dict(
            substrates=dict(
                acetate=["fields", "acetate"],
                biomass=["fields", "biomass"],
                glucose=["fields", "glucose"],
            )
        ),
        output_state=dict(
            substrates=dict(
                acetate=["fields", "acetate"],
                biomass=["fields", "biomass"],
                glucose=["fields", "glucose"],
            )
        ),
        interval=1.0,
    )

    pb_model = PBModel(
        stores=[store_fields_acetate, store_fields_biomass, store_fields_glucose],
        steps=[step_emitter],
        processes=[process_dFBA],
        types=[],
    )
    generated_config: dict[str, Any] = assemble_pb(pb_model=pb_model)
    assert step_config_template == generated_config

    core = pg.ProcessTypes()
    core = pg.register_types(core)
    apply_spatio_types_and_processes_to_core(core)

    # construct and run the Step network (don't need to call composite.run(), executes in composite.initialize())
    composite = pg.Composite(config=deepcopy(generated_config), core=core)
    composite.run(interval=60)

    # compare results
    results: dict = composite.state["fields"]
    assert float(results["acetate"]) == 0.0
    assert float(results["biomass"]) == 0.987918808708276
    assert float(results["glucose"]) == 0.0
