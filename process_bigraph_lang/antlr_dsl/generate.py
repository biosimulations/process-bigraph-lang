import dataclasses
import tempfile
from enum import Enum
from os import PathLike
from pathlib import Path

from antlr4 import FileStream, CommonTokenStream, ParseTreeWalker, Token
from antlr4.error.ErrorListener import ErrorListener

from process_bigraph_lang.antlr.pblangLexer import pblangLexer
from process_bigraph_lang.antlr.pblangParser import pblangParser
from process_bigraph_lang.antlr_dsl.ast_builder_listener import ASTBuilderListener
from process_bigraph_lang.dsl.model import (
    Model,
    Reference,
    Unit,
    Type,
    Definition,
    SchemaItem,
    Expression,
    DeclaredParameter,
    ProcessDef,
    FunctionCall,
    BinaryExpression,
    VariableRef,
    NumberLiteral,
    StoreDef,
    Store,
    CompositeDef,
    Process,
    StoreNode,
    ProcDef,
    StepDef,
    StepCall,
    ProcCall,
    Parameter,
)


class CustomErrorListener(ErrorListener):
    def syntaxError(
        self,
        recognizer: pblangParser | pblangLexer,
        offendingSymbol: Token | None,
        line: int,
        column: int,
        msg: str,
        e: Exception,
    ) -> None:
        raise ValueError(f"Syntax error at line {str(line)}, column {str(column)}: {msg}")


# run cli-native with a filename of a .pblang file
def parse_file(filename: PathLike[str]) -> Model:
    """
    parse a.pblang file using the antlr generated parser into a Model object.

    Args:
        filename (str): The path to the .pblang file to parse.

    Returns:
        Model: The output from the cli-native validation command.
    """

    file_path = Path(filename)
    if not file_path.exists():
        raise FileNotFoundError(filename)
    if not file_path.is_file():
        raise NotADirectoryError(filename)
    if not file_path.name.endswith(".pblang"):
        raise ValueError(f"File {filename} is not a .pblang file")
    if not file_path.is_absolute():
        raise ValueError(f"File {filename} is not an absolute path")

    input_stream = FileStream(fileName=str(file_path))
    lexer = pblangLexer(input_stream)
    lexer.removeErrorListeners()  # remove default ConsoleErrorListener
    lexer.addErrorListener(CustomErrorListener())  # add custom error listener
    stream = CommonTokenStream(lexer)
    parser = pblangParser(stream)
    parser.removeErrorListeners()  # remove default ConsoleErrorListener
    parser.addErrorListener(CustomErrorListener())  # add custom error listener
    tree = parser.model()
    listener = ASTBuilderListener()
    walker = ParseTreeWalker()
    walker.walk(listener, tree)
    model = listener.model
    bind_model(model)
    return model


