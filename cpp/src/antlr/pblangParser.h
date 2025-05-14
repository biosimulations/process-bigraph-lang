
// Generated from pblang.g4 by ANTLR 4.13.1

#pragma once


#include "antlr4-runtime.h"




class  pblangParser : public antlr4::Parser {
public:
  enum {
    T__0 = 1, T__1 = 2, T__2 = 3, T__3 = 4, T__4 = 5, T__5 = 6, T__6 = 7,
    T__7 = 8, T__8 = 9, T__9 = 10, T__10 = 11, T__11 = 12, T__12 = 13, T__13 = 14,
    T__14 = 15, T__15 = 16, T__16 = 17, T__17 = 18, T__18 = 19, T__19 = 20,
    T__20 = 21, T__21 = 22, T__22 = 23, T__23 = 24, T__24 = 25, T__25 = 26,
    T__26 = 27, T__27 = 28, T__28 = 29, T__29 = 30, T__30 = 31, T__31 = 32,
    T__32 = 33, T__33 = 34, T__34 = 35, T__35 = 36, T__36 = 37, T__37 = 38,
    T__38 = 39, T__39 = 40, T__40 = 41, ID = 42, FLOAT = 43, INT = 44, STRING = 45,
    WS = 46, ML_COMMENT = 47, SL_COMMENT = 48
  };

  enum {
    RuleModel = 0, RuleTypeDef = 1, RuleNamedType = 2, RuleDefaultValue = 3,
    RuleSchemaItem = 4, RuleStoreDef = 5, RuleStoreDefStateDef = 6, RuleUnit = 7,
    RuleSbmlModel = 8, RuleSbmlParameter = 9, RuleSbmlVariable = 10, RuleProcessDef = 11,
    RulePythonPath = 12, RuleProcessParameter = 13, RuleProcessVariable = 14,
    RuleProcessInput = 15, RuleProcessOutput = 16, RuleProcess = 17, RuleStore = 18,
    RuleCompositeDef = 19, RuleUpdate = 20, RuleDefinition = 21, RuleDeclaredParameter = 22,
    RuleExpression = 23, RuleAddition = 24, RuleMultiplication = 25, RuleExponentiation = 26,
    RuleModulo = 27, RulePrimaryExpression = 28
  };

  explicit pblangParser(antlr4::TokenStream *input);

  pblangParser(antlr4::TokenStream *input, const antlr4::atn::ParserATNSimulatorOptions &options);

  ~pblangParser() override;

  std::string getGrammarFileName() const override;

  const antlr4::atn::ATN& getATN() const override;

  const std::vector<std::string>& getRuleNames() const override;

  const antlr4::dfa::Vocabulary& getVocabulary() const override;

  antlr4::atn::SerializedATNView getSerializedATN() const override;


  class ModelContext;
  class TypeDefContext;
  class NamedTypeContext;
  class DefaultValueContext;
  class SchemaItemContext;
  class StoreDefContext;
  class StoreDefStateDefContext;
  class UnitContext;
  class SbmlModelContext;
  class SbmlParameterContext;
  class SbmlVariableContext;
  class ProcessDefContext;
  class PythonPathContext;
  class ProcessParameterContext;
  class ProcessVariableContext;
  class ProcessInputContext;
  class ProcessOutputContext;
  class ProcessContext;
  class StoreContext;
  class CompositeDefContext;
  class UpdateContext;
  class DefinitionContext;
  class DeclaredParameterContext;
  class ExpressionContext;
  class AdditionContext;
  class MultiplicationContext;
  class ExponentiationContext;
  class ModuloContext;
  class PrimaryExpressionContext;

  class  ModelContext : public antlr4::ParserRuleContext {
  public:
    ModelContext(antlr4::ParserRuleContext *parent, size_t invokingState);
    virtual size_t getRuleIndex() const override;
    antlr4::tree::TerminalNode *EOF();
    std::vector<TypeDefContext *> typeDef();
    TypeDefContext* typeDef(size_t i);
    std::vector<DefinitionContext *> definition();
    DefinitionContext* definition(size_t i);
    std::vector<UnitContext *> unit();
    UnitContext* unit(size_t i);
    std::vector<ProcessDefContext *> processDef();
    ProcessDefContext* processDef(size_t i);
    std::vector<StoreDefContext *> storeDef();
    StoreDefContext* storeDef(size_t i);
    std::vector<CompositeDefContext *> compositeDef();
    CompositeDefContext* compositeDef(size_t i);
    std::vector<SbmlModelContext *> sbmlModel();
    SbmlModelContext* sbmlModel(size_t i);

