from process_bigraph_lang.dsl.model import Type

from process_bigraph_lang.runtime.v1.process_bigraph_env import ProcessBigraphEnv


def register_types(assembler: ProcessBigraphEnv, types_to_register: list[Type]) -> None:
    for type_to_register in types_to_register:
        if assembler.get_type(type_to_register.name) == {}:
            raise ValueError(f"Type {type_to_register.name} is an unknown type")
        # in the future, we'd attempt to generate a new type
