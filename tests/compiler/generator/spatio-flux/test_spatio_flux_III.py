from copy import deepcopy
from pathlib import Path
from typing import Any

import numpy as np
import process_bigraph as pg  # type: ignore[import-untyped]
from tests.fixtures.test_registry.spatio_flux_library import apply_to_core as apply_spatio_types_and_processes_to_core


bounds = (10.0, 10.0)
bounds_as_str = ("10.0", "10.0")
n_bins = (10, 10)
n_bins_as_str = ("10", "10")
mol_ids = [
    'glucose',
    'acetate',
    'biomass'
]
diffusion_rate = 1e-1
diffusion_dt = 1e-1
advection_coeffs = {'biomass': (0, -0.1)}

DIFF_ADVEC_PROCESS_ADDR = "spatio_flux.processes.DiffusionAdvection"
step_config_template = {
    "composition": {
        "fields": f"map[array[{n_bins},positive_float]]",
    },
    "state": {
        "diffusion_advection": {
            "_type": "process",
            "address": f"local:!{DIFF_ADVEC_PROCESS_ADDR}",
            "config": {
                'n_bins': n_bins_as_str,
                'bounds': bounds,
                'default_diffusion_rate': diffusion_rate,
                'default_diffusion_dt': diffusion_dt,
                'advection_coeffs': advection_coeffs,
            },
            "inputs": {
                "fields": ["fields"]
            },
            "interval": 1.0,
            "outputs": {
                "fields": ["fields"]
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
        "fields": {"acetate": np.array([np.array([float(index_ace_1 + index_ace_0)/20 for index_ace_1 in range(n_bins[1])], dtype=np.float64) for index_ace_0 in range(n_bins[0])], dtype=np.float64),
                   "biomass": np.array([np.array([float(index_bio_1 + index_bio_0)/20 for index_bio_1 in range(n_bins[1])], dtype=np.float64) for index_bio_0 in range(n_bins[0])], dtype=np.float64),
                   "glucose": np.array([np.array([float(index_glu_1 + index_glu_0)/20 for index_glu_1 in range(n_bins[1])], dtype=np.float64) for index_glu_0 in range(n_bins[0])], dtype=np.float64),
                   }
    }
}


def test_spatio_flux_three(sbml_path_caravagna2010: Path) -> None:
    core = pg.ProcessTypes()
    core = pg.register_types(core)
    apply_spatio_types_and_processes_to_core(core)

    config: dict[str, Any] = deepcopy(step_config_template)

    # construct and run the Step network (don't need to call composite.run(), executes in composite.initialize())
    composite = pg.Composite(config=config, core=core)
    composite.run(interval=120)

    # compare results
    results: dict = composite.state["fields"]
    for row in range(n_bins[0]):
        for col in range(n_bins[1]):
            # assert we're not still at initial conditions (unless it's the average, because diffusion)
            assert float(results["acetate"][row][col]) != (row + col)/20 or float(results["acetate"][row][col]) == 0.45
            assert float(results["biomass"][row][col]) != (row + col)/20 or float(results["biomass"][row][col]) == 0.45
            assert float(results["glucose"][row][col]) != (row + col)/20 or float(results["glucose"][row][col]) == 0.45
