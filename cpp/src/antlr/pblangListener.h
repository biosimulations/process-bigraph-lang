
// Generated from pblang.g4 by ANTLR 4.13.1

#pragma once


#include "antlr4-runtime.h"
#include "pblangParser.h"


/**
 * This interface defines an abstract listener for a parse tree produced by pblangParser.
 */
class  pblangListener : public antlr4::tree::ParseTreeListener {
public:

  virtual void enterModel(pblangParser::ModelContext *ctx) = 0;
  virtual void exitModel(pblangParser::ModelContext *ctx) = 0;

  virtual void enterType(pblangParser::TypeContext *ctx) = 0;
  virtual void exitType(pblangParser::TypeContext *ctx) = 0;

  virtual void enterNamedType(pblangParser::NamedTypeContext *ctx) = 0;
  virtual void exitNamedType(pblangParser::NamedTypeContext *ctx) = 0;

  virtual void enterDefaultValue(pblangParser::DefaultValueContext *ctx) = 0;
  virtual void exitDefaultValue(pblangParser::DefaultValueContext *ctx) = 0;

  virtual void enterSchemaItem(pblangParser::SchemaItemContext *ctx) = 0;
  virtual void exitSchemaItem(pblangParser::SchemaItemContext *ctx) = 0;

  virtual void enterStore(pblangParser::StoreContext *ctx) = 0;
  virtual void exitStore(pblangParser::StoreContext *ctx) = 0;

  virtual void enterUnit(pblangParser::UnitContext *ctx) = 0;
  virtual void exitUnit(pblangParser::UnitContext *ctx) = 0;

  virtual void enterSbmlModel(pblangParser::SbmlModelContext *ctx) = 0;
  virtual void exitSbmlModel(pblangParser::SbmlModelContext *ctx) = 0;

  virtual void enterProcessDef(pblangParser::ProcessDefContext *ctx) = 0;
  virtual void exitProcessDef(pblangParser::ProcessDefContext *ctx) = 0;

  virtual void enterProcess(pblangParser::ProcessContext *ctx) = 0;
  virtual void exitProcess(pblangParser::ProcessContext *ctx) = 0;

  virtual void enterCompositeDef(pblangParser::CompositeDefContext *ctx) = 0;
  virtual void exitCompositeDef(pblangParser::CompositeDefContext *ctx) = 0;

  virtual void enterUpdate(pblangParser::UpdateContext *ctx) = 0;
  virtual void exitUpdate(pblangParser::UpdateContext *ctx) = 0;

  virtual void enterDefinition(pblangParser::DefinitionContext *ctx) = 0;
  virtual void exitDefinition(pblangParser::DefinitionContext *ctx) = 0;

  virtual void enterDeclaredParameter(pblangParser::DeclaredParameterContext *ctx) = 0;
  virtual void exitDeclaredParameter(pblangParser::DeclaredParameterContext *ctx) = 0;

  virtual void enterExpression(pblangParser::ExpressionContext *ctx) = 0;
  virtual void exitExpression(pblangParser::ExpressionContext *ctx) = 0;

  virtual void enterAddition(pblangParser::AdditionContext *ctx) = 0;
  virtual void exitAddition(pblangParser::AdditionContext *ctx) = 0;

  virtual void enterMultiplication(pblangParser::MultiplicationContext *ctx) = 0;
  virtual void exitMultiplication(pblangParser::MultiplicationContext *ctx) = 0;

  virtual void enterExponentiation(pblangParser::ExponentiationContext *ctx) = 0;
  virtual void exitExponentiation(pblangParser::ExponentiationContext *ctx) = 0;

  virtual void enterModulo(pblangParser::ModuloContext *ctx) = 0;
  virtual void exitModulo(pblangParser::ModuloContext *ctx) = 0;

  virtual void enterPrimaryExpression(pblangParser::PrimaryExpressionContext *ctx) = 0;
  virtual void exitPrimaryExpression(pblangParser::PrimaryExpressionContext *ctx) = 0;


};
