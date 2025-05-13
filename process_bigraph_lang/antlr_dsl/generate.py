import dataclasses
import tempfile
from os import PathLike
from pathlib import Path
from enum import Enum

from antlr4 import FileStream, CommonTokenStream, ParseTreeWalker  # type: ignore[import-untyped]

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
)


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
    stream = CommonTokenStream(lexer)
    parser = pblangParser(stream)
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
    STORE_STATE = "storeState"  # SchemaItem
    PROCESS_DEF = "processDef"  # ProcessDef
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
        | SchemaItem
        | ProcessDef
        | CompositeDef
        | Store
        | Process
    )


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
            if param.type:
                _bind_ref(param.type, type_symbols)
        for j, var in enumerate(processDef.vars):
            if var.unit_ref:
                _bind_ref(var.unit_ref, unit_symbols)
            if var.type:
                _bind_ref(var.type, type_symbols)
        for j, input_def in enumerate(processDef.inputs):
            _bind_ref(input_def, process_def_var_symbols)
        for j, output_def in enumerate(processDef.outputs):
            _bind_ref(output_def, process_def_var_symbols)
        for j, update_def in enumerate(processDef.updates):
            _bind_ref(update_def.lhs, process_def_var_symbols)
            _bind_expr(update_def.rhs, expr_symbols)

    for i, store_def in enumerate(model.store_defs):
        type_symbols = [e for e in symbol_table if e.ref_type == RefType.TYPE]
        unit_symbols = [e for e in symbol_table if e.ref_type == RefType.UNIT]
        store_def_symbols = [e for e in symbol_table if e.ref_type == RefType.STORE_DEF]
        if store_def.states:
            for j, state in enumerate(store_def.states):
                if state.unit_ref:
                    _bind_ref(state.unit_ref, unit_symbols)
                if state.type:
                    _bind_ref(state.type, type_symbols)
        if store_def.parent:
            _bind_ref(store_def.parent, store_def_symbols)

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