# run cli-native with a filename of a .pblang file
def parse_str(pblang_str: str) -> Model:
    """
    parse a.pblang file using the antlr generated parser into a Model object.

    Args:
        pblang_str (str): The content of a .pblang file to parse.

    Returns:
        Model: The output from the cli-native validation command.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir) / "test.pblang"
        with open(tmp_path, "w") as f:
            f.write(pblang_str)
            f.flush()
            return parse_file(tmp_path)


class RefType(Enum):
    """
    Enum for reference target types.
    """

    UNIT = "unit"  # Unit
    TYPE = "type"  # Type
    DEFINITION = "definition"  # Definition
    DEFINITION_PARAMETER = "definitionParameter"  # DeclaredParameter
    STORE = "storeDef"  # Store
    STORE_DEF = "storeDef"  # Store
    STORE_NODE = "storeNode"  # StoreNode
    STORE_STATE = "storeState"  # SchemaItem
    PROC_DEF = "procDef"  # ProcDef
    STEP_DEF = "stepDef"  # StepDef
    PROCESS_DEF = "processDef"  # ProcessDef
    PROC_DEF_VARIABLE = "procDefVariable"  # SchemaItem
    PARAMETER = "Parameter"  # SchemaItem
    STEP_DEF_VARIABLE = "stepDefVariable"  # SchemaItem
    STEP_DEF_PARAMETER = "stepDefParameter"  # SchemaItem
    PROCESS_DEF_VARIABLE = "processDefVariable"  # SchemaItem
    PROCESS_DEF_PARAMETER = "processDefParameter"  # SchemaItem
    PROCESS = "process"  # Process
    COMPOSITE_DEF = "compositeDef"  # CompositeDef


@dataclasses.dataclass
class SymbolTableEntry:
    name: str
    path: str
    ref_type: RefType
    target_obj: (
        Unit
        | Type
        | Definition
        | DeclaredParameter
        | StoreDef
        | StoreNode
        | SchemaItem
        | ProcessDef
        | ProcDef
        | StepDef
        | CompositeDef
        | Store
        | Process
        | Parameter
    )


def _append_store_node_symbols(store_node: StoreNode, symbol_table: list[SymbolTableEntry], path: str) -> None:
    symbol_table.append(
        SymbolTableEntry(
            name=store_node.name,
            path=path,
            ref_type=RefType.STORE_NODE,
            target_obj=store_node,
        )
    )
    if store_node.child_defs:
        for child_store_node in store_node.child_defs:
            _append_store_node_symbols(child_store_node, symbol_table, f"{path}/{child_store_node.name}")


def create_symbol_table(model: Model) -> list[SymbolTableEntry]:
    symbol_table: list[SymbolTableEntry] = []
    for i, unit in enumerate(model.units):
        symbol_table.append(
            SymbolTableEntry(name=unit.name, path=f"#/units@{i}", ref_type=RefType.UNIT, target_obj=unit)
        )

    for i, type in enumerate(model.types):
        symbol_table.append(
            SymbolTableEntry(name=type.name, path=f"#/types@{i}", ref_type=RefType.TYPE, target_obj=type)
        )

    for i, definition in enumerate(model.definitions):
        symbol_table.append(
            SymbolTableEntry(
                name=definition.name, path=f"#/definitions@{i}", ref_type=RefType.DEFINITION, target_obj=definition
            )
        )

        for j, formal_arg in enumerate(definition.args):
            symbol_table.append(
                SymbolTableEntry(
                    name=formal_arg.name,
                    path=f"#/definitions@{i}/args@{j}",
                    ref_type=RefType.DEFINITION_PARAMETER,
                    target_obj=formal_arg,
                )
            )

    for i, store_def in enumerate(model.store_defs):
        symbol_table.append(
            SymbolTableEntry(
                name=store_def.name, path=f"#/store_defs@{i}", ref_type=RefType.STORE_DEF, target_obj=store_def
            )
        )
        if store_def.states:
            for j, state in enumerate(store_def.states):
                symbol_table.append(
                    SymbolTableEntry(
                        name=state.name, path=f"#/stores@{i}/states@{j}", ref_type=RefType.STORE_STATE, target_obj=state
                    )
                )

    for i, store_node in enumerate(model.storeNodes):
        _append_store_node_symbols(store_node, symbol_table, f"#/storeNodes@{i}")

    for i, process_def in enumerate(model.processDefs):
        symbol_table.append(
            SymbolTableEntry(
                name=process_def.name, path=f"#/processDefs@{i}", ref_type=RefType.PROCESS_DEF, target_obj=process_def
            )
        )
        for j, var in enumerate(process_def.vars):
            symbol_table.append(
                SymbolTableEntry(
                    name=var.name,
                    path=f"#/processDefs@{i}/vars@{j}",
                    ref_type=RefType.PROCESS_DEF_VARIABLE,
                    target_obj=var,
                )
            )
        for j, param in enumerate(process_def.params):
            symbol_table.append(
                SymbolTableEntry(
                    name=param.name,
                    path=f"#/processDefs@{i}/params@{j}",
                    ref_type=RefType.PROCESS_DEF_PARAMETER,
                    target_obj=param,
                )
            )

    for i, parameter in enumerate(model.parameters):
        symbol_table.append(
            SymbolTableEntry(
                name=parameter.name, path=f"#/parameter@{i}", ref_type=RefType.PARAMETER, target_obj=parameter
            )
        )

    for i, proc_def in enumerate(model.procDefs):
        symbol_table.append(
            SymbolTableEntry(name=proc_def.name, path=f"#/procDefs@{i}", ref_type=RefType.PROC_DEF, target_obj=proc_def)
        )
        for j, var in enumerate(proc_def.vars):
            symbol_table.append(
                SymbolTableEntry(
                    name=var.name,
                    path=f"#/procDefs@{i}/vars@{j}",
                    ref_type=RefType.PROC_DEF_VARIABLE,
                    target_obj=var,
                )
            )

    for i, step_def in enumerate(model.stepDefs):
        symbol_table.append(
            SymbolTableEntry(name=step_def.name, path=f"#/stepDefs@{i}", ref_type=RefType.STEP_DEF, target_obj=step_def)
        )
        for j, var in enumerate(step_def.vars):
            symbol_table.append(
                SymbolTableEntry(
                    name=var.name,
                    path=f"#/stepDefs@{i}/vars@{j}",
                    ref_type=RefType.STEP_DEF_VARIABLE,
                    target_obj=var,
                )
            )

    for i, composite_def in enumerate(model.compositeDefs):
        symbol_table.append(
            SymbolTableEntry(
                name=composite_def.name,
                path=f"#/compositeDefs@{i}",
                ref_type=RefType.COMPOSITE_DEF,
                target_obj=composite_def,
            )
        )
        for j, store in enumerate(composite_def.stores):
            symbol_table.append(
                SymbolTableEntry(
                    name=store.name,
                    path=f"#/compositeDefs@{i}/stores@{j}",
                    ref_type=RefType.STORE,
                    target_obj=store,
                )
            )
        for j, process in enumerate(composite_def.processes):
            symbol_table.append(
                SymbolTableEntry(
                    name=process.name,
                    path=f"#/compositeDefs@{i}/processes@{j}",
                    ref_type=RefType.PROCESS,
                    target_obj=process,
                )
            )

    return symbol_table


def _bind_ref(ref: Reference, symbol_table: list[SymbolTableEntry]) -> None:
    for entry in symbol_table:
        if entry.name == ref.ref_text:
            ref.ref = entry.path
            ref.ref_object = entry.target_obj
            return
    raise ValueError(f"Reference '{ref.ref_text}' not found in symbol table")


def _bind_expr(expr: Expression, symbol_table: list[SymbolTableEntry]) -> None:
    if isinstance(expr, VariableRef):
        _bind_ref(expr.variable, symbol_table)
    elif isinstance(expr, BinaryExpression):
        _bind_expr(expr.left, symbol_table)
        _bind_expr(expr.right, symbol_table)
    elif isinstance(expr, FunctionCall):
        def_symbols = [entry for entry in symbol_table if entry.ref_type == RefType.DEFINITION]
        _bind_ref(expr.func, def_symbols)
        for arg in expr.args:
            _bind_expr(arg, symbol_table)
    elif isinstance(expr, NumberLiteral):
        pass  # No binding needed for literals


def _bind_store_node(store_node: StoreNode, symbol_table: list[SymbolTableEntry]) -> None:
    type_symbols = [e for e in symbol_table if e.ref_type == RefType.TYPE]
    store_def_symbols = [e for e in symbol_table if e.ref_type == RefType.STORE_DEF]
    if store_node.optional_type:
        _bind_ref(store_node.optional_type, type_symbols)
    if store_node.child_defs:
        for child_store_node in store_node.child_defs:
            _bind_store_node(child_store_node, store_def_symbols)


def bind_model(model: Model) -> None:
    # 1. generate symbol table with paths and objects
    symbol_table: list[SymbolTableEntry] = create_symbol_table(model)

    # 2. bind all references to objects in the symbol table
    for i, definition in enumerate(model.definitions):
        symbols = [
            e
            for e in symbol_table
            if (e.ref_type == RefType.DEFINITION_PARAMETER and e.path.startswith(f"#/definitions@{i}/args@"))
            or (e.ref_type != RefType.DEFINITION_PARAMETER)
        ]
        # symbols = symbol_table
        if definition.expr:
            _bind_expr(definition.expr, symbols)

    for i, type in enumerate(model.types):
        symbols = [e for e in symbol_table if e.ref_type == RefType.TYPE and not e.path.startswith(f"#/types@{i}")]
        if type.superType:
            _bind_ref(type.superType, symbols)

    for i, unit in enumerate(model.units):
        symbols = [e for e in symbol_table if e.ref_type == RefType.UNIT and not e.path.startswith(f"#/units@{i}")]
        if unit.unit_ref:
            _bind_ref(unit.unit_ref, symbols)

    for i, processDef in enumerate(model.processDefs):
        type_symbols = [e for e in symbol_table if e.ref_type == RefType.TYPE]
        unit_symbols = [e for e in symbol_table if e.ref_type == RefType.UNIT]
        process_def_var_symbols = [e for e in symbol_table if e.ref_type == RefType.PROCESS_DEF_VARIABLE]
        process_def_param_symbols = [e for e in symbol_table if e.ref_type == RefType.PROCESS_DEF_VARIABLE]
        expr_symbols = process_def_param_symbols + process_def_var_symbols + symbol_table
        for j, param in enumerate(processDef.params):
            if param.unit_ref:
                _bind_ref(param.unit_ref, unit_symbols)
            if param.type_ref:
                _bind_ref(param.type_ref, type_symbols)
        for j, var in enumerate(processDef.vars):
            if var.unit_ref:
                _bind_ref(var.unit_ref, unit_symbols)
            if var.type_ref:
                _bind_ref(var.type_ref, type_symbols)
        for j, input_def in enumerate(processDef.inputs):
            _bind_ref(input_def, process_def_var_symbols)
        for j, output_def in enumerate(processDef.outputs):
            _bind_ref(output_def, process_def_var_symbols)
        for j, update_def in enumerate(processDef.updates):
            _bind_ref(update_def.lhs, process_def_var_symbols)
            _bind_expr(update_def.rhs, expr_symbols)

    procdef_or_stepdef_list: list[ProcDef | StepDef] = []
    procdef_or_stepdef_list += model.procDefs
    procdef_or_stepdef_list += model.stepDefs
    for i, procDef_or_stepDef in enumerate(procdef_or_stepdef_list):
        type_symbols = [e for e in symbol_table if e.ref_type == RefType.TYPE]
        unit_symbols = [e for e in symbol_table if e.ref_type == RefType.UNIT]
        process_def_var_symbols = [
            e
            for e in symbol_table
            if e.ref_type == RefType.PROC_DEF_VARIABLE or e.ref_type == RefType.STEP_DEF_VARIABLE
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

    stepcall_or_proccall_list: list[StepCall | ProcCall] = []
    stepcall_or_proccall_list += model.step_calls
    stepcall_or_proccall_list += model.proc_calls
    for i, stepcall_or_proccall in enumerate(stepcall_or_proccall_list):
        step_def_symbols = [e for e in symbol_table if e.ref_type == RefType.STEP_DEF]
        proc_def_symbols = [e for e in symbol_table if e.ref_type == RefType.PROC_DEF]
        if isinstance(stepcall_or_proccall, ProcCall):
            _bind_ref(stepcall_or_proccall.proc_def_ref, proc_def_symbols)
        elif isinstance(stepcall_or_proccall, StepCall):
            _bind_ref(stepcall_or_proccall.step_def_ref, step_def_symbols)
        else:
            raise ValueError(f"Unknown stepcall or proccall type: {type(stepcall_or_proccall)}")
        store_node_symbols = [e for e in symbol_table if e.ref_type == RefType.STORE_NODE]
        parameter_symbols = [e for e in symbol_table if e.ref_type == RefType.PARAMETER]
        if stepcall_or_proccall.config_node_list:
            for j, parameter_ref in enumerate(stepcall_or_proccall.config_node_list.parameter_refs):
                _bind_ref(parameter_ref, parameter_symbols)
        if stepcall_or_proccall.input_node_list:
            for j, store_ref in enumerate(stepcall_or_proccall.input_node_list.store_node_refs):
                _bind_ref(store_ref, store_node_symbols)
        if stepcall_or_proccall.output_node_list:
            for j, store_ref in enumerate(stepcall_or_proccall.output_node_list.store_node_refs):
                _bind_ref(store_ref, store_node_symbols)

    for i, store_def in enumerate(model.store_defs):
        type_symbols = [e for e in symbol_table if e.ref_type == RefType.TYPE]
        unit_symbols = [e for e in symbol_table if e.ref_type == RefType.UNIT]
        store_def_symbols = [e for e in symbol_table if e.ref_type == RefType.STORE_DEF]
        if store_def.states:
            for j, state in enumerate(store_def.states):
                if state.unit_ref:
                    _bind_ref(state.unit_ref, unit_symbols)
                if state.type_ref:
                    _bind_ref(state.type_ref, type_symbols)
        if store_def.parent:
            _bind_ref(store_def.parent, store_def_symbols)

    for i, store_node in enumerate(model.storeNodes):
        _bind_store_node(store_node, symbol_table)

    for i, composite_def in enumerate(model.compositeDefs):
        process_def_symbols = [e for e in symbol_table if e.ref_type == RefType.PROCESS_DEF]
        store_def_symbols = [e for e in symbol_table if e.ref_type == RefType.STORE_DEF]
        store_symbols = [e for e in symbol_table if e.ref_type == RefType.STORE]
        for j, store in enumerate(composite_def.stores):
            if store.store_def:
                _bind_ref(store.store_def, store_def_symbols)
        for j, process in enumerate(composite_def.processes):
            if process.process_def:
                _bind_ref(process.process_def, process_def_symbols)
                for k, store_ref in enumerate(process.stores):
                    _bind_ref(store_ref, store_symbols)
