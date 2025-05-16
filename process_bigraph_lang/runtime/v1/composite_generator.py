from typing import Any, cast

from process_bigraph_lang.dsl.model import Model, StoreDef, ProcessDef, Store, Type
from process_bigraph_lang.runtime.v1.process_bigraph_env import ProcessBigraphEnv


def process_composite(model: Model, assembler: ProcessBigraphEnv) -> None:
    for composite_def in model.compositeDefs:
        store_path_to_value_map: dict[str, Any] = {}
        for process in composite_def.processes:
            process_def = cast(ProcessDef, process.process_def.ref_object)
            assert isinstance(process_def, ProcessDef)

            input_bindings: dict[str, list[str]] = {elem.ref_text: [] for elem in process_def.inputs}
            output_bindings: dict[str, list[str]] = {elem.ref_text: [] for elem in process_def.outputs}

            process_config = {}
            for param in process_def.params:
                param_type = cast(Type, param.type.ref_object)
                assert isinstance(param_type, Type)
                process_config[param.name] = (
                    param.default.val if param.default is not None else _determine_builtin_default(param_type)
                )

            for store_ref in process.stores:
                store = cast(Store, store_ref.ref_object)
                assert isinstance(store, Store)
                store_def = cast(StoreDef, store.store_def.ref_object)
                assert isinstance(store_def, StoreDef)

                store_path_str: str = composite_def.name + "::" + store.name
                store_path = [composite_def.name, store.name]

                if store_def.states:
                    for state_def in store_def.states:
                        state_type = cast(Type, state_def.type.ref_object)
                        assert isinstance(state_type, Type)
                        store_path_to_value_map[store_path_str] = (
                            state_def.default.val
                            if state_def.default is not None
                            else _determine_builtin_default(state_type)
                        )

                    for state_def in store_def.states:
                        if state_def.name in input_bindings:
                            input_bindings[state_def.name] = store_path
                        if state_def.name in output_bindings:
                            output_bindings[state_def.name] = store_path

            if not process_def.python_path:
                raise ValueError(f"Process definition {process_def.name} has no python path")

            process_store_path = ()
            if process_def.python_path.path[-1].endswith("Step"):
                assembler.add_step(
                    name=process.name,
                    process_id=".".join(process_def.python_path.path),
                    config=process_config,
                    inputs=input_bindings,
                    outputs=output_bindings,
                    path=process_store_path,
                )
            elif process_def.python_path.path[-1].endswith("Process"):
                assembler.add_process(
                    name=process.name,
                    process_id=".".join(process_def.python_path.path),
                    config=process_config,
                    inputs=input_bindings,
                    outputs=output_bindings,
                    path=process_store_path,
                )
            else:
                raise ValueError(
                    f"Process definition {process_def.name} has an invalid python path, expecting to end with Step or Process"
                )

        for store_path_str in store_path_to_value_map:
            store_path = store_path_str.split("::")
            assembler.set_value(path=store_path, value=store_path_to_value_map[store_path_str])

    assembler.add_emitter()


def _determine_builtin_default(type_to_infer: Type) -> Any:
    if type_to_infer.name == "float":
        return 0.0
    elif type_to_infer.name == "int":
        return 0
    else:
        raise ValueError(f"Unknown built-in default for type `{type_to_infer}`")