    virtual void enterRule(antlr4::tree::ParseTreeListener *listener) override;
    virtual void exitRule(antlr4::tree::ParseTreeListener *listener) override;

  };

  ModelContext* model();

  class  TypeDefContext : public antlr4::ParserRuleContext {
  public:
    antlr4::Token *name = nullptr;
    antlr4::Token *builtin = nullptr;
    TypeDefContext(antlr4::ParserRuleContext *parent, size_t invokingState);
    virtual size_t getRuleIndex() const override;
    std::vector<antlr4::tree::TerminalNode *> ID();
    antlr4::tree::TerminalNode* ID(size_t i);
    DefaultValueContext *defaultValue();
    std::vector<NamedTypeContext *> namedType();
    NamedTypeContext* namedType(size_t i);

    virtual void enterRule(antlr4::tree::ParseTreeListener *listener) override;
    virtual void exitRule(antlr4::tree::ParseTreeListener *listener) override;

  };

  TypeDefContext* typeDef();

  class  NamedTypeContext : public antlr4::ParserRuleContext {
  public:
    antlr4::Token *name = nullptr;
    antlr4::Token *optional_type_ref = nullptr;
    antlr4::Token *type_ref = nullptr;
    antlr4::Token *unit_ref = nullptr;
    NamedTypeContext(antlr4::ParserRuleContext *parent, size_t invokingState);
    virtual size_t getRuleIndex() const override;
    std::vector<antlr4::tree::TerminalNode *> ID();
    antlr4::tree::TerminalNode* ID(size_t i);
    DefaultValueContext *defaultValue();

    virtual void enterRule(antlr4::tree::ParseTreeListener *listener) override;
    virtual void exitRule(antlr4::tree::ParseTreeListener *listener) override;

  };

  NamedTypeContext* namedType();

  class  DefaultValueContext : public antlr4::ParserRuleContext {
  public:
    DefaultValueContext(antlr4::ParserRuleContext *parent, size_t invokingState);
    virtual size_t getRuleIndex() const override;
    antlr4::tree::TerminalNode *INT();
    antlr4::tree::TerminalNode *FLOAT();
    antlr4::tree::TerminalNode *STRING();

    virtual void enterRule(antlr4::tree::ParseTreeListener *listener) override;
    virtual void exitRule(antlr4::tree::ParseTreeListener *listener) override;

  };

  DefaultValueContext* defaultValue();

  class  SchemaItemContext : public antlr4::ParserRuleContext {
  public:
    antlr4::Token *name = nullptr;
    antlr4::Token *type_ref = nullptr;
    antlr4::Token *unit_ref = nullptr;
    SchemaItemContext(antlr4::ParserRuleContext *parent, size_t invokingState);
    virtual size_t getRuleIndex() const override;
    std::vector<antlr4::tree::TerminalNode *> ID();
    antlr4::tree::TerminalNode* ID(size_t i);
    DefaultValueContext *defaultValue();

    virtual void enterRule(antlr4::tree::ParseTreeListener *listener) override;
    virtual void exitRule(antlr4::tree::ParseTreeListener *listener) override;

  };

  SchemaItemContext* schemaItem();

  class  StoreDefContext : public antlr4::ParserRuleContext {
  public:
    antlr4::Token *name = nullptr;
    antlr4::Token *store_def_ref = nullptr;
    StoreDefContext(antlr4::ParserRuleContext *parent, size_t invokingState);
    virtual size_t getRuleIndex() const override;
    std::vector<antlr4::tree::TerminalNode *> ID();
    antlr4::tree::TerminalNode* ID(size_t i);
    std::vector<StoreDefStateDefContext *> storeDefStateDef();
    StoreDefStateDefContext* storeDefStateDef(size_t i);

    virtual void enterRule(antlr4::tree::ParseTreeListener *listener) override;
    virtual void exitRule(antlr4::tree::ParseTreeListener *listener) override;

  };

  StoreDefContext* storeDef();

  class  StoreDefStateDefContext : public antlr4::ParserRuleContext {
  public:
    StoreDefStateDefContext(antlr4::ParserRuleContext *parent, size_t invokingState);
    virtual size_t getRuleIndex() const override;
    SchemaItemContext *schemaItem();

    virtual void enterRule(antlr4::tree::ParseTreeListener *listener) override;
    virtual void exitRule(antlr4::tree::ParseTreeListener *listener) override;

  };

