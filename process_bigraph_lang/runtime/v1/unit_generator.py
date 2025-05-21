from process_bigraph_lang.dsl.ast_model import Unit
from process_bigraph_lang.runtime.v1.process_bigraph_env import ProcessBigraphEnv


def register_units(assembler: ProcessBigraphEnv, units_to_register: list[Unit]) -> None:
    for unit_to_register in units_to_register:
        pass
        # if 0 == assembler.get_type(unit_to_register.name).size:
        #     raise ValueError(f"Type {unit_to_register.name} is an unknown type")
        # in the future, we'd attempt to generate a new type
