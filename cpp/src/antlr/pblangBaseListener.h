
// Generated from pblang.g4 by ANTLR 4.13.1

#pragma once


#include "antlr4-runtime.h"
#include "pblangListener.h"


/**
 * This class provides an empty implementation of pblangListener,
 * which can be extended to create a listener which only needs to handle a subset
 * of the available methods.
 */
class  pblangBaseListener : public pblangListener {
public:

  virtual void enterModel(pblangParser::ModelContext * /*ctx*/) override { }
  virtual void exitModel(pblangParser::ModelContext * /*ctx*/) override { }

  virtual void enterTypeDef(pblangParser::TypeDefContext * /*ctx*/) override { }
  virtual void exitTypeDef(pblangParser::TypeDefContext * /*ctx*/) override { }

  virtual void enterNamedType(pblangParser::NamedTypeContext * /*ctx*/) override { }
  virtual void exitNamedType(pblangParser::NamedTypeContext * /*ctx*/) override { }

  virtual void enterDefaultValue(pblangParser::DefaultValueContext * /*ctx*/) override { }
  virtual void exitDefaultValue(pblangParser::DefaultValueContext * /*ctx*/) override { }

  virtual void enterSchemaItem(pblangParser::SchemaItemContext * /*ctx*/) override { }
  virtual void exitSchemaItem(pblangParser::SchemaItemContext * /*ctx*/) override { }

  virtual void enterStoreDefRef(pblangParser::StoreDefRefContext * /*ctx*/) override { }
  virtual void exitStoreDefRef(pblangParser::StoreDefRefContext * /*ctx*/) override { }

  virtual void enterStoreDef(pblangParser::StoreDefContext * /*ctx*/) override { }
  virtual void exitStoreDef(pblangParser::StoreDefContext * /*ctx*/) override { }

  virtual void enterStoreDefStateDef(pblangParser::StoreDefStateDefContext * /*ctx*/) override { }
  virtual void exitStoreDefStateDef(pblangParser::StoreDefStateDefContext * /*ctx*/) override { }

  virtual void enterUnit(pblangParser::UnitContext * /*ctx*/) override { }
  virtual void exitUnit(pblangParser::UnitContext * /*ctx*/) override { }

  virtual void enterSbmlModel(pblangParser::SbmlModelContext * /*ctx*/) override { }
  virtual void exitSbmlModel(pblangParser::SbmlModelContext * /*ctx*/) override { }

  virtual void enterSbmlParameter(pblangParser::SbmlParameterContext * /*ctx*/) override { }
  virtual void exitSbmlParameter(pblangParser::SbmlParameterContext * /*ctx*/) override { }

  virtual void enterSbmlVariable(pblangParser::SbmlVariableContext * /*ctx*/) override { }
  virtual void exitSbmlVariable(pblangParser::SbmlVariableContext * /*ctx*/) override { }

  virtual void enterProcessDef(pblangParser::ProcessDefContext * /*ctx*/) override { }
  virtual void exitProcessDef(pblangParser::ProcessDefContext * /*ctx*/) override { }

  virtual void enterPythonPath(pblangParser::PythonPathContext * /*ctx*/) override { }
  virtual void exitPythonPath(pblangParser::PythonPathContext * /*ctx*/) override { }

  virtual void enterProcessParameter(pblangParser::ProcessParameterContext * /*ctx*/) override { }
  virtual void exitProcessParameter(pblangParser::ProcessParameterContext * /*ctx*/) override { }

  virtual void enterProcessVariable(pblangParser::ProcessVariableContext * /*ctx*/) override { }
  virtual void exitProcessVariable(pblangParser::ProcessVariableContext * /*ctx*/) override { }

  virtual void enterProcessInput(pblangParser::ProcessInputContext * /*ctx*/) override { }
  virtual void exitProcessInput(pblangParser::ProcessInputContext * /*ctx*/) override { }

  virtual void enterProcessOutput(pblangParser::ProcessOutputContext * /*ctx*/) override { }
  virtual void exitProcessOutput(pblangParser::ProcessOutputContext * /*ctx*/) override { }

  virtual void enterProcess(pblangParser::ProcessContext * /*ctx*/) override { }
  virtual void exitProcess(pblangParser::ProcessContext * /*ctx*/) override { }

  virtual void enterStore(pblangParser::StoreContext * /*ctx*/) override { }
  virtual void exitStore(pblangParser::StoreContext * /*ctx*/) override { }

  virtual void enterCompositeDef(pblangParser::CompositeDefContext * /*ctx*/) override { }
  virtual void exitCompositeDef(pblangParser::CompositeDefContext * /*ctx*/) override { }

  virtual void enterUpdate(pblangParser::UpdateContext * /*ctx*/) override { }
  virtual void exitUpdate(pblangParser::UpdateContext * /*ctx*/) override { }

  virtual void enterDefinition(pblangParser::DefinitionContext * /*ctx*/) override { }
  virtual void exitDefinition(pblangParser::DefinitionContext * /*ctx*/) override { }

  virtual void enterDeclaredParameter(pblangParser::DeclaredParameterContext * /*ctx*/) override { }
  virtual void exitDeclaredParameter(pblangParser::DeclaredParameterContext * /*ctx*/) override { }

  virtual void enterExpression(pblangParser::ExpressionContext * /*ctx*/) override { }
  virtual void exitExpression(pblangParser::ExpressionContext * /*ctx*/) override { }

  virtual void enterAddition(pblangParser::AdditionContext * /*ctx*/) override { }
  virtual void exitAddition(pblangParser::AdditionContext * /*ctx*/) override { }

  virtual void enterMultiplication(pblangParser::MultiplicationContext * /*ctx*/) override { }
  virtual void exitMultiplication(pblangParser::MultiplicationContext * /*ctx*/) override { }

  virtual void enterExponentiation(pblangParser::ExponentiationContext * /*ctx*/) override { }
  virtual void exitExponentiation(pblangParser::ExponentiationContext * /*ctx*/) override { }

  virtual void enterModulo(pblangParser::ModuloContext * /*ctx*/) override { }
  virtual void exitModulo(pblangParser::ModuloContext * /*ctx*/) override { }

  virtual void enterPrimaryExpression(pblangParser::PrimaryExpressionContext * /*ctx*/) override { }
  virtual void exitPrimaryExpression(pblangParser::PrimaryExpressionContext * /*ctx*/) override { }


  virtual void enterEveryRule(antlr4::ParserRuleContext * /*ctx*/) override { }
  virtual void exitEveryRule(antlr4::ParserRuleContext * /*ctx*/) override { }
  virtual void visitTerminal(antlr4::tree::TerminalNode * /*node*/) override { }
  virtual void visitErrorNode(antlr4::tree::ErrorNode * /*node*/) override { }

};
