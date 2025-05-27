from copy import deepcopy
from typing import Any

import numpy as np
import process_bigraph as pg  # type: ignore[import-untyped]
from tests.fixtures.test_registry.spatio_flux_library import apply_to_core as apply_spatio_types_and_processes_to_core

D_FBA_PROCESS_ADDR = "spatio_flux.processes.DynamicFBA"

rows: int = 2
columns: int = 3

substrate_values: dict[str, list[list[float]]] = {
    substrate: [[10.0 if substrate == "glucose" else (1.0 if substrate == "acetate" else 0.0)] for row in range(rows)]
    for substrate in ["acetate", "biomass", "glucose"]
}
step_config_template = {
    "composition": {
        "fields": {
            "acetate": f"array[({rows}|{columns}),positive_float]",
            "biomass": f"array[({rows}|{columns}),positive_float]",
            "glucose": f"array[({rows}|{columns}),positive_float]",
        },
        "dFBA[0,0]": {
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
        "dFBA[0,1]": {
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
        "dFBA[0,2]": {
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
        "dFBA[1,0]": {
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
        "dFBA[1,1]": {
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
        "dFBA[1,2]": {
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
        "dFBA[0,0]": {
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
                    "acetate": ["fields", "acetate", 0, 0],
                    "biomass": ["fields", "biomass", 0, 0],
                    "glucose": ["fields", "glucose", 0, 0],
                }
            },
            "interval": 1.0,
            "outputs": {
                "substrates": {
                    "acetate": ["fields", "acetate", 0, 0],
                    "biomass": ["fields", "biomass", 0, 0],
                    "glucose": ["fields", "glucose", 0, 0],
                }
            },
            "shared": None,
        },
        "dFBA[0,1]": {
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
                    "acetate": ["fields", "acetate", 0, 1],
                    "biomass": ["fields", "biomass", 0, 1],
                    "glucose": ["fields", "glucose", 0, 1],
                }
            },
            "interval": 1.0,
            "outputs": {
                "substrates": {
                    "acetate": ["fields", "acetate", 0, 1],
                    "biomass": ["fields", "biomass", 0, 1],
                    "glucose": ["fields", "glucose", 0, 1],
                }
            },
            "shared": None,
        },
        "dFBA[0,2]": {
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
                    "acetate": ["fields", "acetate", 0, 2],
                    "biomass": ["fields", "biomass", 0, 2],
                    "glucose": ["fields", "glucose", 0, 2],
                }
            },
            "interval": 1.0,
            "outputs": {
                "substrates": {
                    "acetate": ["fields", "acetate", 0, 2],
                    "biomass": ["fields", "biomass", 0, 2],
                    "glucose": ["fields", "glucose", 0, 2],
                }
            },
            "shared": None,
        },
        "dFBA[1,0]": {
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
                    "acetate": ["fields", "acetate", 1, 0],
                    "biomass": ["fields", "biomass", 1, 0],
                    "glucose": ["fields", "glucose", 1, 0],
                }
            },
            "interval": 1.0,
            "outputs": {
                "substrates": {
                    "acetate": ["fields", "acetate", 1, 0],
                    "biomass": ["fields", "biomass", 1, 0],
                    "glucose": ["fields", "glucose", 1, 0],
                }
            },
            "shared": None,
        },
        "dFBA[1,1]": {
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
                    "acetate": ["fields", "acetate", 1, 1],
                    "biomass": ["fields", "biomass", 1, 1],
                    "glucose": ["fields", "glucose", 1, 1],
                }
            },
            "interval": 1.0,
            "outputs": {
                "substrates": {
                    "acetate": ["fields", "acetate", 1, 1],
                    "biomass": ["fields", "biomass", 1, 1],
                    "glucose": ["fields", "glucose", 1, 1],
                }
            },
            "shared": None,
        },
        "dFBA[1,2]": {
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
                    "acetate": ["fields", "acetate", 1, 2],
                    "biomass": ["fields", "biomass", 1, 2],
                    "glucose": ["fields", "glucose", 1, 2],
                }
            },
            "interval": 1.0,
            "outputs": {
                "substrates": {
                    "acetate": ["fields", "acetate", 1, 2],
                    "biomass": ["fields", "biomass", 1, 2],
                    "glucose": ["fields", "glucose", 1, 2],
                }
            },
            "shared": None,
        },
        "emitter": {
            "_type": "step",
            # "address": "local:ram-emitter",
            "config": {"emit": {"fields": "any", "global_time": "any"}},
            "inputs": {"fields": ["fields"], "global_time": ["global_time"]},
            "outputs": None,
        },
        "fields": {
            "acetate": np.array(
                [np.array([0.3, 0.3, 0.3], dtype=np.float64), np.array([0.3, 0.3, 0.3], dtype=np.float64)],
                dtype=np.float64,
            ),
            "biomass": np.array(
                [np.array([0.1, 0.1, 0.1], dtype=np.float64), np.array([0.1, 0.1, 0.1], dtype=np.float64)],
                dtype=np.float64,
            ),
            "glucose": np.array(
                [np.array([10.0, 10.0, 10.0], dtype=np.float64), np.array([10.0, 10.0, 10.0], dtype=np.float64)],
                dtype=np.float64,
            ),
        },
    },
}


def test_spatio_flux_two() -> None:
    core = pg.ProcessTypes()
    core = pg.register_types(core)
    apply_spatio_types_and_processes_to_core(core)

    config: dict[str, Any] = deepcopy(step_config_template)

    composite = pg.Composite(config=config, core=core)
    composite.run(interval=60)

    # compare results
    results: dict = composite.state["fields"]
    for row in range(rows):
        for col in range(columns):
            assert float(results["acetate"][row][col]) == 0.0
            assert float(results["biomass"][row][col]) == 0.9683019927155062
            assert float(results["glucose"][row][col]) == 0.0
