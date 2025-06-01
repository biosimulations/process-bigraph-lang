import dataclasses
from enum import Enum

from process_bigraph_lang.dsl.ast_model import (
    ASTModel,
    Reference,
    Unit,
    Type,
    Definition,
    SchemaItem,
    Expression,
    DeclaredParameter,
    FunctionCall,
    BinaryExpression,
    VariableRef,
    NumberLiteral,
    StoreNode,
    ProcDef,
    StepDef,
    Parameter,
)


class _RefType(Enum):
    """
    Enum for reference target types.
    """

    UNIT = "unit"  # Unit
    TYPE = "type"  # Type
    DEFINITION = "definition"  # Definition
    DEFINITION_PARAMETER = "definitionParameter"  # DeclaredParameter
    STORE_NODE = "storeNode"  # StoreNode
    STORE_STATE = "storeState"  # SchemaItem
    PROC_DEF = "procDef"  # ProcDef
    STEP_DEF = "stepDef"  # StepDef
    PROC_DEF_VARIABLE = "procDefVariable"  # SchemaItem
    PARAMETER = "Parameter"  # SchemaItem
    STEP_DEF_VARIABLE = "stepDefVariable"  # SchemaItem
    STEP_DEF_PARAMETER = "stepDefParameter"  # SchemaItem
    PROCESS = "process"  # Process
    COMPOSITE_DEF = "compositeDef"  # CompositeDef


@dataclasses.dataclass
class _SymbolTableEntry:
    name: str
    path: str
    ref_type: _RefType
    target_obj: Unit | Type | Definition | DeclaredParameter | StoreNode | SchemaItem | ProcDef | StepDef | Parameter


def _append_store_node_symbols(store_node: StoreNode, symbol_table: list[_SymbolTableEntry], path: str) -> None:
    symbol_table.append(
        _SymbolTableEntry(
            name=store_node.name,
            path=path,
            ref_type=_RefType.STORE_NODE,
            target_obj=store_node,
        )
    )
    if store_node.child_defs:
        for child_store_node in store_node.child_defs:
            _append_store_node_symbols(child_store_node, symbol_table, f"{path}/{child_store_node.name}")


def _create_symbol_table(model: ASTModel) -> list[_SymbolTableEntry]:
    symbol_table: list[_SymbolTableEntry] = []
    for i, unit in enumerate(model.units):
        symbol_table.append(
            _SymbolTableEntry(name=unit.name, path=f"#/units@{i}", ref_type=_RefType.UNIT, target_obj=unit)
        )

    for i, type in enumerate(model.types):
        symbol_table.append(
            _SymbolTableEntry(name=type.name, path=f"#/types@{i}", ref_type=_RefType.TYPE, target_obj=type)
        )

    for i, definition in enumerate(model.definitions):
        symbol_table.append(
            _SymbolTableEntry(
                name=definition.name, path=f"#/definitions@{i}", ref_type=_RefType.DEFINITION, target_obj=definition
            )
        )

        for j, formal_arg in enumerate(definition.args):
            symbol_table.append(
                _SymbolTableEntry(
                    name=formal_arg.name,
                    path=f"#/definitions@{i}/args@{j}",
                    ref_type=_RefType.DEFINITION_PARAMETER,
                    target_obj=formal_arg,
                )
            )

    for i, store_node in enumerate(model.storeNodes):
        _append_store_node_symbols(store_node, symbol_table, f"#/storeNodes@{i}")

    for i, parameter in enumerate(model.parameters):
        symbol_table.append(
            _SymbolTableEntry(
                name=parameter.name, path=f"#/parameter@{i}", ref_type=_RefType.PARAMETER, target_obj=parameter
            )
        )

    for i, proc_def in enumerate(model.procDefs):
        symbol_table.append(
            _SymbolTableEntry(
                name=proc_def.name, path=f"#/procDefs@{i}", ref_type=_RefType.PROC_DEF, target_obj=proc_def
            )
        )
        for j, var in enumerate(proc_def.vars):
            symbol_table.append(
                _SymbolTableEntry(
                    name=var.name,
                    path=f"#/procDefs@{i}/vars@{j}",
                    ref_type=_RefType.PROC_DEF_VARIABLE,
                    target_obj=var,
                )
            )

    for i, step_def in enumerate(model.stepDefs):
        symbol_table.append(
            _SymbolTableEntry(
                name=step_def.name, path=f"#/stepDefs@{i}", ref_type=_RefType.STEP_DEF, target_obj=step_def
            )
        )
        for j, var in enumerate(step_def.vars):
            symbol_table.append(
                _SymbolTableEntry(
                    name=var.name,
                    path=f"#/stepDefs@{i}/vars@{j}",
                    ref_type=_RefType.STEP_DEF_VARIABLE,
                    target_obj=var,
                )
            )

    return symbol_table


def _bind_ref(ref: Reference, symbol_table: list[_SymbolTableEntry]) -> None:
    for entry in symbol_table:
        if entry.name == ref.ref_text:
            ref.ref = entry.path
            ref.ref_object = entry.target_obj
            return
    raise ValueError(f"Reference '{ref.ref_text}' not found in symbol table")


def _bind_expr(expr: Expression, symbol_table: list[_SymbolTableEntry]) -> None:
    if isinstance(expr, VariableRef):
        _bind_ref(expr.variable, symbol_table)
    elif isinstance(expr, BinaryExpression):
        _bind_expr(expr.left, symbol_table)
        _bind_expr(expr.right, symbol_table)
    elif isinstance(expr, FunctionCall):
        def_symbols = [entry for entry in symbol_table if entry.ref_type == _RefType.DEFINITION]
        _bind_ref(expr.func, def_symbols)
        for arg in expr.args:
            _bind_expr(arg, symbol_table)
    elif isinstance(expr, NumberLiteral):
        pass  # No binding needed for literals


