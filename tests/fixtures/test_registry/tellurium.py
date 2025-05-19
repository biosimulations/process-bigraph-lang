from typing import Any

from roadrunner._roadrunner import NamedArray  # type: ignore[import-untyped]

import numpy as np
import tellurium as te  # type: ignore[import-untyped]
from tests.fixtures.test_registry.utils import TypedStep
from typing_extensions import override


class TelluriumStep(TypedStep):
    config_schema = {
        "sbml_model_path": "string",
        "antimony_string": "string",
        "num_steps": "integer",
    }
    num_steps: int = 10
    output_shape: tuple[int, int]

    def __init__(self, config: dict[str, Any] | None = None, core: dict[str, Any] | None = None) -> None:
        super().__init__(config, core)

        # initialize a tellurium(roadrunner) simulation object. Load the model in using either sbml(default) or antimony
        if self.config.get("antimony_string") and not self.config.get("sbml_model_path"):
            self.simulator = te.loada(self.config["antimony_string"])
        elif self.config.get("sbml_model_path") and not self.config.get("antimony_string"):
            self.simulator = te.loadSBMLModel(sbml=self.config["sbml_model_path"])
        else:
            raise Exception('the config requires either an "antimony_string" or an "sbml_model_path"')

        # Get the species (floating and boundary)
        self.floating_species_list = self.simulator.getFloatingSpeciesIds()
        self.boundary_species_list = self.simulator.getBoundarySpeciesIds()
        self.floating_species_initial = self.simulator.getFloatingSpeciesConcentrations()
        self.boundary_species_initial = self.simulator.getBoundarySpeciesConcentrations()

        # Get the list of parameters and their values
        self.model_parameters_list = self.simulator.getGlobalParameterIds()
        self.model_parameter_values = self.simulator.getGlobalParameterValues()

        # Get a list of reactions
        self.reaction_list = self.simulator.getReactionIds()
        self.output_shape = (
            self.num_steps,
            len(self.floating_species_list) + 1,
        )

    @override
    def inputs(self) -> dict[str, Any]:
        return {
            "time": "float",
            "run_time": "float",
        }

    @override
    def outputs(self) -> dict[str, Any]:
        return {
            "results": {
                "result_array": f"array[({self.output_shape[0]}|{self.output_shape[1]}),float]",
                "result_labels": "list[string]",
            }
        }

    @override
    def update(self, inputs: dict[str, Any]) -> dict[str, Any]:
        time = inputs["time"]
        run_time = inputs["run_time"]
        num_steps = self.config["num_steps"]
        results: NamedArray = self.simulator.simulate(time, run_time, num_steps)
        nparray: np.ndarray = np.array(results)
        return {"results": {"result_array": nparray, "result_labels": ["time"] + self.floating_species_list}}
