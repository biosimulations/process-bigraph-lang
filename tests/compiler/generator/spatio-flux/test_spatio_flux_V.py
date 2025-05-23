import os.path
from copy import deepcopy
from pathlib import Path
from typing import Any

import numpy as np
import process_bigraph as pg  # type: ignore[import-untyped]
from tests.fixtures.test_registry.spatio_flux_library import apply_to_core as apply_spatio_types_and_processes_to_core
from spatio_flux.processes.particles import get_particles_state, get_minimal_particle_composition

PARTICLES_PROCESS_ADDR = "spatio_flux.processes.Particles"
step_config_template = {
    "composition": {
        'particles': {
            '_type': 'map',
            '_value': {
                'minimal_particle': {
                    '_type': 'process',
                    'address': {
                        '_type': 'string',
                        '_default': 'local:MinimalParticle'
                    },
                    'config': {
                        '_type': 'quote',
                        '_default': {
                            'reactions': {
                                'grow': {
                                    'biomass': {
                                        'vmax': 0.01,
                                        'kcat': 0.01,
                                        'role': 'reactant'
                                    },
                                    'detritus': {
                                        'vmax': 0.001,
                                        'kcat': 0.001,
                                        'role': 'product'
                                    }
                                }
                            }
                        }
                    },
                    '_inputs': {
                        'mass': 'float',
                        'substrates':'map[positive_float]'
                    },
                    '_outputs': {
                        'mass': 'float',
                        'substrates':'map[float]'
                    },
                    'inputs': {
                        '_type': 'tree[wires]',
                        '_default': {
                            'mass': ['mass'],
                            'substrates': ['local']
                        }
                    },
                    'outputs': {
                        '_type': 'tree[wires]',
                        '_default': {
                            'mass': ['mass'],
                            'substrates': ['exchange']
                        }
                    }
                }
            }
        }
    },
    "state": {
        'fields': {
            'biomass': np.array([
                [0.9335271 , 0.94210545, 1.45635715, 0.85470302],
                [0.55119037, 0.92462433, 1.61128428, 1.96258914],
                [0.82698072, 1.34714521, 1.87425519, 0.53209707],
                [0.98956844, 1.31688393, 0.90556535, 0.76034733]
            ]),
            'detritus': np.array([
                [0., 0., 0., 0.],
                [0., 0., 0., 0.],
                [0., 0., 0., 0.],
                [0., 0., 0., 0.]
            ])
        },
        'particles': {
            'xBaTNrq4T8mh1phCXNGeow': {
                'position': (np.float64(2.4310020233238836), np.float64(14.43465475731152)),
                'size': 48.17502371097209,
                'local': {
                    'biomass': np.float64(1.4563571535090656),
                    'detritus': np.float64(0.0)
                },
                'mass': 0.9667339634671268,
                'exchange': {
                    'biomass': 0.0,
                    'detritus': 0.0
                },
                'id': 'xBaTNrq4T8mh1phCXNGeow'
            }
        },
        'particles_process': {
            '_type': 'process',
            'address': 'local:Particles',
            'config': {
                'n_bins': (4, 4),
                'bounds': (10.0, 20.0),
                'diffusion_rate': 0.1,
                'advection_rate': (0, -0.1),
                'add_probability': 0.4,
                'boundary_to_add': ['top']
            },
            'inputs': {
                'particles': ['particles'],
                'fields': ['fields']
            },
            'outputs': {
                'particles': ['particles'],
                'fields': ['fields']
            }
        },
        'emitter': {
            '_type': 'step',
            'address': 'local:ram-emitter',
            'config': {
                'emit': {
                    'global_time': 'any',
                    'particles': 'any',
                    'fields': 'any'
                }
            },
            'inputs': {
                'global_time': ['global_time'],
                'particles': ['particles'],
                'fields': ['fields']
            }
        }
    }
}


def test_spatio_flux_five() -> None:
    core = pg.ProcessTypes()
    core = pg.register_types(core)
    apply_spatio_types_and_processes_to_core(core)

    config: dict[str, Any] = deepcopy(step_config_template)

    # construct and run the Step network (don't need to call composite.run(), executes in composite.initialize())
    composite = pg.Composite(config=config, core=core)
    composite.run(interval=60)

    # compare results
    results: dict = composite.state["fields"]
    pass


