from typing import cast, Any

from process_bigraph_lang.dsl.ast_model import (
    Type,
    ASTModel,
    StoreNode,
    DefaultValue,
    ProcDef,
    StepDef,
    SchemaItem,
    EdgeDef,
    StoreNodeRef,
    Parameter,
)
from process_bigraph_lang.compiler.pb_model import (
    PBModel,
    PBStepSchema,
    PBStepState,
    PBProcessSchema,
    PBProcessState,
    PBStoreSchema,
    PBStoreState,
)


def compile_ast(ast_model: ASTModel) -> PBModel:
    pb_model = PBModel(
        process_schemas=[],
        process_states=[],
        store_schemas=[],
        store_states=[],
        step_schemas=[],
        step_states=[],
        types=[],
    )
    for type_def in ast_model.types:
        if type_def.builtin:
            continue
        type_name = type_def.name
        if type_name not in pb_model.types:
            # pb_type = PBType(name=type_name, type=type_def.type)
            # pb_model.types.append(pb_type)
            pass

    for store_node in ast_model.storeNodes:
        compile_store_node(store_node, pb_model, [])

    # emitter_step = PBStep()
    # pb_model.steps.append(emitter_step)
    return pb_model


def compute_relative_path(target_abs_path: list[str], reference_abs_path: list[str]) -> list[str]:
    # examples:
    # target_path = ["a", "b", "c"] and reference_path = ["a", "b"] return ["c"]
    # target_path = ["a", "b", "c"] and reference_path = ["a", "b", "c"] raise ValueError
    # target_path = ["a", "b", "c"] and reference_path = ["a", "b", "d"] return ["..", "c"]
    # target_path = ["a", "b", "c"] and reference_path = ["a", "d"] return ["..", "..", "b", "c"]
    if not target_abs_path:
        raise ValueError("Both target_path and reference_path must be non-empty lists")
    if target_abs_path == reference_abs_path:
        raise ValueError("Target path and reference path cannot be the same")
    if ".." in target_abs_path or ".." in reference_abs_path:
        raise ValueError("Target path and reference path cannot contain '..'")
    # Find the common prefix length
    common_length = 0
    for i in range(min(len(target_abs_path), len(reference_abs_path))):
        if target_abs_path[i] == reference_abs_path[i]:
            common_length += 1
        else:
            break
    # Calculate the relative path
    relative_path = [".."] * (len(reference_abs_path) - common_length)
    relative_path.extend(target_abs_path[common_length:])
    return relative_path


