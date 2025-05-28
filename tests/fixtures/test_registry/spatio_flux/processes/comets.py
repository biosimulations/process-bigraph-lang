"""
COMETS composite made of dFBAs and diffusion-advection processes.
"""

from typing import Any

from process_bigraph import Composite, ProcessTypes  # type: ignore[import-untyped]

# TODO -- need to do this to register???

default_config = {
    "total_time": 60.0,
    # environment size
    "bounds": (10.0, 10.0),
    "n_bins": (10, 10),
    # set fields
    "mol_ids": ["glucose", "acetate", "biomass"],
    "initial_min_max": {"glucose": (0, 10), "acetate": (0, 0), "biomass": (0, 0.1)},
}


## TODO -- maybe we need to make specific composites
class COMETS(Composite):
    """
    This needs to declare what types of processes are in the composite.
    """

    config_schema = {
        "n_bins": "tuple",
    }

    def __init__(self, config: dict[str, Any], core: ProcessTypes | None = None) -> None:
        # set up the document here
        _state = {
            "dFBA": {
                "config": {
                    "n_bins": config["n_bins"],
                }
            },
            "diffusion": {
                "config": {
                    "something_else": config["n_bins"],
                }
            },
        }

        super().__init__(config, core=core)

    # TODO -- this could be in Process.
    def get_default(self) -> Any:
        return self.core.default(self.config_schema)


# if __name__ == "__main__":
#     run_comets(**default_config)
