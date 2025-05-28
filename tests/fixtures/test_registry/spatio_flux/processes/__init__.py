from process_bigraph import ProcessTypes  # type: ignore[import-untyped]

from tests.fixtures.test_registry.spatio_flux.processes.dfba import DynamicFBA
from tests.fixtures.test_registry.spatio_flux.processes.diffusion_advection import DiffusionAdvection
from tests.fixtures.test_registry.spatio_flux.processes.particles import Particles, MinimalParticle


PROCESS_DICT = {
    "DynamicFBA": DynamicFBA,
    "DiffusionAdvection": DiffusionAdvection,
    "Particles": Particles,
    "MinimalParticle": MinimalParticle,
}


def register_processes(core: ProcessTypes) -> ProcessTypes:
    for process_name, process in PROCESS_DICT.items():
        core.register_process(process_name, process)
    return core
