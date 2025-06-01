from copy import deepcopy
from typing import Any

import numpy as np
import process_bigraph as pg  # type: ignore[import-untyped]

from process_bigraph_lang.compiler.converter import assemble_pb
from process_bigraph_lang.compiler.pb_model import (
    PBStoreSchema,
    PBStoreState,
    PBModel,
    PBProcessSchema,
    PBProcessState,
    PBStepSchema,
    PBStepState,
)
from tests.fixtures.test_registry.spatio_flux import register_types as apply_spatio_types_and_processes_to_core

D_FBA_PROCESS_ADDR = "tests.fixtures.test_registry.spatio_flux.processes.DynamicFBA"

rows: int = 2
columns: int = 3
n_bins = (4, 4)
bounds = (10.0, 20.0)
diffusion_rate = 0.1
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
        },
        "emitter": {
            "_type": "step",
            "config": {"emit": {"fields": "any", "global_time": "any"}},
            "inputs": {"fields": ["fields"], "global_time": ["global_time"]},
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


def test_spatio_flux_two_from_document() -> None:
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
            assert np.allclose(float(results["biomass"][row][col]), 0.9683019927155062)
            assert float(results["glucose"][row][col]) == 0.0


def test_spatio_flux_two_from_generator() -> None:
    store_schema_fields_acetate = PBStoreSchema(
        key="acetate",
        path=["fields"],
        default_value=None,
        data_type=f"array[({rows}|{columns}),positive_float]",
    )
    store_state_fields_acetate = PBStoreState(
        key="acetate",
        path=["fields"],
        value=np.array(
            [np.array([0.3, 0.3, 0.3], dtype=np.float64), np.array([0.3, 0.3, 0.3], dtype=np.float64)], dtype=np.float64
        ),
        store_schema=store_schema_fields_acetate,
    )
    store_schema_fields_biomass = PBStoreSchema(
        key="biomass",
        path=["fields"],
        default_value=None,
        data_type=f"array[({rows}|{columns}),positive_float]",
    )
    store_state_fields_biomass = PBStoreState(
        key="biomass",
        path=["fields"],
        value=np.array(
            [np.array([0.1, 0.1, 0.1], dtype=np.float64), np.array([0.1, 0.1, 0.1], dtype=np.float64)], dtype=np.float64
        ),
        store_schema=store_schema_fields_biomass,
    )
    store_schema_fields_glucose = PBStoreSchema(
        key="glucose",
        path=["fields"],
        default_value=None,
        data_type=f"array[({rows}|{columns}),positive_float]",
    )
    store_state_fields_glucose = PBStoreState(
        key="glucose",
        path=["fields"],
        value=np.array(
            [np.array([10.0, 10.0, 10.0], dtype=np.float64), np.array([10.0, 10.0, 10.0], dtype=np.float64)],
            dtype=np.float64,
        ),
        store_schema=store_schema_fields_glucose,
    )
    step_emitter_schema = PBStepSchema(
        key="emitter",
        path=[],
        address="local:ram-emitter",
        config_schema=dict(emit=dict(_type="map", _value="any")),
        input_schema=dict(_type="map", _value="any"),
        output_schema={},
        default_config_state={},
        default_input_state={},
        default_output_state={},
        collection_info=None,
    )
    step_emitter_state = PBStepState(
        key="emitter",
        path=[],
        address="local:ram-emitter",
        config_state=dict(emit=dict(fields="any", global_time="any")),
        input_state=dict(fields=["fields"], global_time=["global_time"]),
        output_state={},
        step_schema=step_emitter_schema,
    )
    process_schema_dFBA_list = []
    process_state_dFBA_list = []
    for i in range(rows):
        for j in range(columns):
            process_schema_dFBA_list.append(
                PBProcessSchema(
                    key=f"dFBA[{i},{j}]",
                    path=[],
                    address="tests.fixtures.test_registry.spatio_flux.processes.DynamicFBA",
                    config_schema=dict(
                        model_file="string",
                        kinetic_params="map[tuple[float,float]]",
                        substrate_update_reactions="map[string]",
                        biomass_identifier="string",
                        bounds="map[bounds]",
                    ),
                    input_schema=dict(substrates=dict(_type="map", _value="positive_float")),
                    output_schema=dict(substrates=dict(_type="map", _value="positive_float")),
                    default_config_state={},
                    default_input_state={},
                    default_output_state={},
                    default_interval=1.0,
                    collection_info=None,
                )
            )
            process_state_dFBA_list.append(
                PBProcessState(
                    key=f"dFBA[{i},{j}]",
                    path=[],
                    address="tests.fixtures.test_registry.spatio_flux.processes.DynamicFBA",
                    config_state=dict(
                        biomass_identifier="biomass",
                        bounds=dict(ATPM=dict(lower=1.0, upper=1.0), EX_o2_e=dict(lower=-2.0, upper=None)),
                        kinetic_params=dict(acetate=(0.5, 2.0), glucose=(0.5, 1.0)),
                        model_file="textbook",
                        substrate_update_reactions=dict(acetate="EX_ac_e", glucose="EX_glc__D_e"),
                    ),
                    input_state=dict(
                        substrates=dict(
                            acetate=["fields", "acetate", i, j],
                            biomass=["fields", "biomass", i, j],
                            glucose=["fields", "glucose", i, j],
                        )
                    ),
                    output_state=dict(
                        substrates=dict(
                            acetate=["fields", "acetate", i, j],
                            biomass=["fields", "biomass", i, j],
                            glucose=["fields", "glucose", i, j],
                        )
                    ),
                    interval=1.0,
                    process_schema=process_schema_dFBA_list[-1],
                )
            )

    pb_model = PBModel(
        store_schemas=[store_schema_fields_acetate, store_schema_fields_biomass, store_schema_fields_glucose],
        store_states=[store_state_fields_acetate, store_state_fields_biomass, store_state_fields_glucose],
        step_schemas=[step_emitter_schema],
        step_states=[step_emitter_state],
        process_schemas=process_schema_dFBA_list,
        process_states=process_state_dFBA_list,
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
    apply_spatio_types_and_processes_to_core(core)

    composite = pg.Composite(config=deepcopy(generated_config), core=core)
    composite.run(interval=60)

    # compare results
    results: dict = composite.state["fields"]
    for row in range(rows):
        for col in range(columns):
            assert float(results["acetate"][row][col]) == 0.0
            assert np.allclose(float(results["biomass"][row][col]), 0.9683019927155062)
            assert float(results["glucose"][row][col]) == 0.0
