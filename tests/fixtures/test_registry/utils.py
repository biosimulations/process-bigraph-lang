from typing import Any

from process_bigraph import Process, Step  # type: ignore[import-untyped]
from process_bigraph import ProcessTypes
from process_bigraph.composite import SyncUpdate  # type: ignore[import-untyped]


class TypedStep(Step):
    def __init__(self, config: dict[str, Any] | None = None, core: ProcessTypes | None = None) -> None:
        super().__init__(config, core)

    def inputs(self) -> dict[str, Any]:
        return {}

    def outputs(self) -> dict[str, Any]:
        return {}

    def invoke(self, state: dict[str, Any], _: float | None = None) -> SyncUpdate:
        return super().invoke(state)

    def update(self, inputs: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("Subclasses should implement this method.")


class TypedProcess(Process):
    def __init__(self, config: dict[str, Any] | None = None, core: ProcessTypes | None = None) -> None:
        super().__init__(config, core)

    def inputs(self) -> dict[str, Any]:
        return {}

    def outputs(self) -> dict[str, Any]:
        return {}

    def invoke(self, state: dict[str, Any], interval: float) -> SyncUpdate:
        return super().invoke(state, interval)

    def update(self, inputs: dict[str, Any], interval: float) -> dict[str, Any]:
        raise NotImplementedError("Subclasses should implement this method.")
