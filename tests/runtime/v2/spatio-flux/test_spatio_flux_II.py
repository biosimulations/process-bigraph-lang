from copy import deepcopy
from pathlib import Path
from typing import Any

import numpy as np
import process_bigraph as pg  # type: ignore[import-untyped]
from tests.fixtures.test_registry.spatio_flux_library import apply_to_core as apply_spatio_types_and_processes_to_core

D_FBA_PROCESS_ADDR = "spatio_flux.processes.DynamicFBA"

rows: int = 2
columns: int = 3

substrate_values: dict[str, list[list[float]]] = { substrate:
                                                       [
                                                           [ 10.0 if substrate == "glucose" else (1.0 if substrate == "acetate" else 0.0)  ]
                                                           for row in range(rows)]
                                                        for substrate in ["acetate", "biomass", "glucose"] }
step_config_template = {
    "composition": {
        "fields": {
            "acetate": f"array[({rows}|{columns}),positive_float],",
            "biomass": f"array[({rows}|{columns}),positive_float]",
            "glucose": f"array[({rows}|{columns}),positive_float]"},
    },
    "state": {
        "dFBA[0,0]": {
            "_type": "process",
            "address": f"local:!{D_FBA_PROCESS_ADDR}",
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
            "address": f"local:!{D_FBA_PROCESS_ADDR}",
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
            "address": f"local:!{D_FBA_PROCESS_ADDR}",
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
            "address": f"local:!{D_FBA_PROCESS_ADDR}",
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
            "address": f"local:!{D_FBA_PROCESS_ADDR}",
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
            "address": f"local:!{D_FBA_PROCESS_ADDR}",
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
            "_type": "process",
            "address": "local:ram-emitter",
            "config": {"emit": {"fields": "any", "global_time": "any"}},
            "inputs": {"fields": ["fields"], "global_time": ["global_time"]},
            "outputs": None,
        },
        "fields": {"acetate": np.array([[0.3, 0.3, 0.3],[0.3, 0.3, 0.3]], dtype=np.float64),
                   "biomass": np.array([[0.0, 0.0, 0.0],[0.0, 0.0, 0.0]], dtype=np.float64),
                   "glucose": np.array([[10.0, 10.0, 10.0],[10.0, 10.0, 10.0]], dtype=np.float64)},
    },
}


def test_spatio_flux_two(sbml_path_caravagna2010: Path) -> None:
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
