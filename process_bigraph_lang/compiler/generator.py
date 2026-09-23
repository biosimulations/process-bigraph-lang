from dataclasses import dataclass
from typing import Any

from process_bigraph_lang.compiler.pb_model import (
    PBModel,
    PBProcessSchema,
    PBProcessState,
    PBStepSchema,
    PBStepState,
    PBStoreSchema,
    PBStoreState,
)
from process_bigraph_lang.dsl.ast_model import (
    ArrayLiteral,
    ArrayType,
    ASTModel,
    BoolLiteral,
    CallableLiteral,
    ConnectStatement,
    FloatLiteral,
    InitDecl,
    IntLiteral,
    MapLiteral,
    MapType,
    MemberCall,
    PrimitiveType,
    RemoteCallableType,
    SimpleTypeRef,
    StoreDecl,
    StringLiteral,
    StructLiteral,
    StructType,
    TupleLiteral,
    TupleType,
    TypeAlias,
    TypeRef,
    Value,
    VarDef,
)

# DSL primitive type names that differ from their bigraph-schema names
_PRIMITIVE_SCHEMA_NAMES = {"int": "integer", "bool": "boolean"}


def compile_ast(ast_model: ASTModel) -> PBModel:
    """
    Compile a bound ASTModel (see bind_ast.bind_ast_model) into a PBModel.

    - every `store` and every `let` whose type is not a remote type becomes a store; struct-typed
      stores are split into one store per field, nested under the struct's name
    - a value of a remote type (`Grow(...)`) becomes a step or process at that path
    - `connect` bindings wire edge ports to store paths, relative to the edge's container
    """
    return _Compiler(ast_model).compile()


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


def type_schema(type_ref: TypeRef) -> str | dict[str, Any]:
    """The bigraph-schema type for a DSL type (aliases are replaced by their target type)."""
    if isinstance(type_ref, SimpleTypeRef):
        type_def = type_ref.type.ref_object
        if isinstance(type_def, PrimitiveType):
            return _PRIMITIVE_SCHEMA_NAMES.get(type_def.name, type_def.name)
        if isinstance(type_def, TypeAlias):
            return type_schema(type_def.type)
        if isinstance(type_def, StructType):
            return {field.name: type_schema(field.type) for field in type_def.fields}
        raise ValueError(f"Type '{type_ref.type.ref_text}' has no data schema")
    if isinstance(type_ref, ArrayType):
        element = type_schema(type_ref.elementType)
        return f"list[{element}]" if isinstance(element, str) else {"_type": "list", "_element": element}
    if isinstance(type_ref, MapType):
        if type_schema(type_ref.keyType) != "string":
            raise ValueError("bigraph-schema maps are keyed by strings; map key type must be 'string'")
        value = type_schema(type_ref.valueType)
        return f"map[{value}]" if isinstance(value, str) else {"_type": "map", "_value": value}
    elements = [type_schema(element.type) for element in type_ref.elements]
    if all(isinstance(element, str) for element in elements):
        return f"tuple[{','.join(str(element) for element in elements)}]"
    return {"_type": "tuple", "_values": elements}


def _unalias(type_ref: TypeRef) -> TypeRef:
    while isinstance(type_ref, SimpleTypeRef) and isinstance(type_ref.type.ref_object, TypeAlias):
        type_ref = type_ref.type.ref_object.type
    return type_ref


def _type_def(type_ref: TypeRef) -> Any:
    type_ref = _unalias(type_ref)
    return type_ref.type.ref_object if isinstance(type_ref, SimpleTypeRef) else None


def _chain_path(member_call: MemberCall) -> list[str]:
    prefix = _chain_path(member_call.previous) if member_call.previous else []
    return [*prefix, member_call.element.ref_text]


@dataclass
class _Const:
    """An already-evaluated value (e.g. a struct field of a referenced constant)."""

    value: Any


