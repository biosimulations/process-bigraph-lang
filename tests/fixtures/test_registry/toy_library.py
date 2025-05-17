import os.path
from typing import Any

from process_bigraph_lang.runtime.v1.process_bigraph_env import ProcessBigraphEnv
from tests.fixtures.test_registry.utils import TypedStep, TypedProcess
from typing_extensions import override

complex_number = {
    "real": "float",
    "imag": "float",
}

TYPES_DICT = {
    "complex_number": complex_number,
}


class AddFloatsStep(TypedStep):
    @override
    def inputs(self) -> dict[str, Any]:
        return {"left_hand_addend": "float", "right_hand_addend": "float"}

    @override
    def outputs(self) -> dict[str, Any]:
        return {"result": "float"}

    @override
    def update(self, inputs: dict[str, Any]) -> dict[str, Any]:
        left_hand_addend: float = inputs["left_hand_addend"]
        right_hand_addend: float = inputs["right_hand_addend"]
        result = left_hand_addend + right_hand_addend
        return {"result": result}


class AddFloatsProcess(TypedProcess):
    @override
    def inputs(self) -> dict[str, Any]:
        return {"left_hand_addend": "float", "right_hand_addend": "float"}

    @override
    def outputs(self) -> dict[str, Any]:
        return {"result": "float"}

    @override
    def update(self, inputs: dict[str, Any], interval: float) -> dict[str, Any]:
        left_hand_addend: float = inputs["left_hand_addend"]
        right_hand_addend: float = inputs["right_hand_addend"]
        result = left_hand_addend + right_hand_addend
        return {"result": result}


class SaveFloatToFileStep(TypedStep):
    @override
    def inputs(self) -> dict[str, Any]:
        return {
            "result": "float",
        }

    @override
    def update(self, state: dict[str, Any]) -> dict[str, Any]:
        with open(os.path.expanduser(self.config["output_file_path"]), "w+") as f:
            f.write(str(state["result"]))
        return {}


class AddComplexNumbersStep(TypedStep):
    @override
    def inputs(self) -> dict[str, Any]:
        return {"left_hand_addend": "complex_number", "right_hand_addend": "complex_number"}

    @override
    def outputs(self) -> dict[str, Any]:
        return {"result": "complex_number"}

    @override
    def update(self, inputs: dict[str, Any]) -> dict[str, Any]:
        result = {}
        left_hand_addend = inputs["left_hand_addend"]
        right_hand_addend = inputs["right_hand_addend"]
        result["real"] = left_hand_addend["real"] + right_hand_addend["real"]
        result["imag"] = left_hand_addend["imag"] + right_hand_addend["imag"]
        return {"result": result}


class GetRealFromComplexNumberStep(TypedStep):
    pass


PROCESS_DICT = {
    "AddFloatsStep": AddFloatsStep,
    "AddFloatsProcess": AddFloatsProcess,
    "SaveFloatToFileStep": SaveFloatToFileStep,
    "AddComplexNumbersStep": AddComplexNumbersStep,
    "GetRealFromComplexNumberStep": GetRealFromComplexNumberStep,
}


def register(assembler: ProcessBigraphEnv) -> None:
    for type_name, type_schema in TYPES_DICT.items():
        assembler.core.register("toy.type." + type_name, type_schema)
    for process_name, process in PROCESS_DICT.items():
        assembler.core.register_process("toy." + process_name, process)
