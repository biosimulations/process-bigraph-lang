"""
Particle-COMETS composite made of diffusion-advection and particle processes, with a dFBA within each particle.
"""

from typing import Any, cast

import numpy as np
from process_bigraph import ProcessTypes  # type: ignore[import-untyped]

# TODO -- need to do this to register???
from tests.fixtures.test_registry.spatio_flux.processes.diffusion_advection import get_diffusion_advection_spec
from tests.fixtures.test_registry.spatio_flux.processes.particles import Particles, get_particles_spec
from tests.fixtures.test_registry.spatio_flux.processes.particle_comets import default_config


# default_config = {
#     'total_time': 10.0,
#     # environment size
#     'bounds': (10.0, 20.0),
#     'n_bins': (8, 16),
#     # set fields
#     'mol_ids': ['biomass', 'detritus'],
#     'field_diffusion_rate': 1e-1,
#     'field_advection_rate': (0, 0),
#     'initial_min_max': {'biomass': (0, 0.1), 'detritus': (0, 0)},
#     # set particles
#     'n_particles': 10,
#     'particle_diffusion_rate': 1e-1,
#     'particle_advection_rate': (0, -0.1),
#     'particle_add_probability': 0.3,
#     'particle_boundary_to_add': ['top'],
#     'field_interactions': {
#         'biomass': {'vmax': 0.1, 'Km': 1.0, 'interaction_type': 'uptake'},
#         'detritus': {'vmax': -0.1, 'Km': 1.0, 'interaction_type': 'secretion'},
#     },
# }


def get_particles_dfba_state(
    core: ProcessTypes,
    n_bins: tuple[int, int] = (10, 10),
    bounds: tuple[float, float] = (10.0, 10.0),
    mol_ids: list[str] | None = None,
    n_particles: int = 10,
    field_diffusion_rate: float = 1e-1,
    field_advection_rate: tuple[float, float] = (0, 0),
    particle_diffusion_rate: float = 1e-1,
    particle_advection_rate: tuple[float, float] = (0, 0),
    particle_add_probability: float = 0.3,
    particle_boundary_to_add: list[str] | None = None,
    field_interactions: dict[str, dict[str, float | str]] | None = None,
    initial_min_max: dict[str, tuple[float, float]] | None = None,
) -> dict[str, Any]:
    particle_boundary_to_add = particle_boundary_to_add or cast(list[str], default_config["particle_boundary_to_add"])
    mol_ids = mol_ids or cast(list[str], default_config["mol_ids"])
    field_interactions = field_interactions or cast(
        dict[str, dict[str, float | str]], default_config["field_interactions"]
    )
    initial_min_max = initial_min_max or cast(dict[str, tuple[float, float]], default_config["initial_min_max"])
    for mol_id in field_interactions.keys():
        if mol_id not in mol_ids:
            mol_ids.append(mol_id)
        if mol_id not in initial_min_max:
            initial_min_max[mol_id] = (0, 1)

    # TODO -- add fields?
    composite_state = {}

    # add diffusion/advection process
    composite_state["diffusion"] = get_diffusion_advection_spec(
        bounds=bounds,
        n_bins=n_bins,
        mol_ids=mol_ids,
        default_diffusion_rate=field_diffusion_rate,
        default_advection_rate=field_advection_rate,
        diffusion_coeffs=None,  # TODO -- add diffusion coeffs config
        advection_coeffs=None,
    )
    # initialize fields
    fields = {}
    for field, minmax in initial_min_max.items():
        fields[field] = np.random.uniform(low=minmax[0], high=minmax[1], size=n_bins)

    # add particles process
    particles = Particles.generate_state(
        config={
            "n_particles": n_particles,
            "bounds": bounds,
            "fields": fields,
            "n_bins": n_bins,
        }
    )

    composite_state["fields"] = fields
    composite_state["particles"] = particles["particles"]
    composite_state["particles_process"] = get_particles_spec(
        n_bins=n_bins,
        bounds=bounds,
        diffusion_rate=particle_diffusion_rate,
        advection_rate=particle_advection_rate,
        add_probability=particle_add_probability,
        boundary_to_add=particle_boundary_to_add,
    )

    return composite_state
