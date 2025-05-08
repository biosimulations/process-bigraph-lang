from enum import Enum
import sys

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override

from process_bigraph_lang.antlr.pblangListener import pblangListener
from process_bigraph_lang.antlr.pblangParser import pblangParser
from process_bigraph_lang.dsl.model import (
    Model,
    Definition,
    DeclaredParameter,
    BinaryExpression,
    VariableRef,
    NumberLiteral,
    Reference,
    FunctionCall,
    Type,
    DefaultValue,
    Unit,
    ProcessDef,
    SchemaItem,
    TypeRef,
    UnitRef,
    Update,
    SchemaItemRef,
    SbmlModel,
    StoreDef,
    CompositeDef,
    Store,
    PythonPath,
    Process,
)


def float_or_int(value: str) -> float | int:
    f = float(value)
    if f.is_integer():
        return int(f)
    else:
        return f


class SchemaItemParentType(Enum):
    PROCESS_DEF_VARIABLE = "process_def_variable"
    PROCESS_DEF_PARAMETER = "process_def_parameter"
    STORE_STATE_DEF = "store_state_def"
    SBML_MODEL_VARIABLE = "sbml_model_variable"
    SBML_MODEL_PARAMETER = "sbml_model_parameter"


class ASTBuilderListener(pblangListener):
    current_definition: Definition | None
    current_process_def: ProcessDef | None
    current_sbml_model: SbmlModel | None
    current_store_def: StoreDef | None
    current_schema_item_parent_type: SchemaItemParentType | None
    current_composite_def: CompositeDef | None
    current_process: Process | None

    def __init__(self) -> None:
        super().__init__()
        self.model = Model(definitions=[], types=[], units=[], processDefs=[], store_defs=[], compositeDefs=[])
        self.current_definition = None
        self.current_process_def = None
        self.current_store_def = None
        self.current_schema_item_parent_type = None
        self.current_composite_def = None
        self.current_process = None

    @override
    def enterTypeDef(self, ctx: pblangParser.TypeDefContext) -> None:
        type_name = ctx.ID(0).getText()
        default_value = DefaultValue(val=float_or_int(ctx.defaultValue().getText())) if ctx.defaultValue() else None
        super_type = Reference(ref="", ref_text=ctx.ID(1).getText()) if len(ctx.ID()) > 1 else None
        new_type = Type(name=type_name, default=default_value, superType=super_type)
        if ctx.builtin:
            new_type.builtin = "builtin"
        self.model.types.append(new_type)

    @override
    def enterDefinition(self, ctx: pblangParser.DefinitionContext) -> None:
        name = ctx.ID().getText()
        args = [DeclaredParameter(name=param.getText()) for param in ctx.declaredParameter()]
        self.current_definition = Definition(name=name, args=args)

    @override
    def exitDefinition(self, ctx: pblangParser.DefinitionContext) -> None:
        if not self.current_definition:
            raise ValueError("unexpected listener error, current_definition is None")
        if ctx.builtin:
            self.current_definition.builtin = "builtin"
        else:
            expr = self._build_expression(ctx.expression())
            # if not builtin, must have an expression
            if not expr:
                raise ValueError(f"Definition '{self.current_definition.name}' must have an expression.")
            self.current_definition.expr = expr
        self.model.definitions.append(self.current_definition)
        self.current_definition = None

    @override
    def enterUnit(self, ctx: pblangParser.UnitContext) -> None:
        name = ctx.ID(0).getText()
        symbol = ctx.STRING().getText().strip('"') if ctx.STRING() else None
        unit_ref = Reference(ref="", ref_text=ctx.ID(1).getText()) if len(ctx.ID()) > 1 else None
        new_unit = Unit(name=name, symbol=symbol, unit_ref=unit_ref)
        self.model.units.append(new_unit)

    @override
    def enterProcessDef(self, ctx: pblangParser.ProcessDefContext) -> None:
        name = ctx.ID().getText()
        self.current_process_def = ProcessDef(
            name=name, vars=[], params=[], inputs=[], outputs=[], updates=[], python_path=None
        )

    @override
    def exitProcessDef(self, ctx: pblangParser.ProcessDefContext) -> None:
        if not self.current_process_def:
            raise ValueError("unexpected listener error, current_process_def is None")
        self.model.processDefs.append(self.current_process_def)
        self.current_process_def = None

    @override
    def enterPythonPath(self, ctx: pblangParser.PythonPathContext) -> None:
        if not self.current_process_def:
            raise ValueError("unexpected listener error, current_process_def is None")
        path = [part.getText() for part in ctx.ID()]
        self.current_process_def.python_path = PythonPath(path=path)

    def _enterSchemaItemParent(self, schema_item_parent_type: SchemaItemParentType) -> None:
        if self.current_schema_item_parent_type:
            raise ValueError("unexpected listener error, current_schema_item_parent_type is not None")
        self.current_schema_item_parent_type = schema_item_parent_type

    def _exitSchemaItemParent(self, schema_item_parent_type: SchemaItemParentType) -> None:
        if self.current_schema_item_parent_type != schema_item_parent_type:
            raise ValueError(
                f"unexpected listener error, current_schema_item_parent_type is not {schema_item_parent_type}"
            )
        self.current_schema_item_parent_type = None

    @override
    def enterStoreDefStateDef(self, ctx: pblangParser.StoreDefStateDefContext) -> None:
        self._enterSchemaItemParent(SchemaItemParentType.STORE_STATE_DEF)

    @override
    def exitStoreDefStateDef(self, ctx: pblangParser.StoreDefStateDefContext) -> None:
        self._exitSchemaItemParent(SchemaItemParentType.STORE_STATE_DEF)

    @override
    def enterSbmlParameter(self, ctx: pblangParser.SbmlParameterContext) -> None:
        self._enterSchemaItemParent(SchemaItemParentType.SBML_MODEL_PARAMETER)

    @override
    def exitSbmlParameter(self, ctx: pblangParser.SbmlParameterContext) -> None:
        self._exitSchemaItemParent(SchemaItemParentType.SBML_MODEL_PARAMETER)

    @override
    def enterSbmlVariable(self, ctx: pblangParser.SbmlVariableContext) -> None:
        self._enterSchemaItemParent(SchemaItemParentType.SBML_MODEL_VARIABLE)

    @override
    def exitSbmlVariable(self, ctx: pblangParser.SbmlVariableContext) -> None:
        self._exitSchemaItemParent(SchemaItemParentType.SBML_MODEL_VARIABLE)

    @override
    def enterProcessParameter(self, ctx: pblangParser.ProcessParameterContext) -> None:
        self._enterSchemaItemParent(SchemaItemParentType.PROCESS_DEF_PARAMETER)

    @override
    def exitProcessParameter(self, ctx: pblangParser.ProcessParameterContext) -> None:
        self._exitSchemaItemParent(SchemaItemParentType.PROCESS_DEF_PARAMETER)

    @override
    def enterProcessVariable(self, ctx: pblangParser.ProcessVariableContext) -> None:
        self._enterSchemaItemParent(SchemaItemParentType.PROCESS_DEF_VARIABLE)

    @override
    def exitProcessVariable(self, ctx: pblangParser.ProcessVariableContext) -> None:
        self._exitSchemaItemParent(SchemaItemParentType.PROCESS_DEF_VARIABLE)

    @override
    def enterProcessInput(self, ctx: pblangParser.ProcessInputContext) -> None:
        type_ref = TypeRef(ref="", ref_text=ctx.ID().getText())
        if self.current_process_def:
            self.current_process_def.inputs.append(type_ref)
        else:
            raise ValueError("unexpected listener error, current_process_def is None")

    @override
    def enterProcessOutput(self, ctx: pblangParser.ProcessOutputContext) -> None:
        type_ref = TypeRef(ref="", ref_text=ctx.ID().getText())
        if self.current_process_def:
            self.current_process_def.outputs.append(type_ref)
        else:
            raise ValueError("unexpected listener error, current_process_def is None")

    @override
    def enterProcess(self, ctx: pblangParser.ProcessContext) -> None:
        if not self.current_composite_def:
            raise ValueError("unexpected listener error, current_composite_def is None")
        name = ctx.ID(0).getText()
        process_ref = Reference(ref="", ref_text=ctx.ID(1).getText()) if len(ctx.ID()) > 1 else None
        process = Process(name=name, process_def=process_ref, stores=[])
        self.current_composite_def.processes.append(process)

    @override
    def exitProcess(self, ctx: pblangParser.ProcessContext) -> None:
        pass

    @override
    def enterStore(self, ctx: pblangParser.StoreContext) -> None:
        if self.current_composite_def:
            name = ctx.ID(0).getText()
            parent = Reference(ref="", ref_text=ctx.ID(1).getText()) if len(ctx.ID()) > 1 else None
            if not parent:
                raise ValueError("unexpected listener error, parent is None")
            self.current_composite_def.stores.append(Store(name=name, store_def=parent))

    @override
    def exitStore(self, ctx: pblangParser.StoreContext) -> None:
        pass

    @override
    def enterCompositeDef(self, ctx: pblangParser.CompositeDefContext) -> None:
        if self.current_composite_def:
            raise ValueError("unexpected listener error, current_composite_def is not None")
        self.current_composite_def = CompositeDef(name=ctx.ID().getText(), stores=[], processes=[])
        self.model.compositeDefs.append(self.current_composite_def)

    @override
    def exitCompositeDef(self, ctx: pblangParser.CompositeDefContext) -> None:
        if not self.current_composite_def:
            raise ValueError("unexpected listener error, current_composite_def is None")
        self.current_composite_def = None

    @override
    def enterSchemaItem(self, ctx: pblangParser.SchemaItemContext) -> None:
        name = ctx.ID(0).getText()
        type_ref = TypeRef(ref="", ref_text=ctx.ID(1).getText())
        default = DefaultValue(val=float_or_int(ctx.defaultValue().getText())) if ctx.defaultValue() else None
        unit_ref = UnitRef(ref="", ref_text=ctx.ID(2).getText()) if len(ctx.ID()) > 2 else None
        schema_item = SchemaItem(name=name, type=type_ref, default=default, unit_ref=unit_ref)
        if self.current_process_def:
            if self.current_schema_item_parent_type == SchemaItemParentType.PROCESS_DEF_PARAMETER:
                self.current_process_def.params.append(schema_item)
            elif self.current_schema_item_parent_type == SchemaItemParentType.PROCESS_DEF_VARIABLE:
                self.current_process_def.vars.append(schema_item)
            else:
                raise ValueError(
                    f"unexpected listener error, current_schema_item_parent_type is {self.current_schema_item_parent_type}"
                )
        elif self.current_store_def:
            if not self.current_store_def.states:
                self.current_store_def.states = []
            self.current_store_def.states.append(schema_item)

    @override
    def enterStoreDef(self, ctx: pblangParser.StoreDefContext) -> None:
        name = ctx.ID().getText()
        store_def_ref = ctx.storeDefRef().getText() if ctx.storeDefRef() else None
        parent = Reference(ref="", ref_text=ctx.storeDefRef().ID(1).getText()) if len(ctx.ID()) > 1 else None
        self.current_store_def = StoreDef(name=name, parent=parent, states=[])

    @override
    def exitStoreDef(self, ctx: pblangParser.StoreDefContext) -> None:
        if not self.current_store_def:
            raise ValueError("unexpected listener error, current_store is None")
        self.model.store_defs.append(self.current_store_def)
        self.current_store_def = None

    @override
    def enterUpdate(self, ctx: pblangParser.UpdateContext) -> None:
        lhs = SchemaItemRef(ref="", ref_text=ctx.ID().getText())
        rhs = self._build_expression(ctx.expression())
        update = Update(lhs=lhs, rhs=rhs)
        if self.current_process_def:
            self.current_process_def.updates.append(update)

    def _build_expression(
        self, ctx: pblangParser.AdditionContext
    ) -> BinaryExpression | VariableRef | NumberLiteral | FunctionCall:
        if (
            isinstance(ctx, pblangParser.AdditionContext)
            or isinstance(ctx, pblangParser.MultiplicationContext)
            or isinstance(ctx, pblangParser.ExponentiationContext)
            or isinstance(ctx, pblangParser.ModuloContext)
        ):
            left = self._build_expression(ctx.getChild(0))  # First operand
            i = 1
            while i < ctx.getChildCount():
                op = ctx.getChild(i).getText()  # Operator (e.g., +, -)
                right = self._build_expression(ctx.getChild(i + 1))  # Next operand
                left = BinaryExpression(operator=op, left=left, right=right)
                i += 2  # Move to the next operator-operand pair
            return left
        elif isinstance(ctx, pblangParser.PrimaryExpressionContext):
            if ctx.FLOAT():
                return NumberLiteral(value=float(ctx.FLOAT().getText()))
            elif ctx.ID() and ctx.expression():
                func = Reference(ref="", ref_text=ctx.ID().getText())
                args = [self._build_expression(arg) for arg in ctx.expression()]
                return FunctionCall(func=func, args=args)
            elif ctx.ID():
                return VariableRef(variable=Reference(ref="", ref_text=ctx.ID().getText()))
            elif ctx.expression():
                return self._build_expression(ctx.expression())
        elif isinstance(ctx, pblangParser.ExpressionContext):
            # Handle the case where ctx is an ExpressionContext
            if ctx.getChildCount() == 1:
                return self._build_expression(ctx.getChild(0))
            elif ctx.getChildCount() == 3:
                left = self._build_expression(ctx.getChild(0))
                op = ctx.getChild(1).getText()
                right = self._build_expression(ctx.getChild(2))
                return BinaryExpression(operator=op, left=left, right=right)
        raise ValueError(f"Unsupported expression type: {ctx.getText()} of class {ctx.__class__.__name__}")