def _bind_store_node(store_node: StoreNode, symbol_table: list[_SymbolTableEntry]) -> None:
    type_symbols = [e for e in symbol_table if e.ref_type == _RefType.TYPE]
    proc_def_symbols = [e for e in symbol_table if e.ref_type == _RefType.PROC_DEF]
    step_def_symbols = [e for e in symbol_table if e.ref_type == _RefType.STEP_DEF]
    store_node_symbols = [e for e in symbol_table if e.ref_type == _RefType.STORE_NODE]
    parameter_symbols = [e for e in symbol_table if e.ref_type == _RefType.PARAMETER]
    if store_node.optional_type:
        _bind_ref(store_node.optional_type, type_symbols)

    if store_node.proc_call:
        proc_call = store_node.proc_call
        _bind_ref(proc_call.proc_def_ref, proc_def_symbols)
        for parameter_ref in proc_call.config_node_list.parameter_refs if proc_call.config_node_list else []:
            _bind_ref(parameter_ref, parameter_symbols)
        for store_ref in proc_call.input_node_list.store_node_refs if proc_call.input_node_list else []:
            _bind_ref(store_ref, store_node_symbols)
        for store_ref in proc_call.output_node_list.store_node_refs if proc_call.output_node_list else []:
            _bind_ref(store_ref, store_node_symbols)

    if store_node.step_call:
        step_call = store_node.step_call
        _bind_ref(step_call.step_def_ref, step_def_symbols)
        for parameter_ref in step_call.config_node_list.parameter_refs if step_call.config_node_list else []:
            _bind_ref(parameter_ref, parameter_symbols)
        for store_ref in step_call.input_node_list.store_node_refs if step_call.input_node_list else []:
            _bind_ref(store_ref, store_node_symbols)
        for store_ref in step_call.output_node_list.store_node_refs if step_call.output_node_list else []:
            _bind_ref(store_ref, store_node_symbols)

    if store_node.child_defs:
        for child_store_node in store_node.child_defs:
            _bind_store_node(child_store_node, symbol_table)


def bind_ast_model(model: ASTModel) -> None:
    # 1. generate symbol table with paths and objects
    symbol_table: list[_SymbolTableEntry] = _create_symbol_table(model)

    # 2. bind all references to objects in the symbol table
    for i, definition in enumerate(model.definitions):
        symbols = [
            e
            for e in symbol_table
            if (e.ref_type == _RefType.DEFINITION_PARAMETER and e.path.startswith(f"#/definitions@{i}/args@"))
            or (e.ref_type != _RefType.DEFINITION_PARAMETER)
        ]
        # symbols = symbol_table
        if definition.expr:
            _bind_expr(definition.expr, symbols)

    for i, type in enumerate(model.types):
        symbols = [e for e in symbol_table if e.ref_type == _RefType.TYPE and not e.path.startswith(f"#/types@{i}")]
        if type.superType:
            _bind_ref(type.superType, symbols)

    for i, unit in enumerate(model.units):
        symbols = [e for e in symbol_table if e.ref_type == _RefType.UNIT and not e.path.startswith(f"#/units@{i}")]
        if unit.unit_ref:
            _bind_ref(unit.unit_ref, symbols)

    procdef_or_stepdef_list: list[ProcDef | StepDef] = []
    procdef_or_stepdef_list += model.procDefs
    procdef_or_stepdef_list += model.stepDefs
    for i, procDef_or_stepDef in enumerate(procdef_or_stepdef_list):
        type_symbols = [e for e in symbol_table if e.ref_type == _RefType.TYPE]
        unit_symbols = [e for e in symbol_table if e.ref_type == _RefType.UNIT]
        process_def_var_symbols = [
            e
            for e in symbol_table
            if e.ref_type == _RefType.PROC_DEF_VARIABLE or e.ref_type == _RefType.STEP_DEF_VARIABLE
        ]
        # process_def_param_symbols = [
        #     e
        #     for e in symbol_table
        #     if e.ref_type == RefType.PROC_DEF_VARIABLE or e.ref_type == RefType.STEP_DEF_VARIABLE
        # ]
        # expr_symbols = process_def_param_symbols + process_def_var_symbols + symbol_table
        for j, param_ref in enumerate(procDef_or_stepDef.params):
            if param_ref.unit_ref:
                _bind_ref(param_ref.unit_ref, unit_symbols)
            if param_ref.type_ref:
                _bind_ref(param_ref.type_ref, type_symbols)
        for j, var in enumerate(procDef_or_stepDef.vars):
            if var.unit_ref:
                _bind_ref(var.unit_ref, unit_symbols)
            if var.type_ref:
                _bind_ref(var.type_ref, type_symbols)
        for j, input_def in enumerate(procDef_or_stepDef.inputs):
            _bind_ref(input_def, process_def_var_symbols)
        for j, output_def in enumerate(procDef_or_stepDef.outputs):
            _bind_ref(output_def, process_def_var_symbols)
        # for j, update_def in enumerate(procDef_or_stepDef.updates):
        #     _bind_ref(update_def.lhs, process_def_var_symbols)
        #     _bind_expr(update_def.rhs, expr_symbols)

    for i, store_node in enumerate(model.storeNodes):
        _bind_store_node(store_node, symbol_table)
