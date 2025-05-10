# Generated from pblang.g4 by ANTLR 4.13.1
from antlr4 import *

from process_bigraph_lang.antlr.pblangParser import pblangParser


# This class defines a complete listener for a parse tree produced by pblangParser.
class pblangListener(ParseTreeListener):
    # Enter a parse tree produced by pblangParser#model.
    def enterModel(self, ctx: pblangParser.ModelContext):
        pass

    # Exit a parse tree produced by pblangParser#model.
    def exitModel(self, ctx: pblangParser.ModelContext):
        pass

    # Enter a parse tree produced by pblangParser#typeDef.
    def enterTypeDef(self, ctx: pblangParser.TypeDefContext):
        pass

    # Exit a parse tree produced by pblangParser#typeDef.
    def exitTypeDef(self, ctx: pblangParser.TypeDefContext):
        pass

    # Enter a parse tree produced by pblangParser#namedType.
    def enterNamedType(self, ctx: pblangParser.NamedTypeContext):
        pass

    # Exit a parse tree produced by pblangParser#namedType.
    def exitNamedType(self, ctx: pblangParser.NamedTypeContext):
        pass

    # Enter a parse tree produced by pblangParser#defaultValue.
    def enterDefaultValue(self, ctx: pblangParser.DefaultValueContext):
        pass

    # Exit a parse tree produced by pblangParser#defaultValue.
    def exitDefaultValue(self, ctx: pblangParser.DefaultValueContext):
        pass

    # Enter a parse tree produced by pblangParser#schemaItem.
    def enterSchemaItem(self, ctx: pblangParser.SchemaItemContext):
        pass

    # Exit a parse tree produced by pblangParser#schemaItem.
    def exitSchemaItem(self, ctx: pblangParser.SchemaItemContext):
        pass

    # Enter a parse tree produced by pblangParser#storeDef.
    def enterStoreDef(self, ctx: pblangParser.StoreDefContext):
        pass

    # Exit a parse tree produced by pblangParser#storeDef.
    def exitStoreDef(self, ctx: pblangParser.StoreDefContext):
        pass

    # Enter a parse tree produced by pblangParser#storeDefStateDef.
    def enterStoreDefStateDef(self, ctx: pblangParser.StoreDefStateDefContext):
        pass

    # Exit a parse tree produced by pblangParser#storeDefStateDef.
    def exitStoreDefStateDef(self, ctx: pblangParser.StoreDefStateDefContext):
        pass

    # Enter a parse tree produced by pblangParser#unit.
    def enterUnit(self, ctx: pblangParser.UnitContext):
        pass

    # Exit a parse tree produced by pblangParser#unit.
    def exitUnit(self, ctx: pblangParser.UnitContext):
        pass

    # Enter a parse tree produced by pblangParser#sbmlModel.
    def enterSbmlModel(self, ctx: pblangParser.SbmlModelContext):
        pass

    # Exit a parse tree produced by pblangParser#sbmlModel.
    def exitSbmlModel(self, ctx: pblangParser.SbmlModelContext):
        pass

    # Enter a parse tree produced by pblangParser#sbmlParameter.
    def enterSbmlParameter(self, ctx: pblangParser.SbmlParameterContext):
        pass

    # Exit a parse tree produced by pblangParser#sbmlParameter.
    def exitSbmlParameter(self, ctx: pblangParser.SbmlParameterContext):
        pass

    # Enter a parse tree produced by pblangParser#sbmlVariable.
    def enterSbmlVariable(self, ctx: pblangParser.SbmlVariableContext):
        pass

    # Exit a parse tree produced by pblangParser#sbmlVariable.
    def exitSbmlVariable(self, ctx: pblangParser.SbmlVariableContext):
        pass

    # Enter a parse tree produced by pblangParser#processDef.
    def enterProcessDef(self, ctx: pblangParser.ProcessDefContext):
        pass

    # Exit a parse tree produced by pblangParser#processDef.
    def exitProcessDef(self, ctx: pblangParser.ProcessDefContext):
        pass

    # Enter a parse tree produced by pblangParser#pythonPath.
    def enterPythonPath(self, ctx: pblangParser.PythonPathContext):
        pass

    # Exit a parse tree produced by pblangParser#pythonPath.
    def exitPythonPath(self, ctx: pblangParser.PythonPathContext):
        pass

    # Enter a parse tree produced by pblangParser#processParameter.
    def enterProcessParameter(self, ctx: pblangParser.ProcessParameterContext):
        pass

    # Exit a parse tree produced by pblangParser#processParameter.
    def exitProcessParameter(self, ctx: pblangParser.ProcessParameterContext):
        pass

    # Enter a parse tree produced by pblangParser#processVariable.
    def enterProcessVariable(self, ctx: pblangParser.ProcessVariableContext):
        pass

    # Exit a parse tree produced by pblangParser#processVariable.
    def exitProcessVariable(self, ctx: pblangParser.ProcessVariableContext):
        pass

    # Enter a parse tree produced by pblangParser#processInput.
    def enterProcessInput(self, ctx: pblangParser.ProcessInputContext):
        pass

    # Exit a parse tree produced by pblangParser#processInput.
    def exitProcessInput(self, ctx: pblangParser.ProcessInputContext):
        pass

    # Enter a parse tree produced by pblangParser#processOutput.
    def enterProcessOutput(self, ctx: pblangParser.ProcessOutputContext):
        pass

    # Exit a parse tree produced by pblangParser#processOutput.
    def exitProcessOutput(self, ctx: pblangParser.ProcessOutputContext):
        pass

    # Enter a parse tree produced by pblangParser#process.
    def enterProcess(self, ctx: pblangParser.ProcessContext):
        pass

    # Exit a parse tree produced by pblangParser#process.
    def exitProcess(self, ctx: pblangParser.ProcessContext):
        pass

    # Enter a parse tree produced by pblangParser#store.
    def enterStore(self, ctx: pblangParser.StoreContext):
        pass

    # Exit a parse tree produced by pblangParser#store.
    def exitStore(self, ctx: pblangParser.StoreContext):
        pass

    # Enter a parse tree produced by pblangParser#compositeDef.
    def enterCompositeDef(self, ctx: pblangParser.CompositeDefContext):
        pass

    # Exit a parse tree produced by pblangParser#compositeDef.
    def exitCompositeDef(self, ctx: pblangParser.CompositeDefContext):
        pass

    # Enter a parse tree produced by pblangParser#update.
    def enterUpdate(self, ctx: pblangParser.UpdateContext):
        pass

    # Exit a parse tree produced by pblangParser#update.
    def exitUpdate(self, ctx: pblangParser.UpdateContext):
        pass

    # Enter a parse tree produced by pblangParser#definition.
    def enterDefinition(self, ctx: pblangParser.DefinitionContext):
        pass

    # Exit a parse tree produced by pblangParser#definition.
    def exitDefinition(self, ctx: pblangParser.DefinitionContext):
        pass

    # Enter a parse tree produced by pblangParser#declaredParameter.
    def enterDeclaredParameter(self, ctx: pblangParser.DeclaredParameterContext):
        pass

    # Exit a parse tree produced by pblangParser#declaredParameter.
    def exitDeclaredParameter(self, ctx: pblangParser.DeclaredParameterContext):
        pass

    # Enter a parse tree produced by pblangParser#expression.
    def enterExpression(self, ctx: pblangParser.ExpressionContext):
        pass

    # Exit a parse tree produced by pblangParser#expression.
    def exitExpression(self, ctx: pblangParser.ExpressionContext):
        pass

    # Enter a parse tree produced by pblangParser#addition.
    def enterAddition(self, ctx: pblangParser.AdditionContext):
        pass

    # Exit a parse tree produced by pblangParser#addition.
    def exitAddition(self, ctx: pblangParser.AdditionContext):
        pass

    # Enter a parse tree produced by pblangParser#multiplication.
    def enterMultiplication(self, ctx: pblangParser.MultiplicationContext):
        pass

    # Exit a parse tree produced by pblangParser#multiplication.
    def exitMultiplication(self, ctx: pblangParser.MultiplicationContext):
        pass

    # Enter a parse tree produced by pblangParser#exponentiation.
    def enterExponentiation(self, ctx: pblangParser.ExponentiationContext):
        pass

    # Exit a parse tree produced by pblangParser#exponentiation.
    def exitExponentiation(self, ctx: pblangParser.ExponentiationContext):
        pass

    # Enter a parse tree produced by pblangParser#modulo.
    def enterModulo(self, ctx: pblangParser.ModuloContext):
        pass

    # Exit a parse tree produced by pblangParser#modulo.
    def exitModulo(self, ctx: pblangParser.ModuloContext):
        pass

    # Enter a parse tree produced by pblangParser#primaryExpression.
    def enterPrimaryExpression(self, ctx: pblangParser.PrimaryExpressionContext):
        pass

    # Exit a parse tree produced by pblangParser#primaryExpression.
    def exitPrimaryExpression(self, ctx: pblangParser.PrimaryExpressionContext):
        pass


del pblangParser
