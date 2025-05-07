from enum import Enum

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
    Store,
    SbmlModel,
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
    STORE_STATE = "store_state"
    SBML_MODEL_VARIABLE = "sbml_model_variable"
    SBML_MODEL_PARAMETER = "sbml_model_parameter"


class ASTBuilderListener(pblangListener):
    current_definition: Definition | None
    current_process_def: ProcessDef | None
    current_sbml_model: SbmlModel | None
    current_store: Store | None
    current_schema_item_parent_type: SchemaItemParentType | None

    def __init__(self) -> None:
        super().__init__()
        self.model = Model(definitions=[], types=[], units=[], processDefs=[], stores=[])
        self.current_definition = None
        self.current_process_def = None
        self.current_store = None
        self.current_schema_item_parent_type = None

    def enterType(self, ctx: pblangParser.TypeContext) -> None:
        type_name = ctx.ID(0).getText()
        default_value = DefaultValue(val=float_or_int(ctx.defaultValue().getText())) if ctx.defaultValue() else None
        super_type = Reference(ref="", ref_text=ctx.ID(1).getText()) if len(ctx.ID()) > 1 else None
        new_type = Type(name=type_name, default=default_value, superType=super_type)
        if ctx.builtin:
            new_type.builtin = "builtin"
        self.model.types.append(new_type)

    def enterDefinition(self, ctx: pblangParser.DefinitionContext) -> None:
        name = ctx.ID().getText()
        args = [DeclaredParameter(name=param.getText()) for param in ctx.declaredParameter()]
        self.current_definition = Definition(name=name, args=args)

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

    def enterUnit(self, ctx: pblangParser.UnitContext) -> None:
        name = ctx.ID(0).getText()
        symbol = ctx.STRING().getText().strip('"') if ctx.STRING() else None
        unit_ref = Reference(ref="", ref_text=ctx.ID(1).getText()) if len(ctx.ID()) > 1 else None
        new_unit = Unit(name=name, symbol=symbol, unit_ref=unit_ref)
        self.model.units.append(new_unit)

    def enterProcessDef(self, ctx: pblangParser.ProcessDefContext) -> None:
        name = ctx.ID().getText()
        self.current_process_def = ProcessDef(name=name, params=[], vars=[], inputs=[], outputs=[], updates=[])

    def exitProcessDef(self, ctx: pblangParser.ProcessDefContext) -> None:
        if not self.current_process_def:
            raise ValueError("unexpected listener error, current_process_def is None")
        self.model.processDefs.append(self.current_process_def)
        self.current_process_def = None

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

    def enterStoreState(self, ctx: pblangParser.StoreStateContext) -> None:
        self._enterSchemaItemParent(SchemaItemParentType.STORE_STATE)

    def exitStoreState(self, ctx: pblangParser.StoreStateContext) -> None:
        self._exitSchemaItemParent(SchemaItemParentType.STORE_STATE)

    def enterSbmlParameter(self, ctx: pblangParser.SbmlParameterContext) -> None:
        self._enterSchemaItemParent(SchemaItemParentType.SBML_MODEL_PARAMETER)

    def exitSbmlParameter(self, ctx: pblangParser.SbmlParameterContext) -> None:
        self._exitSchemaItemParent(SchemaItemParentType.SBML_MODEL_PARAMETER)

    def enterSbmlVariable(self, ctx: pblangParser.SbmlVariableContext) -> None:
        self._enterSchemaItemParent(SchemaItemParentType.SBML_MODEL_VARIABLE)

    def exitSbmlVariable(self, ctx: pblangParser.SbmlVariableContext) -> None:
        self._exitSchemaItemParent(SchemaItemParentType.SBML_MODEL_VARIABLE)

    def enterProcessParameter(self, ctx: pblangParser.ProcessParameterContext) -> None:
        self._enterSchemaItemParent(SchemaItemParentType.PROCESS_DEF_PARAMETER)

    def exitProcessParameter(self, ctx: pblangParser.ProcessParameterContext) -> None:
        self._exitSchemaItemParent(SchemaItemParentType.PROCESS_DEF_PARAMETER)

    def enterProcessVariable(self, ctx: pblangParser.ProcessVariableContext) -> None:
        self._enterSchemaItemParent(SchemaItemParentType.PROCESS_DEF_VARIABLE)

    def exitProcessVariable(self, ctx: pblangParser.ProcessVariableContext) -> None:
        self._exitSchemaItemParent(SchemaItemParentType.PROCESS_DEF_VARIABLE)

    def enterProcessInput(self, ctx: pblangParser.ProcessInputContext) -> None:
        type_ref = TypeRef(ref="", ref_text=ctx.ID().getText())
        if self.current_process_def:
            self.current_process_def.inputs.append(type_ref)
        else:
            raise ValueError("unexpected listener error, current_process_def is None")

    def enterProcessOutput(self, ctx: pblangParser.ProcessOutputContext) -> None:
        type_ref = TypeRef(ref="", ref_text=ctx.ID().getText())
        if self.current_process_def:
            self.current_process_def.outputs.append(type_ref)
        else:
            raise ValueError("unexpected listener error, current_process_def is None")

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
        elif self.current_store:
            if not self.current_store.states:
                self.current_store.states = []
            self.current_store.states.append(schema_item)

    def enterStore(self, ctx: pblangParser.StoreContext) -> None:
        name = ctx.ID(0).getText()
        parent = Reference(ref="", ref_text=ctx.ID(1).getText()) if len(ctx.ID()) > 1 else None
        self.current_store = Store(name=name, parent=parent, states=[])

    def exitStore(self, ctx: pblangParser.StoreContext) -> None:
        if not self.current_store:
            raise ValueError("unexpected listener error, current_store is None")
        self.model.stores.append(self.current_store)
        self.current_store = None

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