def compile_store_node(store_node: StoreNode, pb_model: PBModel, store_node_path: list[str]) -> None:
    opt_type: Type | None = None
    if store_node.optional_type:
        opt_type = cast(Type, store_node.optional_type.ref_object)
        assert isinstance(opt_type, Type)

    opt_val: DefaultValue | None = store_node.optional_val
    if opt_val is not None or opt_type is not None:
        # this is a leaf, add a PBStoreSchema and/or a PBStoreState object
        pb_store_schema: PBStoreSchema | None = None
        if opt_type is not None:
            pb_store_schema = PBStoreSchema(
                key=store_node.name,
                path=store_node_path,
                data_type=opt_type.name if opt_type is not None else None,
                default_value=None,
                collection_type=None,
            )
            pb_model.store_schemas.append(pb_store_schema)
        if opt_val is not None:
            pb_model.store_states.append(
                PBStoreState(
                    key=store_node.name,
                    path=store_node_path,
                    store_schema=pb_store_schema,
                    value=opt_val.val,
                )
            )

    if store_node.proc_call is not None:
        proc_call = store_node.proc_call
        proc_def = cast(ProcDef, proc_call.proc_def_ref.ref_object)
        assert isinstance(proc_def, ProcDef)

        address, config_schema_info, input_schema_info, output_schema_info = retrieve_edge_def_fields(proc_def)
        config_schema = {key: val.schema_dict_val for key, val in config_schema_info.items()}
        input_schema = {key: val.schema_dict_val for key, val in input_schema_info.items()}
        output_schema = {key: val.schema_dict_val for key, val in output_schema_info.items()}

        proc_config_state: dict[str, int | float | str | bool] = {}
        if proc_call.config_node_list:
            for parameter_ref, param in zip(proc_call.config_node_list.parameter_refs, proc_def.params):
                parameter: Parameter = cast(Parameter, parameter_ref.ref_object)
                assert isinstance(parameter, Parameter)
                assert parameter.default
                proc_config_state[param.name] = parameter.default.val

        proc_input_state: dict[str, Any] = {}
        if proc_call.input_node_list:
            for store_node_ref, proc_def_ref in zip(proc_call.input_node_list.store_node_refs, proc_def.inputs):
                _, _pb_store_schema, _ = retrieve_store_nodes(store_node_ref, pb_model)
                if _pb_store_schema:
                    rel_path = compute_relative_path(_pb_store_schema.full_path, store_node_path)
                    proc_input_state[proc_def_ref.ref_text] = rel_path

        proc_output_state: dict[str, Any] = {}
        if proc_call.output_node_list:
            for store_node_ref, proc_def_ref in zip(proc_call.output_node_list.store_node_refs, proc_def.outputs):
                _, _pb_store_schema, _ = retrieve_store_nodes(store_node_ref, pb_model)
                if _pb_store_schema:
                    rel_path = compute_relative_path(_pb_store_schema.full_path, store_node_path)
                    proc_output_state[proc_def_ref.ref_text] = rel_path

        pb_process_schema = PBProcessSchema(
            key=store_node.name,
            path=store_node_path,
            address=address,
            config_schema=config_schema,
            input_schema=input_schema,
            output_schema=output_schema,
            default_config_state={},
            default_input_state={},
            default_output_state={},
            collection_info=None,
        )
        pb_model.process_schemas.append(pb_process_schema)

        pb_process_state = PBProcessState(
            key=store_node.name,
            path=store_node_path,
            address=address,
            config_state=proc_config_state,
            input_state=proc_input_state,
            output_state=proc_output_state,
            process_schema=pb_process_schema,
        )
        pb_model.process_states.append(pb_process_state)

    if store_node.step_call is not None:
        step_call = store_node.step_call
        step_def = cast(StepDef, step_call.step_def_ref.ref_object)
        assert isinstance(step_def, StepDef)

        address, config_schema_info, input_schema_info, output_schema_info = retrieve_edge_def_fields(step_def)
        config_schema = {key: val.schema_dict_val for key, val in config_schema_info.items()}
        input_schema = {key: val.schema_dict_val for key, val in input_schema_info.items()}
        output_schema = {key: val.schema_dict_val for key, val in output_schema_info.items()}

        step_config_state: dict[str, int | float | str | bool] = {}
        if step_call.config_node_list:
            for parameter_ref, param in zip(step_call.config_node_list.parameter_refs, step_def.params):
                parameter = cast(Parameter, parameter_ref.ref_object)
                assert isinstance(parameter, Parameter)
                assert parameter.default
                step_config_state[param.name] = parameter.default.val

        step_input_state: dict[str, list[str]] = {}
        if step_call.input_node_list:
            for store_node_ref, step_def_ref in zip(step_call.input_node_list.store_node_refs, step_def.inputs):
                _, _pb_store_schema, _ = retrieve_store_nodes(store_node_ref, pb_model)
                if _pb_store_schema:
                    rel_path = compute_relative_path(_pb_store_schema.full_path, store_node_path)
                    step_input_state[step_def_ref.ref_text] = rel_path

        step_output_state: dict[str, list[str]] = {}
        if step_call.output_node_list:
            for store_node_ref, step_def_ref in zip(step_call.output_node_list.store_node_refs, step_def.outputs):
                _, _pb_store_schema, _ = retrieve_store_nodes(store_node_ref, pb_model)
                if _pb_store_schema:
                    rel_path = compute_relative_path(_pb_store_schema.full_path, store_node_path)
                    step_output_state[step_def_ref.ref_text] = rel_path

        pb_step_schema = PBStepSchema(
            key=store_node.name,
            path=store_node_path,
            address=address,
            config_schema=config_schema,
            input_schema=input_schema,
            output_schema=output_schema,
            default_config_state={},
            default_input_state={},
            default_output_state={},
            collection_info=None,
        )
        pb_model.step_schemas.append(pb_step_schema)

        pb_step_state = PBStepState(
            key=store_node.name,
            path=store_node_path,
            address=address,
            config_state=step_config_state,
            input_state=step_input_state,
            output_state=step_output_state,
            step_schema=pb_step_schema,
        )
        pb_model.step_states.append(pb_step_state)

    for child_node in store_node.child_defs or []:
        compile_store_node(child_node, pb_model, store_node_path + [store_node.name])