class _Compiler:
    def __init__(self, ast_model: ASTModel) -> None:
        self.ast_model = ast_model
        self.pb_model = PBModel(
            process_schemas=[],
            process_states=[],
            store_schemas=[],
            store_states=[],
            step_schemas=[],
            step_states=[],
            types=[],
        )
        self.edge_states: dict[tuple[str, ...], PBStepState | PBProcessState] = {}
        self.inits: dict[int, Value] = {}
        for element in ast_model.elements:
            if isinstance(element, InitDecl):
                store = element.store.ref_object
                if id(store) in self.inits:
                    raise ValueError(f"Store '{element.store.ref_text}' is initialized more than once")
                self.inits[id(store)] = element.value

    def compile(self) -> PBModel:
        for element in self.ast_model.elements:
            if isinstance(element, StoreDecl):
                self._declare(element.name, element.type, self.inits.get(id(element)), [])
            elif isinstance(element, VarDef):
                self._declare_var(element)
        for element in self.ast_model.elements:
            if isinstance(element, ConnectStatement):
                self._connect(element)
        return self.pb_model

    def _declare_var(self, var_def: VarDef) -> None:
        if var_def.name is not None:
            self._declare(var_def.name, var_def.type, var_def.value, [])
        elif var_def.lhs is not None:
            # destructuring: let (a: A, b: B): (a: A, b: B) = (a = ..., b = ...);
            values = self._evaluate(var_def.value, var_def.type) if var_def.value is not None else None
            names = [element.name for element in _unalias(var_def.type).elements]  # type: ignore[union-attr]
            for binding in var_def.lhs.bindings:
                value = _Const(values[names.index(binding.name)]) if values is not None else None
                self._declare(binding.name, binding.type, value, [])

    def _declare(
        self, key: str, type_ref: TypeRef, value: Value | _Const | None, path: list[str], default: Value | None = None
    ) -> None:
        type_def = _type_def(type_ref)
        if isinstance(type_def, RemoteCallableType):
            if not isinstance(value, CallableLiteral):
                raise ValueError(f"'{'.'.join([*path, key])}' must be initialized with {type_def.name}(...)")
            self._declare_edge(key, type_def, value, path)
        elif isinstance(type_def, StructType):
            field_values: dict[str, Value | _Const] = {}
            if isinstance(value, StructLiteral):
                field_values = {field.name: field.value for field in value.fields}
            elif value is not None:
                evaluated = value.value if isinstance(value, _Const) else self._evaluate(value, type_ref)
                field_values = {name: _Const(field_value) for name, field_value in evaluated.items()}
            for field in type_def.fields:
                self._declare(field.name, field.type, field_values.get(field.name), [*path, key], field.default)
        else:
            store_schema = PBStoreSchema(
                key=key,
                path=path,
                data_type=type_schema(type_ref),
                default_value=self._evaluate(default, type_ref) if default is not None else None,
            )
            self.pb_model.store_schemas.append(store_schema)
            if value is not None:
                self.pb_model.store_states.append(
                    PBStoreState(
                        key=key,
                        path=path,
                        store_schema=store_schema,
                        value=value.value if isinstance(value, _Const) else self._evaluate(value, type_ref),
                    )
                )

    def _declare_edge(self, key: str, remote: RemoteCallableType, literal: CallableLiteral, path: list[str]) -> None:
        def schema(ports: TupleType | None) -> dict[str, Any]:
            return {port.name: type_schema(port.type) for port in ports.elements} if ports else {}

        config_types = {param.name: param.type for param in remote.config.elements} if remote.config else {}
        config_state = {arg.name: self._evaluate(arg.value, config_types.get(arg.name)) for arg in literal.configArgs}
        edge_fields: dict[str, Any] = dict(
            key=key,
            path=path,
            address=remote.address,
            config_schema=schema(remote.config),
            input_schema=schema(remote.inputs),
            output_schema=schema(remote.outputs),
            default_config_state={},
            default_input_state={},
            default_output_state={},
            collection_info=None,
        )
        state_fields: dict[str, Any] = dict(
            key=key, path=path, address=remote.address, config_state=config_state, input_state={}, output_state={}
        )
        state: PBStepState | PBProcessState
        if remote.kind == "step":
            step_schema = PBStepSchema(**edge_fields)
            state = PBStepState(**state_fields, step_schema=step_schema)
            self.pb_model.step_schemas.append(step_schema)
            self.pb_model.step_states.append(state)
        else:
            process_schema = PBProcessSchema(**edge_fields)
            state = PBProcessState(**state_fields, process_schema=process_schema)
            self.pb_model.process_schemas.append(process_schema)
            self.pb_model.process_states.append(state)
        self.edge_states[tuple([*path, key])] = state

    def _connect(self, connect: ConnectStatement) -> None:
        instance_path = _chain_path(connect.instance)
        state = self.edge_states.get(tuple(instance_path))
        if state is None:
            raise ValueError(f"'{'.'.join(instance_path)}' is not a step or process instance")
        for bindings, wires in (
            (connect.inputBindings, state.input_state),
            (connect.outputBindings, state.output_state),
        ):
            for binding in bindings:
                if binding.name in wires:
                    raise ValueError(
                        f"Port '{binding.name}' of '{'.'.join(instance_path)}' is connected more than once"
                    )
                target_path = _chain_path(binding.variable)
                if not self._is_store_path(target_path):
                    raise ValueError(f"'{'.'.join(target_path)}' is not a store")
                wires[binding.name] = compute_relative_path(target_path, state.path)

    def _is_store_path(self, path: list[str]) -> bool:
        # a leaf store, or a struct-typed store containing leaf stores
        return any(schema.full_path[: len(path)] == path for schema in self.pb_model.store_schemas)

    def _evaluate(self, value: Value, type_ref: TypeRef | None = None) -> Any:
        """Evaluate a constant value; `type_ref` (if known) orders tuples and widens ints to floats."""
        type_ref = _unalias(type_ref) if type_ref is not None else None
        type_def = type_ref.type.ref_object if isinstance(type_ref, SimpleTypeRef) else None
        if isinstance(value, IntLiteral):
            return (
                float(value.value) if isinstance(type_def, PrimitiveType) and type_def.name == "float" else value.value
            )
        if isinstance(value, (FloatLiteral, StringLiteral)):
            return value.value
        if isinstance(value, BoolLiteral):
            return value.value == "true"
        if isinstance(value, StructLiteral):
            field_types = (
                {field.name: field.type for field in type_def.fields} if isinstance(type_def, StructType) else {}
            )
            return {field.name: self._evaluate(field.value, field_types.get(field.name)) for field in value.fields}
        if isinstance(value, ArrayLiteral):
            element_type = type_ref.elementType if isinstance(type_ref, ArrayType) else None
            return [self._evaluate(element, element_type) for element in value.elements]
        if isinstance(value, MapLiteral):
            value_type = type_ref.valueType if isinstance(type_ref, MapType) else None
            return {self._evaluate(entry.key): self._evaluate(entry.value, value_type) for entry in value.entries}
        if isinstance(value, TupleLiteral):
            fields = {field.name: field.value for field in value.fields}
            if isinstance(type_ref, TupleType):
                return tuple(self._evaluate(fields[element.name], element.type) for element in type_ref.elements)
            return tuple(self._evaluate(field_value) for field_value in fields.values())
        if isinstance(value, MemberCall):
            return self._evaluate_reference(value)
        raise ValueError(f"'{value.callable_type.ref_text}(...)' cannot be used as a constant value")

    def _evaluate_reference(self, member_call: MemberCall) -> Any:
        path = _chain_path(member_call)
        root = member_call
        while root.previous is not None:
            root = root.previous
        declaration = root.element.ref_object
        value = declaration.value if isinstance(declaration, VarDef) else self.inits.get(id(declaration))
        if value is None:
            raise ValueError(f"'{path[0]}' has no value to use as a constant")
        result = self._evaluate(value, declaration.type)
        type_ref: TypeRef | None = declaration.type
        for name in path[1:]:
            type_ref = _unalias(type_ref) if type_ref is not None else None
            if isinstance(type_ref, TupleType):
                names = [element.name for element in type_ref.elements]
                type_ref = type_ref.elements[names.index(name)].type
                result = result[names.index(name)]
            else:
                type_def = type_ref.type.ref_object if isinstance(type_ref, SimpleTypeRef) else None
                field_types = {f.name: f.type for f in type_def.fields} if isinstance(type_def, StructType) else {}
                type_ref = field_types.get(name)
                result = result[name]
        return result
