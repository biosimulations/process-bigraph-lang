from copy import deepcopy
from typing import Any, cast

import numpy as np
import process_bigraph as pg  # type: ignore[import-untyped]

from process_bigraph_lang.compiler.converter import assemble_pb
from process_bigraph_lang.compiler.pb_model import PBStore, PBModel, PBProcess, PBStep
from tests.fixtures.test_registry.spatio_flux import register_types as apply_spatio_types_and_processes_to_core

n_bins = (4, 4)
bounds = (10.0, 20.0)
diffusion_rate = 0.1
PARTICLES_PROCESS_ADDR = "tests.fixtures.test_registry.spatio_flux.processes.Particles"
MINIMAL_PARTICLE_PROCESS_ADDR = "tests.fixtures.test_registry.spatio_flux.processes.MinimalParticle"
step_config_template = {
    "composition": {
        "particles": {
            "_type": "map",
            "_value": {
                "minimal_particle": {
                    "_type": "process",
                    "address": {"_type": "quote", "_default": f"local:!{MINIMAL_PARTICLE_PROCESS_ADDR}"},
                    "_config": {
                        "_type": {"_type": "map", "_value": "reaction"},
                    },
                    "config": {
                        "_type": "quote",
                        "_default": {
                            "reactions": {
                                "grow": {
                                    "biomass": {"vmax": 0.01, "kcat": 0.01, "role": "reactant"},
                                    "detritus": {"vmax": 0.001, "kcat": 0.001, "role": "product"},
                                }
                            }
                        },
                    },
                    "_inputs": {"mass": "float", "substrates": {"_type": "map", "_value": "positive_float"}},
                    "_outputs": {"mass": "float", "substrates": {"_type": "map", "_value": "float"}},
                    "inputs": {"_type": "tree[wires]", "_default": {"mass": ["mass"], "substrates": ["local"]}},
                    "outputs": {"_type": "tree[wires]", "_default": {"mass": ["mass"], "substrates": ["exchange"]}},
                }
            },
        },
        "particles_process": {
            "_type": "process",
            "address": {
                "_type": "quote",
                "_default": f"local:!{PARTICLES_PROCESS_ADDR}",
            },
            "_config": {
                "bounds": "tuple[float,float]",
                "n_bins": "tuple[integer,integer]",
                "diffusion_rate": {"_type": "float", "_default": 1e-1},
                "advection_rate": {"_type": "tuple[float,float]", "_default": (0, 0)},
                "add_probability": "float",
                "boundary_to_add": {"_type": "list[boundary_side]", "_default": ["left", "right"]},
                "boundary_to_remove": {"_type": "list[boundary_side]", "_default": ["left", "right", "top", "bottom"]},
            },
            "_inputs": {
                "particles": "map[particle]",
                "fields": {
                    "_type": "map",
                    "_value": {
                        "_type": "array",
                        "_shape": n_bins,
                        "_data": "positive_float",
                    },
                },
            },
            "_outputs": {
                "particles": "map[particle]",
                "fields": {
                    "_type": "map",
                    "_value": {
                        "_type": "array",
                        "_shape": n_bins,
                        "_data": "positive_float",
                    },
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
        "fields": {
            "biomass": np.array([
                [0.9335271, 0.94210545, 1.45635715, 0.85470302],
                [0.55119037, 0.92462433, 1.61128428, 1.96258914],
                [0.82698072, 1.34714521, 1.87425519, 0.53209707],
                [0.98956844, 1.31688393, 0.90556535, 0.76034733],
            ]),
            "detritus": np.array([
                [0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0],
            ]),
        },
        "particles": {
            "xBaTNrq4T8mh1phCXNGeow": {
                "position": (np.float64(2.4310020233238836), np.float64(14.43465475731152)),
                "size": 48.17502371097209,
                "local": {"biomass": np.float64(1.4563571535090656), "detritus": np.float64(0.0)},
                "mass": 0.9667339634671268,
                "exchange": {"biomass": 0.0, "detritus": 0.0},
                "id": "xBaTNrq4T8mh1phCXNGeow",
            }
        },
        "particles_process": {
            "_type": "process",
            # "address": f"local:!{PARTICLES_PROCESS_ADDR}",
            "config": {
                "n_bins": n_bins,
                "bounds": bounds,
                "diffusion_rate": diffusion_rate,
                "advection_rate": (0, -0.1),
                "add_probability": 0.4,
                "boundary_to_add": ["top"],
            },
            "inputs": {"particles": ["particles"], "fields": ["fields"]},
            "outputs": {"particles": ["particles"], "fields": ["fields"]},
        },
        "emitter": {
            "_type": "step",
            # "address": "local:ram-emitter",
            "config": {"emit": {"global_time": "any", "particles": "any", "fields": "any"}},
            "inputs": {"global_time": ["global_time"], "particles": ["particles"], "fields": ["fields"]},
        },
    },
}


def test_five_from_document() -> None:
    core = pg.ProcessTypes()
    core = pg.register_types(core)
    apply_spatio_types_and_processes_to_core(core)

    config: dict[str, Any] = deepcopy(step_config_template)

    # construct and run the Step network (don't need to call composite.run(), executes in composite.initialize())
    composite = pg.Composite(config=config, core=core)
    composite.run(interval=60)

    # compare results
    _results: dict = composite.state["fields"]
    pass


def test_five_from_generator() -> None:
    biomass_array = np.array([
        [0.9335271, 0.94210545, 1.45635715, 0.85470302],
        [0.55119037, 0.92462433, 1.61128428, 1.96258914],
        [0.82698072, 1.34714521, 1.87425519, 0.53209707],
        [0.98956844, 1.31688393, 0.90556535, 0.76034733],
    ])
    detrius_array = np.array([
        [0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0],
    ])
    field_array_type = dict(_type="array", _shape=n_bins, _data="positive_float")
    store_biomass = PBStore(key="biomass", path=["fields"], value=biomass_array, data_type=field_array_type)
    store_detritus = PBStore(key="detritus", path=["fields"], value=detrius_array, data_type=field_array_type)
    store_position = PBStore(
        key="position",
        path=["particles", "xBaTNrq4T8mh1phCXNGeow"],
        value=(np.float64(2.4310020233238836), np.float64(14.43465475731152)),
        data_type=dict(_type="tuple", _data="float"),
    )
    store_size = PBStore(
        key="size", path=["particles", "xBaTNrq4T8mh1phCXNGeow"], value=48.17502371097209, data_type="float"
    )
    store_local_biomass = PBStore(
        key="biomass",
        path=["particles", "xBaTNrq4T8mh1phCXNGeow", "local"],
        value=np.float64(1.4563571535090656),
        data_type="float",
    )
    store_local_detritus = PBStore(
        key="detritus", path=["particles", "xBaTNrq4T8mh1phCXNGeow", "local"], value=np.float64(0.0), data_type="float"
    )
    store_particle_id = PBStore(
        key="id", path=["particles", "xBaTNrq4T8mh1phCXNGeow"], value="xBaTNrq4T8mh1phCXNGeow", data_type="string"
    )
    store_mass = PBStore(
        key="mass", path=["particles", "xBaTNrq4T8mh1phCXNGeow"], value=0.9667339634671268, data_type="float"
    )
    store_exchange_biomass = PBStore(
        key="biomass",
        path=["particles", "xBaTNrq4T8mh1phCXNGeow", "exchange"],
        value=0.0,
        data_type="float",
    )
    store_exchange_detritus = PBStore(
        key="detritus",
        path=["particles", "xBaTNrq4T8mh1phCXNGeow", "exchange"],
        value=0.0,
        data_type="float",
    )
    process_particles = PBProcess(
        key="particles_process",
        path=[],
        address=f"local:!{PARTICLES_PROCESS_ADDR}",
        config_schema=dict(
            bounds="tuple[float,float]",
            n_bins="tuple[integer,integer]",
            diffusion_rate=dict(_type="float", _default=1e-1),
            advection_rate=dict(_type="tuple[float,float]", _default=(0, 0)),
            add_probability="float",
            boundary_to_add=dict(_type="list[boundary_side]", _default=["left", "right"]),
            boundary_to_remove=dict(_type="list[boundary_side]", _default=["left", "right", "top", "bottom"]),
        ),
        input_schema=dict(
            particles="map[particle]",
            fields=dict(_type="map", _value=dict(_type="array", _shape=n_bins, _data="positive_float")),
        ),
        output_schema=dict(
            particles="map[particle]",
            fields=dict(_type="map", _value=dict(_type="array", _shape=n_bins, _data="positive_float")),
        ),
        config_state=dict(
            n_bins=n_bins,
            bounds=bounds,
            diffusion_rate=diffusion_rate,
            advection_rate=(0, -0.1),
            add_probability=0.4,
            boundary_to_add=["top"],
        ),
        input_state=dict(particles=["particles"], fields=["fields"]),
        output_state=dict(particles=["particles"], fields=["fields"]),
    )
    process_minimal_particle = PBProcess(
        key="minimal_particle",
        path=["particles", "xBaTNrq4T8mh1phCXNGeow"],
        address=f"local:!{MINIMAL_PARTICLE_PROCESS_ADDR}",
        config_schema=dict(_type="map", _value="reaction"),
        input_schema=dict(mass="float", substrates=dict(_type="map", _value="positive_float")),
        output_schema=dict(mass="float", substrates=dict(_type="map", _value="float")),
        config_state=dict(
            _type="quote",
            _default=dict(
                reaction=dict(
                    grow=dict(
                        biomass=dict(vmax=0.01, kcat=0.01, role="reactant"),
                        detritus=dict(vmax=0.001, kcat=0.001, role="product"),
                    )
                )
            ),
        ),
        input_state=dict(_type="tree[wires]", _default=dict(mass=["mass"], substrates=["local"])),
        output_state=dict(_type="tree[wires]", _default=dict(mass=["mass"], substrates=["exchange"])),
    )
    step_emitter = PBStep(
        key="emitter",
        path=[],
        address="local:ram-emitter",
        config_schema=dict(emit=dict(_type="map", _value="any")),
        input_schema=dict(_type="map", _value="any"),
        output_schema={},
        config_state=dict(emit=dict(global_time="any", particles="any", fields="any")),
        input_state=dict(global_time=["global_time"], particles=["particles"], fields=["fields"]),
        output_state={},
    )
    pb_model = PBModel(
        processes=[process_particles, process_minimal_particle],
        steps=[step_emitter],
        stores=[
            store_biomass,
            store_detritus,
            store_position,
            store_size,
            store_local_biomass,
            store_local_detritus,
            store_particle_id,
            store_mass,
            store_exchange_biomass,
            store_exchange_detritus,
        ],
        types=[],
    )
    generated_config: dict[str, Any] = assemble_pb(pb_model=pb_model)
    a: dict[str, dict[str, Any]] = cast(dict[str, dict[str, Any]], deepcopy(step_config_template))
    b: dict[str, dict[str, Any]] = cast(dict[str, dict[str, Any]], deepcopy(generated_config))
    a["state"]["fields"] = {}
    b["state"]["fields"] = {}
    # assert a == b

    core = pg.ProcessTypes()
    core = pg.register_types(core)
    apply_spatio_types_and_processes_to_core(core)

    composite = pg.Composite(config=deepcopy(step_config_template), core=core)
    composite.run(interval=60)

    # compare results
    _results: dict = composite.state["fields"]
    pass
