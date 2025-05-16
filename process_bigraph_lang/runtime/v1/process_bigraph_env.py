import json
from pathlib import Path
from typing import Any

from bigraph_schema import is_schema_key, set_path  # type: ignore[import-untyped]
from bigraph_schema.utilities import remove_path  # type: ignore[import-untyped]
from process_bigraph import Composite, ProcessTypes  # type: ignore[import-untyped]


class ProcessBigraphEnv:
    core: ProcessTypes
    composite: Composite
    emitter_config: dict[str, Any]
    emitter_paths: dict[str | tuple[str, ...], tuple[str, ...]]

    def __init__(self) -> None:
        self.core = ProcessTypes()
        self.composite = Composite(core=self.core)
        self.emitter_config = {}
        self.emitter_paths = {}

    def add_process(
        self,
        name: str,
        process_id: str,
        config: dict[str, Any] | None = None,
        inputs: dict[str, Any] | None = None,
        outputs: dict[str, Any] | None = None,
        path: tuple[str, ...] | None = None,
    ) -> None:
        edge_type = "process"  # TODO -- does it matter if this is a step or a process?
        config = config or {}
        inputs = inputs or {}
        outputs = outputs or {}
        path = path or ()

        # convert string paths to lists
        # TODO -- make this into a separate path-parsing function
        for ports in [inputs, outputs]:
            for port, port_path in ports.items():
                ports[port] = parse_path(port_path)

        # make the process spec
        state = {
            name: {
                "_type": edge_type,
                "address": f"local:{process_id}",  # TODO -- only support local right now?
                "config": config,
                "inputs": inputs,
                "outputs": outputs,
            }
        }

        # nest the process in the composite at the given path
        self.composite.merge({}, state, path)
        self.reset_emitters()
        self.reset_paths()

    def add_step(
        self,
        name: str,
        process_id: str,
        config: dict[str, Any] | None = None,
        inputs: dict[str, Any] | None = None,
        outputs: dict[str, Any] | None = None,
        path: tuple[str, ...] | None = None,
    ) -> None:
        edge_type = "step"  # TODO -- does it matter if this is a step or a process?
        config = config or {}
        inputs = inputs or {}
        outputs = outputs or {}
        path = path or ()

        # convert string paths to lists
        # TODO -- make this into a separate path-parsing function
        for ports in [inputs, outputs]:
            for port, port_path in ports.items():
                ports[port] = parse_path(port_path)

        # make the process spec
        state = {
            name: {
                "_type": edge_type,
                "address": f"local:{process_id}",  # TODO -- only support local right now?
                "config": config,
                "inputs": inputs,
                "outputs": outputs,
            }
        }

        # nest the process in the composite at the given path
        self.composite.merge({}, state, path)
        self.reset_emitters()
        self.reset_paths()

    def reset_emitters(self) -> None:
        for path, emitter in self.emitter_paths.items():
            remove_path(self.composite.state, path)
            self.add_emitter()

    #         for path, instance in self.composite.step_paths.items():
    #             if "emitter" in path:
    #                 remove_path(self.composite.state, path)
    #                 self.add_emitter()

    def reset_paths(self) -> None:
        self.composite.find_instance_paths(self.composite.state)
        self.composite.build_step_network()

    def add_emitter(self) -> None:
        """
        Add an emitter to the composite.
        """

        emitter_state = self._read_emitter_config()

        # set the emitter at the path
        path = tuple(self.emitter_config.get("path", ("emitter",)))
        emitter_state = set_path({}, path, emitter_state)

        self.composite.merge({}, emitter_state)

        # TODO -- this is a hack to get the emitter to show up in the state
        # TODO -- this should be done in the merge function
        _, instance = self.core.slice(self.composite.composition, self.composite.state, path)

        self.emitter_paths[path] = instance
        self.composite.step_paths[path] = instance

        # rebuild the step network
        self.composite.build_step_network()

    def _read_emitter_config(self) -> dict[str | tuple[str, ...], Any]:
        address = self.emitter_config.get("address", "local:ram-emitter")
        config = self.emitter_config.get("config", {})
        mode = self.emitter_config.get("mode", "all")

        if mode == "all":
            inputs = {}
            for key in self.composite.state.keys():
                if is_schema_key(key):  # skip schema keys
                    continue
                if self.core.inherits_from(self.composite.composition[key], "edge"):  # skip edges
                    continue
                inputs[key] = [self.emitter_config.get("inputs", {}).get(key, key)]

        elif mode == "none":
            inputs = self.emitter_config.get("emit", {})

        elif mode == "bridge":
            print("Warning: emitter bridge mode not implemented.")
            inputs = {}

        elif mode == "ports":
            print("Warning: emitter ports mode not implemented.")
            inputs = {}

        if "emit" not in config:
            config["emit"] = {input: "any" for input in inputs}

        return {"_type": "step", "address": address, "config": config, "inputs": inputs}

    def set_value(self, path: list[str], value: Any) -> None:
        # TODO -- make this set the value in the composite using core
        set_path(self.composite.state, path=path, value=value)
        # self.composite[path] = value
        # self.composite.set({}, value, path)

    def get_type(self, type_id: str) -> dict[str, Any]:
        return render_type(type_name_or_dict=self.core.access(type_id), core=self.core)

    def make_document(self) -> dict[str, Any]:
        serialized_state = self.composite.serialize_state()

        # TODO fix RecursionError
        # schema = self.core.representation(self.composite.composition)
        schema = self.composite.serialize_schema()
        # schema = self.composite.composition

        return {
            "state": serialized_state,
            "composition": schema,
        }

    def save(self, json_file_path: Path) -> None:
        document = self.make_document()
        with open(json_file_path, "w") as json_file:
            json.dump(document, json_file, indent=4)
            print(f"Saved file: {json_file_path}")

    def run(self, interval: float) -> None:
        """
        Run the simulation for a given interval.
        """
        if not self.emitter_paths:
            self.add_emitter()

        self.composite.run(interval)

    def step(self) -> None:
        """
        Run the simulation for a single step.
        """
        self.composite.build_step_network()
        self.composite.run_steps(self.composite.to_run)
        # self.composite.run(0)
        # self.composite.update(self.composite.state, 0)


def render_type(type_name_or_dict: str | dict[str, Any], core: ProcessTypes) -> dict[str, Any]:
    type_dict: dict[str, Any] = core.access(type_name_or_dict)
    rendered = {}
    for key, value in type_dict.items():
        if is_schema_key(key):
            if key == "_description":
                rendered["description"] = value
            elif key == "_default":
                rendered["default"] = core.default(type_dict)
        elif isinstance(value, dict):
            rendered[key] = render_type(value, core)
    return rendered


def parse_path(path: list[str] | str | dict[str, Any]) -> list[str] | dict[str, Any]:
    if isinstance(path, dict):
        return {key: parse_path(value) for key, value in path.items()}
    elif isinstance(path, str):
        if path.startswith("/"):
            return path.split("/")[1:]
        else:
            return [path]
    else:
        return path
