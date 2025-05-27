from copy import deepcopy
from typing import Any


import process_bigraph as pg  # type: ignore[import-untyped]
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
            "shared": None,
        },
        "emitter": {
            "_type": "step",
            "config": {"emit": {"fields": "any", "global_time": "any"}},
            "inputs": {"fields": ["fields"], "global_time": ["global_time"]},
            "outputs": None,
        },
        "fields": {"acetate": 0.807561836566412, "biomass": 0.1, "glucose": 10},
    },
}


def test_spatio_flux_one() -> None:
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