  StoreDefStateDefContext* storeDefStateDef();

  class  UnitContext : public antlr4::ParserRuleContext {
  public:
    antlr4::Token *name = nullptr;
    UnitContext(antlr4::ParserRuleContext *parent, size_t invokingState);
    virtual size_t getRuleIndex() const override;
    std::vector<antlr4::tree::TerminalNode *> ID();
    antlr4::tree::TerminalNode* ID(size_t i);
    antlr4::tree::TerminalNode *STRING();

    virtual void enterRule(antlr4::tree::ParseTreeListener *listener) override;
    virtual void exitRule(antlr4::tree::ParseTreeListener *listener) override;

  };

  UnitContext* unit();

  class  SbmlModelContext : public antlr4::ParserRuleContext {
  public:
    antlr4::Token *name = nullptr;
    SbmlModelContext(antlr4::ParserRuleContext *parent, size_t invokingState);
    virtual size_t getRuleIndex() const override;
    antlr4::tree::TerminalNode *STRING();
    antlr4::tree::TerminalNode *ID();
    std::vector<SbmlParameterContext *> sbmlParameter();
    SbmlParameterContext* sbmlParameter(size_t i);
    std::vector<SbmlVariableContext *> sbmlVariable();
    SbmlVariableContext* sbmlVariable(size_t i);

    virtual void enterRule(antlr4::tree::ParseTreeListener *listener) override;
    virtual void exitRule(antlr4::tree::ParseTreeListener *listener) override;

  };

  SbmlModelContext* sbmlModel();

  class  SbmlParameterContext : public antlr4::ParserRuleContext {
  public:
    SbmlParameterContext(antlr4::ParserRuleContext *parent, size_t invokingState);
    virtual size_t getRuleIndex() const override;
    SchemaItemContext *schemaItem();

    virtual void enterRule(antlr4::tree::ParseTreeListener *listener) override;
    virtual void exitRule(antlr4::tree::ParseTreeListener *listener) override;

  };

  SbmlParameterContext* sbmlParameter();

  class  SbmlVariableContext : public antlr4::ParserRuleContext {
  public:
    SbmlVariableContext(antlr4::ParserRuleContext *parent, size_t invokingState);
    virtual size_t getRuleIndex() const override;
    SchemaItemContext *schemaItem();

    virtual void enterRule(antlr4::tree::ParseTreeListener *listener) override;
    virtual void exitRule(antlr4::tree::ParseTreeListener *listener) override;

  };

  SbmlVariableContext* sbmlVariable();

  class  ProcessDefContext : public antlr4::ParserRuleContext {
  public:
    ProcessDefContext(antlr4::ParserRuleContext *parent, size_t invokingState);
    virtual size_t getRuleIndex() const override;
    antlr4::tree::TerminalNode *ID();
    PythonPathContext *pythonPath();
    std::vector<ProcessParameterContext *> processParameter();
    ProcessParameterContext* processParameter(size_t i);
    std::vector<ProcessVariableContext *> processVariable();
    ProcessVariableContext* processVariable(size_t i);
    std::vector<ProcessInputContext *> processInput();
    ProcessInputContext* processInput(size_t i);
    std::vector<ProcessOutputContext *> processOutput();
    ProcessOutputContext* processOutput(size_t i);
    std::vector<UpdateContext *> update();
    UpdateContext* update(size_t i);

    virtual void enterRule(antlr4::tree::ParseTreeListener *listener) override;
    virtual void exitRule(antlr4::tree::ParseTreeListener *listener) override;

  };

  ProcessDefContext* processDef();

  class  PythonPathContext : public antlr4::ParserRuleContext {
  public:
    PythonPathContext(antlr4::ParserRuleContext *parent, size_t invokingState);
    virtual size_t getRuleIndex() const override;
    std::vector<antlr4::tree::TerminalNode *> ID();
    antlr4::tree::TerminalNode* ID(size_t i);

    virtual void enterRule(antlr4::tree::ParseTreeListener *listener) override;
    virtual void exitRule(antlr4::tree::ParseTreeListener *listener) override;

  };

  PythonPathContext* pythonPath();

  class  ProcessParameterContext : public antlr4::ParserRuleContext {
  public:
    ProcessParameterContext(antlr4::ParserRuleContext *parent, size_t invokingState);
    virtual size_t getRuleIndex() const override;
    SchemaItemContext *schemaItem();

