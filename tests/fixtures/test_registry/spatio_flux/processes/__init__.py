from typing import Any

from tests.fixtures.test_registry.spatio_flux.processes.dfba import DynamicFBA
from tests.fixtures.test_registry.spatio_flux.processes.diffusion_advection import DiffusionAdvection
from tests.fixtures.test_registry.spatio_flux.processes.particles import Particles, MinimalParticle


PROCESS_DICT = {
    "DynamicFBA": DynamicFBA,
    "DiffusionAdvection": DiffusionAdvection,
    "Particles": Particles,
    "MinimalParticle": MinimalParticle,
}


def register_processes(core: Any) -> Any:
    core.register_links(PROCESS_DICT)
    return core