def retrieve_store_nodes(
    store_node_ref: StoreNodeRef, pb_model: PBModel
) -> tuple[StoreNode, PBStoreSchema | None, PBStoreState | None]:
    store_node = cast(StoreNode, store_node_ref.ref_object)
    assert isinstance(store_node, StoreNode)
    pb_store_schema: PBStoreSchema | None = next(
        (store_schema for store_schema in pb_model.store_schemas if store_schema.key == store_node.name), None
    )
    pb_store_state: PBStoreState | None = next(
        (store_state for store_state in pb_model.store_states if store_state.key == store_node.name), None
    )
    if not pb_store_schema and not pb_store_state:
        raise ValueError(f"Store definition {store_node.name} not found in model")
    return store_node, pb_store_schema, pb_store_state


class SchemaAndState:
    schema_type: Type | None
    state_val: DefaultValue | None

    def __init__(self, schema_type: Type | None, state_val: DefaultValue | None):
        self.schema_type = schema_type
        self.state_val = state_val

    @property
    def schema_dict_val(self) -> int | float | bool | str:
        if self.schema_type:
            return self.schema_type.name
        elif self.state_val:
            return self.state_val.val
        else:
            raise ValueError("SchemaAndState has no schema type or state value")


def retrieve_edge_def_fields(
    edge_def: EdgeDef,
) -> tuple[str, dict[str, SchemaAndState], dict[str, SchemaAndState], dict[str, SchemaAndState]]:
    if not edge_def.python_path:
        raise ValueError(f"Process or Step definition {edge_def.name} has no python path")
    address: str = ".".join(edge_def.python_path.path)
    config_schema_and_state: dict[str, SchemaAndState] = {}
    input_schema_and_state: dict[str, SchemaAndState] = {}
    output_schema_and_state: dict[str, SchemaAndState] = {}
    for param_item in edge_def.params:
        config_schema_and_state[param_item.name] = get_schema_item_schema_and_state(edge_def, param_item)
    for input_item in edge_def.inputs:
        # get var with same name as input item
        var_item = next((var for var in edge_def.vars if var.name == input_item.ref_text), None)
        if var_item is None:
            raise ValueError(f"Process definition {edge_def.name} has no var with name {input_item.ref_text}")
        input_schema_and_state[input_item.ref_text] = get_schema_item_schema_and_state(edge_def, var_item)
    for output_item in edge_def.outputs:
        # get var with same name as output item
        var_item = next((var for var in edge_def.vars if var.name == output_item.ref_text), None)
        if var_item is None:
            raise ValueError(f"Process definition {edge_def.name} has no var with name {output_item.ref_text}")
        output_schema_and_state[output_item.ref_text] = get_schema_item_schema_and_state(edge_def, var_item)
    return address, config_schema_and_state, input_schema_and_state, output_schema_and_state


def get_schema_item_schema_and_state(proc_or_step_def: EdgeDef, schema_item: SchemaItem) -> SchemaAndState:
    opt_type: Type | None = None
    if schema_item.type_ref is not None:
        opt_type = cast(Type, schema_item.type_ref.ref_object)
        assert isinstance(opt_type, Type)
        if not opt_type.builtin:
            raise ValueError(f"Process or Step definition {proc_or_step_def.name} has non-builtin type {opt_type.name}")
    default_value: DefaultValue | None = schema_item.default
    if opt_type is None and default_value is None:
        raise ValueError(f"Process or Step definition {proc_or_step_def.name} has no type and no default value")
    return SchemaAndState(schema_type=opt_type, state_val=default_value)


def _determine_builtin_default(type_to_infer: Type) -> Any:
    if type_to_infer.name == "float":
        return 0.0
    elif type_to_infer.name == "int":
        return 0
    else:
        raise ValueError(f"Unknown built-in default for type `{type_to_infer}`")