    virtual void enterRule(antlr4::tree::ParseTreeListener *listener) override;
    virtual void exitRule(antlr4::tree::ParseTreeListener *listener) override;

  };

  ProcessParameterContext* processParameter();

  class  ProcessVariableContext : public antlr4::ParserRuleContext {
  public:
    ProcessVariableContext(antlr4::ParserRuleContext *parent, size_t invokingState);
    virtual size_t getRuleIndex() const override;
    SchemaItemContext *schemaItem();

    virtual void enterRule(antlr4::tree::ParseTreeListener *listener) override;
    virtual void exitRule(antlr4::tree::ParseTreeListener *listener) override;

  };

  ProcessVariableContext* processVariable();

  class  ProcessInputContext : public antlr4::ParserRuleContext {
  public:
    ProcessInputContext(antlr4::ParserRuleContext *parent, size_t invokingState);
    virtual size_t getRuleIndex() const override;
    antlr4::tree::TerminalNode *ID();

    virtual void enterRule(antlr4::tree::ParseTreeListener *listener) override;
    virtual void exitRule(antlr4::tree::ParseTreeListener *listener) override;

  };

  ProcessInputContext* processInput();

  class  ProcessOutputContext : public antlr4::ParserRuleContext {
  public:
    ProcessOutputContext(antlr4::ParserRuleContext *parent, size_t invokingState);
    virtual size_t getRuleIndex() const override;
    antlr4::tree::TerminalNode *ID();

    virtual void enterRule(antlr4::tree::ParseTreeListener *listener) override;
    virtual void exitRule(antlr4::tree::ParseTreeListener *listener) override;

  };

  ProcessOutputContext* processOutput();

  class  ProcessContext : public antlr4::ParserRuleContext {
  public:
    antlr4::Token *name = nullptr;
    antlr4::Token *process_def_ref = nullptr;
    antlr4::Token *idToken = nullptr;
    std::vector<antlr4::Token *> store_def_refs;
    ProcessContext(antlr4::ParserRuleContext *parent, size_t invokingState);
    virtual size_t getRuleIndex() const override;
    std::vector<antlr4::tree::TerminalNode *> ID();
    antlr4::tree::TerminalNode* ID(size_t i);

    virtual void enterRule(antlr4::tree::ParseTreeListener *listener) override;
    virtual void exitRule(antlr4::tree::ParseTreeListener *listener) override;

  };

  ProcessContext* process();

  class  StoreContext : public antlr4::ParserRuleContext {
  public:
    antlr4::Token *name = nullptr;
    antlr4::Token *store_def = nullptr;
    StoreContext(antlr4::ParserRuleContext *parent, size_t invokingState);
    virtual size_t getRuleIndex() const override;
    std::vector<antlr4::tree::TerminalNode *> ID();
    antlr4::tree::TerminalNode* ID(size_t i);

    virtual void enterRule(antlr4::tree::ParseTreeListener *listener) override;
    virtual void exitRule(antlr4::tree::ParseTreeListener *listener) override;

  };

  StoreContext* store();

  class  CompositeDefContext : public antlr4::ParserRuleContext {
  public:
    antlr4::Token *name = nullptr;
    CompositeDefContext(antlr4::ParserRuleContext *parent, size_t invokingState);
    virtual size_t getRuleIndex() const override;
    antlr4::tree::TerminalNode *ID();
    std::vector<StoreContext *> store();
    StoreContext* store(size_t i);
    std::vector<ProcessContext *> process();
    ProcessContext* process(size_t i);

    virtual void enterRule(antlr4::tree::ParseTreeListener *listener) override;
    virtual void exitRule(antlr4::tree::ParseTreeListener *listener) override;

  };

  CompositeDefContext* compositeDef();

  class  UpdateContext : public antlr4::ParserRuleContext {
  public:
    antlr4::Token *lhs = nullptr;
    UpdateContext(antlr4::ParserRuleContext *parent, size_t invokingState);
    virtual size_t getRuleIndex() const override;
    ExpressionContext *expression();
    antlr4::tree::TerminalNode *ID();

    virtual void enterRule(antlr4::tree::ParseTreeListener *listener) override;
    virtual void exitRule(antlr4::tree::ParseTreeListener *listener) override;

  };

  UpdateContext* update();

  class  DefinitionContext : public antlr4::ParserRuleContext {
  public:
    antlr4::Token *builtin = nullptr;
    DefinitionContext(antlr4::ParserRuleContext *parent, size_t invokingState);
    virtual size_t getRuleIndex() const override;
    antlr4::tree::TerminalNode *ID();
    std::vector<DeclaredParameterContext *> declaredParameter();
    DeclaredParameterContext* declaredParameter(size_t i);
    ExpressionContext *expression();

    virtual void enterRule(antlr4::tree::ParseTreeListener *listener) override;
    virtual void exitRule(antlr4::tree::ParseTreeListener *listener) override;

  };

  DefinitionContext* definition();

  class  DeclaredParameterContext : public antlr4::ParserRuleContext {
  public:
    DeclaredParameterContext(antlr4::ParserRuleContext *parent, size_t invokingState);
    virtual size_t getRuleIndex() const override;
    antlr4::tree::TerminalNode *ID();

    virtual void enterRule(antlr4::tree::ParseTreeListener *listener) override;
    virtual void exitRule(antlr4::tree::ParseTreeListener *listener) override;

  };

  DeclaredParameterContext* declaredParameter();

  class  ExpressionContext : public antlr4::ParserRuleContext {
  public:
    ExpressionContext(antlr4::ParserRuleContext *parent, size_t invokingState);
    virtual size_t getRuleIndex() const override;
    AdditionContext *addition();

    virtual void enterRule(antlr4::tree::ParseTreeListener *listener) override;
    virtual void exitRule(antlr4::tree::ParseTreeListener *listener) override;

  };

  ExpressionContext* expression();

  class  AdditionContext : public antlr4::ParserRuleContext {
  public:
    AdditionContext(antlr4::ParserRuleContext *parent, size_t invokingState);
    virtual size_t getRuleIndex() const override;
    std::vector<MultiplicationContext *> multiplication();
    MultiplicationContext* multiplication(size_t i);

    virtual void enterRule(antlr4::tree::ParseTreeListener *listener) override;
    virtual void exitRule(antlr4::tree::ParseTreeListener *listener) override;

  };

  AdditionContext* addition();

  class  MultiplicationContext : public antlr4::ParserRuleContext {
  public:
    MultiplicationContext(antlr4::ParserRuleContext *parent, size_t invokingState);
    virtual size_t getRuleIndex() const override;
    std::vector<ExponentiationContext *> exponentiation();
    ExponentiationContext* exponentiation(size_t i);

    virtual void enterRule(antlr4::tree::ParseTreeListener *listener) override;
    virtual void exitRule(antlr4::tree::ParseTreeListener *listener) override;

  };

  MultiplicationContext* multiplication();

  class  ExponentiationContext : public antlr4::ParserRuleContext {
  public:
    ExponentiationContext(antlr4::ParserRuleContext *parent, size_t invokingState);
    virtual size_t getRuleIndex() const override;
    std::vector<ModuloContext *> modulo();
    ModuloContext* modulo(size_t i);

    virtual void enterRule(antlr4::tree::ParseTreeListener *listener) override;
    virtual void exitRule(antlr4::tree::ParseTreeListener *listener) override;

  };

  ExponentiationContext* exponentiation();

  class  ModuloContext : public antlr4::ParserRuleContext {
  public:
    ModuloContext(antlr4::ParserRuleContext *parent, size_t invokingState);
    virtual size_t getRuleIndex() const override;
    std::vector<PrimaryExpressionContext *> primaryExpression();
    PrimaryExpressionContext* primaryExpression(size_t i);

    virtual void enterRule(antlr4::tree::ParseTreeListener *listener) override;
    virtual void exitRule(antlr4::tree::ParseTreeListener *listener) override;

  };

  ModuloContext* modulo();

  class  PrimaryExpressionContext : public antlr4::ParserRuleContext {
  public:
    PrimaryExpressionContext(antlr4::ParserRuleContext *parent, size_t invokingState);
    virtual size_t getRuleIndex() const override;
    std::vector<ExpressionContext *> expression();
    ExpressionContext* expression(size_t i);
    antlr4::tree::TerminalNode *FLOAT();
    antlr4::tree::TerminalNode *ID();

    virtual void enterRule(antlr4::tree::ParseTreeListener *listener) override;
    virtual void exitRule(antlr4::tree::ParseTreeListener *listener) override;

  };

  PrimaryExpressionContext* primaryExpression();


  // By default the static state used to implement the parser is lazily initialized during the first
  // call to the constructor. You can call this function if you wish to initialize the static state
  // ahead of time.
  static void initialize();

private:
};
