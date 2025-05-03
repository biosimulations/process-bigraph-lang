
// Generated from pblang.g4 by ANTLR 4.13.1


#include "pblangListener.h"

#include "pblangParser.h"


using namespace antlrcpp;

using namespace antlr4;

namespace {

struct PblangParserStaticData final {
  PblangParserStaticData(std::vector<std::string> ruleNames,
                        std::vector<std::string> literalNames,
                        std::vector<std::string> symbolicNames)
      : ruleNames(std::move(ruleNames)), literalNames(std::move(literalNames)),
        symbolicNames(std::move(symbolicNames)),
        vocabulary(this->literalNames, this->symbolicNames) {}

  PblangParserStaticData(const PblangParserStaticData&) = delete;
  PblangParserStaticData(PblangParserStaticData&&) = delete;
  PblangParserStaticData& operator=(const PblangParserStaticData&) = delete;
  PblangParserStaticData& operator=(PblangParserStaticData&&) = delete;

  std::vector<antlr4::dfa::DFA> decisionToDFA;
  antlr4::atn::PredictionContextCache sharedContextCache;
  const std::vector<std::string> ruleNames;
  const std::vector<std::string> literalNames;
  const std::vector<std::string> symbolicNames;
  const antlr4::dfa::Vocabulary vocabulary;
  antlr4::atn::SerializedATNView serializedATN;
  std::unique_ptr<antlr4::atn::ATN> atn;
};

::antlr4::internal::OnceFlag pblangParserOnceFlag;
#if ANTLR4_USE_THREAD_LOCAL_CACHE
static thread_local
#endif
PblangParserStaticData *pblangParserStaticData = nullptr;

void pblangParserInitialize() {
#if ANTLR4_USE_THREAD_LOCAL_CACHE
  if (pblangParserStaticData != nullptr) {
    return;
  }
#else
  assert(pblangParserStaticData == nullptr);
#endif
  auto staticData = std::make_unique<PblangParserStaticData>(
    std::vector<std::string>{
      "model", "type", "namedType", "defaultValue", "schemaItem", "store",
      "unit", "sbmlModel", "processDef", "process", "compositeDef", "update",
      "definition", "declaredParameter", "expression", "addition", "multiplication",
      "exponentiation", "modulo", "primaryExpression"
    },
    std::vector<std::string>{
      "", "'type'", "'builtin'", "'extends'", "'default'", "'update'", "':'",
      "'maybe'", "'['", "']'", "'store'", "'parent'", "'state'", "'unit'",
      "'sbml'", "'file'", "'param'", "'var'", "'process_def'", "'inputs'",
      "'outputs'", "'updates'", "'stores'", "'composite_def'", "'process'",
      "':='", "';'", "'def'", "'('", "','", "')'", "'+'", "'-'", "'*'",
      "'/'", "'^'", "'%'"
    },
    std::vector<std::string>{
      "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
      "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
      "", "", "", "ID", "FLOAT", "INT", "STRING", "WS", "ML_COMMENT", "SL_COMMENT"
    }
  );
  static const int32_t serializedATNSegment[] = {
  	4,1,43,308,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,6,2,
  	7,7,7,2,8,7,8,2,9,7,9,2,10,7,10,2,11,7,11,2,12,7,12,2,13,7,13,2,14,7,
  	14,2,15,7,15,2,16,7,16,2,17,7,17,2,18,7,18,2,19,7,19,1,0,1,0,1,0,1,0,
  	1,0,1,0,1,0,5,0,48,8,0,10,0,12,0,51,9,0,1,0,1,0,1,1,1,1,1,1,3,1,58,8,
  	1,1,1,1,1,3,1,62,8,1,1,1,1,1,3,1,66,8,1,1,1,1,1,3,1,70,8,1,1,1,5,1,73,
  	8,1,10,1,12,1,76,9,1,1,2,1,2,1,2,1,2,1,2,1,2,3,2,84,8,2,1,2,1,2,1,2,3,
  	2,89,8,2,1,2,1,2,1,2,3,2,94,8,2,1,3,1,3,1,4,1,4,1,4,1,4,1,4,3,4,103,8,
  	4,1,4,1,4,1,4,3,4,108,8,4,1,5,1,5,1,5,1,5,3,5,114,8,5,1,5,1,5,5,5,118,
  	8,5,10,5,12,5,121,9,5,1,6,1,6,1,6,1,6,1,6,1,6,1,6,3,6,130,8,6,1,7,1,7,
  	1,7,1,7,1,7,1,7,5,7,138,8,7,10,7,12,7,141,9,7,1,7,1,7,5,7,145,8,7,10,
  	7,12,7,148,9,7,1,8,1,8,1,8,1,8,5,8,154,8,8,10,8,12,8,157,9,8,1,8,1,8,
  	5,8,161,8,8,10,8,12,8,164,9,8,1,8,1,8,5,8,168,8,8,10,8,12,8,171,9,8,3,
  	8,173,8,8,1,8,1,8,5,8,177,8,8,10,8,12,8,180,9,8,3,8,182,8,8,1,8,1,8,5,
  	8,186,8,8,10,8,12,8,189,9,8,3,8,191,8,8,1,9,1,9,1,9,1,9,1,9,5,9,198,8,
  	9,10,9,12,9,201,9,9,3,9,203,8,9,1,10,1,10,1,10,1,10,5,10,209,8,10,10,
  	10,12,10,212,9,10,3,10,214,8,10,1,10,1,10,5,10,218,8,10,10,10,12,10,221,
  	9,10,1,11,1,11,1,11,1,11,1,11,1,12,1,12,1,12,1,12,1,12,1,12,5,12,234,
  	8,12,10,12,12,12,237,9,12,1,12,1,12,3,12,241,8,12,1,12,1,12,1,12,1,12,
  	1,12,3,12,248,8,12,1,13,1,13,1,14,1,14,1,15,1,15,1,15,5,15,257,8,15,10,
  	15,12,15,260,9,15,1,16,1,16,1,16,5,16,265,8,16,10,16,12,16,268,9,16,1,
  	17,1,17,1,17,5,17,273,8,17,10,17,12,17,276,9,17,1,18,1,18,1,18,5,18,281,
  	8,18,10,18,12,18,284,9,18,1,19,1,19,1,19,1,19,1,19,1,19,1,19,1,19,1,19,
  	1,19,5,19,296,8,19,10,19,12,19,299,9,19,1,19,1,19,3,19,303,8,19,1,19,
  	3,19,306,8,19,1,19,0,0,20,0,2,4,6,8,10,12,14,16,18,20,22,24,26,28,30,
  	32,34,36,38,0,3,1,0,38,39,1,0,31,32,1,0,33,34,334,0,49,1,0,0,0,2,54,1,
  	0,0,0,4,77,1,0,0,0,6,95,1,0,0,0,8,97,1,0,0,0,10,109,1,0,0,0,12,122,1,
  	0,0,0,14,131,1,0,0,0,16,149,1,0,0,0,18,192,1,0,0,0,20,204,1,0,0,0,22,
  	222,1,0,0,0,24,227,1,0,0,0,26,249,1,0,0,0,28,251,1,0,0,0,30,253,1,0,0,
  	0,32,261,1,0,0,0,34,269,1,0,0,0,36,277,1,0,0,0,38,305,1,0,0,0,40,48,3,
  	2,1,0,41,48,3,24,12,0,42,48,3,12,6,0,43,48,3,16,8,0,44,48,3,10,5,0,45,
  	48,3,20,10,0,46,48,3,14,7,0,47,40,1,0,0,0,47,41,1,0,0,0,47,42,1,0,0,0,
  	47,43,1,0,0,0,47,44,1,0,0,0,47,45,1,0,0,0,47,46,1,0,0,0,48,51,1,0,0,0,
  	49,47,1,0,0,0,49,50,1,0,0,0,50,52,1,0,0,0,51,49,1,0,0,0,52,53,5,0,0,1,
  	53,1,1,0,0,0,54,55,5,1,0,0,55,57,5,37,0,0,56,58,5,2,0,0,57,56,1,0,0,0,
  	57,58,1,0,0,0,58,61,1,0,0,0,59,60,5,3,0,0,60,62,5,37,0,0,61,59,1,0,0,
  	0,61,62,1,0,0,0,62,65,1,0,0,0,63,64,5,4,0,0,64,66,3,6,3,0,65,63,1,0,0,
  	0,65,66,1,0,0,0,66,69,1,0,0,0,67,68,5,5,0,0,68,70,5,37,0,0,69,67,1,0,
  	0,0,69,70,1,0,0,0,70,74,1,0,0,0,71,73,3,4,2,0,72,71,1,0,0,0,73,76,1,0,
  	0,0,74,72,1,0,0,0,74,75,1,0,0,0,75,3,1,0,0,0,76,74,1,0,0,0,77,78,5,37,
  	0,0,78,83,5,6,0,0,79,80,5,7,0,0,80,81,5,8,0,0,81,82,5,37,0,0,82,84,5,
  	9,0,0,83,79,1,0,0,0,83,84,1,0,0,0,84,85,1,0,0,0,85,88,5,37,0,0,86,87,
  	5,4,0,0,87,89,3,6,3,0,88,86,1,0,0,0,88,89,1,0,0,0,89,93,1,0,0,0,90,91,
  	5,8,0,0,91,92,5,37,0,0,92,94,5,9,0,0,93,90,1,0,0,0,93,94,1,0,0,0,94,5,
  	1,0,0,0,95,96,7,0,0,0,96,7,1,0,0,0,97,98,5,37,0,0,98,99,5,6,0,0,99,102,
  	5,37,0,0,100,101,5,4,0,0,101,103,3,6,3,0,102,100,1,0,0,0,102,103,1,0,
  	0,0,103,107,1,0,0,0,104,105,5,8,0,0,105,106,5,37,0,0,106,108,5,9,0,0,
  	107,104,1,0,0,0,107,108,1,0,0,0,108,9,1,0,0,0,109,110,5,10,0,0,110,113,
  	5,37,0,0,111,112,5,11,0,0,112,114,5,37,0,0,113,111,1,0,0,0,113,114,1,
  	0,0,0,114,119,1,0,0,0,115,116,5,12,0,0,116,118,3,8,4,0,117,115,1,0,0,
  	0,118,121,1,0,0,0,119,117,1,0,0,0,119,120,1,0,0,0,120,11,1,0,0,0,121,
  	119,1,0,0,0,122,123,5,13,0,0,123,124,5,37,0,0,124,129,5,6,0,0,125,126,
  	5,8,0,0,126,127,5,40,0,0,127,130,5,9,0,0,128,130,5,37,0,0,129,125,1,0,
  	0,0,129,128,1,0,0,0,130,13,1,0,0,0,131,132,5,14,0,0,132,133,5,37,0,0,
  	133,134,5,15,0,0,134,139,5,40,0,0,135,136,5,16,0,0,136,138,3,8,4,0,137,
  	135,1,0,0,0,138,141,1,0,0,0,139,137,1,0,0,0,139,140,1,0,0,0,140,146,1,
  	0,0,0,141,139,1,0,0,0,142,143,5,17,0,0,143,145,3,8,4,0,144,142,1,0,0,
  	0,145,148,1,0,0,0,146,144,1,0,0,0,146,147,1,0,0,0,147,15,1,0,0,0,148,
  	146,1,0,0,0,149,150,5,18,0,0,150,155,5,37,0,0,151,152,5,16,0,0,152,154,
  	3,8,4,0,153,151,1,0,0,0,154,157,1,0,0,0,155,153,1,0,0,0,155,156,1,0,0,
  	0,156,162,1,0,0,0,157,155,1,0,0,0,158,159,5,17,0,0,159,161,3,8,4,0,160,
  	158,1,0,0,0,161,164,1,0,0,0,162,160,1,0,0,0,162,163,1,0,0,0,163,172,1,
  	0,0,0,164,162,1,0,0,0,165,169,5,19,0,0,166,168,5,37,0,0,167,166,1,0,0,
  	0,168,171,1,0,0,0,169,167,1,0,0,0,169,170,1,0,0,0,170,173,1,0,0,0,171,
  	169,1,0,0,0,172,165,1,0,0,0,172,173,1,0,0,0,173,181,1,0,0,0,174,178,5,
  	20,0,0,175,177,5,37,0,0,176,175,1,0,0,0,177,180,1,0,0,0,178,176,1,0,0,
  	0,178,179,1,0,0,0,179,182,1,0,0,0,180,178,1,0,0,0,181,174,1,0,0,0,181,
  	182,1,0,0,0,182,190,1,0,0,0,183,187,5,21,0,0,184,186,3,22,11,0,185,184,
  	1,0,0,0,186,189,1,0,0,0,187,185,1,0,0,0,187,188,1,0,0,0,188,191,1,0,0,
  	0,189,187,1,0,0,0,190,183,1,0,0,0,190,191,1,0,0,0,191,17,1,0,0,0,192,
  	193,5,37,0,0,193,194,5,6,0,0,194,202,5,37,0,0,195,199,5,22,0,0,196,198,
  	5,37,0,0,197,196,1,0,0,0,198,201,1,0,0,0,199,197,1,0,0,0,199,200,1,0,
  	0,0,200,203,1,0,0,0,201,199,1,0,0,0,202,195,1,0,0,0,202,203,1,0,0,0,203,
  	19,1,0,0,0,204,205,5,23,0,0,205,213,5,37,0,0,206,210,5,22,0,0,207,209,
  	5,37,0,0,208,207,1,0,0,0,209,212,1,0,0,0,210,208,1,0,0,0,210,211,1,0,
  	0,0,211,214,1,0,0,0,212,210,1,0,0,0,213,206,1,0,0,0,213,214,1,0,0,0,214,
  	219,1,0,0,0,215,216,5,24,0,0,216,218,3,18,9,0,217,215,1,0,0,0,218,221,
  	1,0,0,0,219,217,1,0,0,0,219,220,1,0,0,0,220,21,1,0,0,0,221,219,1,0,0,
  	0,222,223,5,37,0,0,223,224,5,25,0,0,224,225,3,28,14,0,225,226,5,26,0,
  	0,226,23,1,0,0,0,227,228,5,27,0,0,228,240,5,37,0,0,229,230,5,28,0,0,230,
  	235,3,26,13,0,231,232,5,29,0,0,232,234,3,26,13,0,233,231,1,0,0,0,234,
  	237,1,0,0,0,235,233,1,0,0,0,235,236,1,0,0,0,236,238,1,0,0,0,237,235,1,
  	0,0,0,238,239,5,30,0,0,239,241,1,0,0,0,240,229,1,0,0,0,240,241,1,0,0,
  	0,241,242,1,0,0,0,242,247,5,6,0,0,243,248,5,2,0,0,244,245,3,28,14,0,245,
  	246,5,26,0,0,246,248,1,0,0,0,247,243,1,0,0,0,247,244,1,0,0,0,248,25,1,
  	0,0,0,249,250,5,37,0,0,250,27,1,0,0,0,251,252,3,30,15,0,252,29,1,0,0,
  	0,253,258,3,32,16,0,254,255,7,1,0,0,255,257,3,32,16,0,256,254,1,0,0,0,
  	257,260,1,0,0,0,258,256,1,0,0,0,258,259,1,0,0,0,259,31,1,0,0,0,260,258,
  	1,0,0,0,261,266,3,34,17,0,262,263,7,2,0,0,263,265,3,34,17,0,264,262,1,
  	0,0,0,265,268,1,0,0,0,266,264,1,0,0,0,266,267,1,0,0,0,267,33,1,0,0,0,
  	268,266,1,0,0,0,269,274,3,36,18,0,270,271,5,35,0,0,271,273,3,36,18,0,
  	272,270,1,0,0,0,273,276,1,0,0,0,274,272,1,0,0,0,274,275,1,0,0,0,275,35,
  	1,0,0,0,276,274,1,0,0,0,277,282,3,38,19,0,278,279,5,36,0,0,279,281,3,
  	38,19,0,280,278,1,0,0,0,281,284,1,0,0,0,282,280,1,0,0,0,282,283,1,0,0,
  	0,283,37,1,0,0,0,284,282,1,0,0,0,285,286,5,28,0,0,286,287,3,28,14,0,287,
  	288,5,30,0,0,288,306,1,0,0,0,289,306,5,38,0,0,290,302,5,37,0,0,291,292,
  	5,28,0,0,292,297,3,28,14,0,293,294,5,29,0,0,294,296,3,28,14,0,295,293,
  	1,0,0,0,296,299,1,0,0,0,297,295,1,0,0,0,297,298,1,0,0,0,298,300,1,0,0,
  	0,299,297,1,0,0,0,300,301,5,30,0,0,301,303,1,0,0,0,302,291,1,0,0,0,302,
  	303,1,0,0,0,303,306,1,0,0,0,304,306,5,37,0,0,305,285,1,0,0,0,305,289,
  	1,0,0,0,305,290,1,0,0,0,305,304,1,0,0,0,306,39,1,0,0,0,40,47,49,57,61,
  	65,69,74,83,88,93,102,107,113,119,129,139,146,155,162,169,172,178,181,
  	187,190,199,202,210,213,219,235,240,247,258,266,274,282,297,302,305
  };
  staticData->serializedATN = antlr4::atn::SerializedATNView(serializedATNSegment, sizeof(serializedATNSegment) / sizeof(serializedATNSegment[0]));

  antlr4::atn::ATNDeserializer deserializer;
  staticData->atn = deserializer.deserialize(staticData->serializedATN);

  const size_t count = staticData->atn->getNumberOfDecisions();
  staticData->decisionToDFA.reserve(count);
  for (size_t i = 0; i < count; i++) {
    staticData->decisionToDFA.emplace_back(staticData->atn->getDecisionState(i), i);
  }
  pblangParserStaticData = staticData.release();
}

}

pblangParser::pblangParser(TokenStream *input) : pblangParser(input, antlr4::atn::ParserATNSimulatorOptions()) {}

pblangParser::pblangParser(TokenStream *input, const antlr4::atn::ParserATNSimulatorOptions &options) : Parser(input) {
  pblangParser::initialize();
  _interpreter = new atn::ParserATNSimulator(this, *pblangParserStaticData->atn, pblangParserStaticData->decisionToDFA, pblangParserStaticData->sharedContextCache, options);
}

pblangParser::~pblangParser() {
  delete _interpreter;
}

const atn::ATN& pblangParser::getATN() const {
  return *pblangParserStaticData->atn;
}

std::string pblangParser::getGrammarFileName() const {
  return "pblang.g4";
}

const std::vector<std::string>& pblangParser::getRuleNames() const {
  return pblangParserStaticData->ruleNames;
}

const dfa::Vocabulary& pblangParser::getVocabulary() const {
  return pblangParserStaticData->vocabulary;
}

antlr4::atn::SerializedATNView pblangParser::getSerializedATN() const {
  return pblangParserStaticData->serializedATN;
}


//----------------- ModelContext ------------------------------------------------------------------

pblangParser::ModelContext::ModelContext(ParserRuleContext *parent, size_t invokingState)
  : ParserRuleContext(parent, invokingState) {
}

tree::TerminalNode* pblangParser::ModelContext::EOF() {
  return getToken(pblangParser::EOF, 0);
}

std::vector<pblangParser::TypeContext *> pblangParser::ModelContext::type() {
  return getRuleContexts<pblangParser::TypeContext>();
}

pblangParser::TypeContext* pblangParser::ModelContext::type(size_t i) {
  return getRuleContext<pblangParser::TypeContext>(i);
}

std::vector<pblangParser::DefinitionContext *> pblangParser::ModelContext::definition() {
  return getRuleContexts<pblangParser::DefinitionContext>();
}

pblangParser::DefinitionContext* pblangParser::ModelContext::definition(size_t i) {
  return getRuleContext<pblangParser::DefinitionContext>(i);
}

std::vector<pblangParser::UnitContext *> pblangParser::ModelContext::unit() {
  return getRuleContexts<pblangParser::UnitContext>();
}

pblangParser::UnitContext* pblangParser::ModelContext::unit(size_t i) {
  return getRuleContext<pblangParser::UnitContext>(i);
}

std::vector<pblangParser::ProcessDefContext *> pblangParser::ModelContext::processDef() {
  return getRuleContexts<pblangParser::ProcessDefContext>();
}

pblangParser::ProcessDefContext* pblangParser::ModelContext::processDef(size_t i) {
  return getRuleContext<pblangParser::ProcessDefContext>(i);
}

std::vector<pblangParser::StoreContext *> pblangParser::ModelContext::store() {
  return getRuleContexts<pblangParser::StoreContext>();
}

pblangParser::StoreContext* pblangParser::ModelContext::store(size_t i) {
  return getRuleContext<pblangParser::StoreContext>(i);
}

std::vector<pblangParser::CompositeDefContext *> pblangParser::ModelContext::compositeDef() {
  return getRuleContexts<pblangParser::CompositeDefContext>();
}

pblangParser::CompositeDefContext* pblangParser::ModelContext::compositeDef(size_t i) {
  return getRuleContext<pblangParser::CompositeDefContext>(i);
}

std::vector<pblangParser::SbmlModelContext *> pblangParser::ModelContext::sbmlModel() {
  return getRuleContexts<pblangParser::SbmlModelContext>();
}

pblangParser::SbmlModelContext* pblangParser::ModelContext::sbmlModel(size_t i) {
  return getRuleContext<pblangParser::SbmlModelContext>(i);
}


size_t pblangParser::ModelContext::getRuleIndex() const {
  return pblangParser::RuleModel;
}

void pblangParser::ModelContext::enterRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<pblangListener *>(listener);
  if (parserListener != nullptr)
    parserListener->enterModel(this);
}

void pblangParser::ModelContext::exitRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<pblangListener *>(listener);
  if (parserListener != nullptr)
    parserListener->exitModel(this);
}

pblangParser::ModelContext* pblangParser::model() {
  ModelContext *_localctx = _tracker.createInstance<ModelContext>(_ctx, getState());
  enterRule(_localctx, 0, pblangParser::RuleModel);
  size_t _la = 0;

#if __cplusplus > 201703L
  auto onExit = finally([=, this] {
#else
  auto onExit = finally([=] {
#endif
    exitRule();
  });
  try {
    enterOuterAlt(_localctx, 1);
    setState(49);
    _errHandler->sync(this);
    _la = _input->LA(1);
    while ((((_la & ~ 0x3fULL) == 0) &&
      ((1ULL << _la) & 142894082) != 0)) {
      setState(47);
      _errHandler->sync(this);
      switch (_input->LA(1)) {
        case pblangParser::T__0: {
          setState(40);
          type();
          break;
        }

        case pblangParser::T__26: {
          setState(41);
          definition();
          break;
        }

        case pblangParser::T__12: {
          setState(42);
          unit();
          break;
        }

        case pblangParser::T__17: {
          setState(43);
          processDef();
          break;
        }

        case pblangParser::T__9: {
          setState(44);
          store();
          break;
        }

        case pblangParser::T__22: {
          setState(45);
          compositeDef();
          break;
        }

        case pblangParser::T__13: {
          setState(46);
          sbmlModel();
          break;
        }

      default:
        throw NoViableAltException(this);
      }
      setState(51);
      _errHandler->sync(this);
      _la = _input->LA(1);
    }
    setState(52);
    match(pblangParser::EOF);

  }
  catch (RecognitionException &e) {
    _errHandler->reportError(this, e);
    _localctx->exception = std::current_exception();
    _errHandler->recover(this, _localctx->exception);
  }

  return _localctx;
}

//----------------- TypeContext ------------------------------------------------------------------

pblangParser::TypeContext::TypeContext(ParserRuleContext *parent, size_t invokingState)
  : ParserRuleContext(parent, invokingState) {
}

std::vector<tree::TerminalNode *> pblangParser::TypeContext::ID() {
  return getTokens(pblangParser::ID);
}

tree::TerminalNode* pblangParser::TypeContext::ID(size_t i) {
  return getToken(pblangParser::ID, i);
}

pblangParser::DefaultValueContext* pblangParser::TypeContext::defaultValue() {
  return getRuleContext<pblangParser::DefaultValueContext>(0);
}

std::vector<pblangParser::NamedTypeContext *> pblangParser::TypeContext::namedType() {
  return getRuleContexts<pblangParser::NamedTypeContext>();
}

pblangParser::NamedTypeContext* pblangParser::TypeContext::namedType(size_t i) {
  return getRuleContext<pblangParser::NamedTypeContext>(i);
}


size_t pblangParser::TypeContext::getRuleIndex() const {
  return pblangParser::RuleType;
}

void pblangParser::TypeContext::enterRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<pblangListener *>(listener);
  if (parserListener != nullptr)
    parserListener->enterType(this);
}

void pblangParser::TypeContext::exitRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<pblangListener *>(listener);
  if (parserListener != nullptr)
    parserListener->exitType(this);
}

pblangParser::TypeContext* pblangParser::type() {
  TypeContext *_localctx = _tracker.createInstance<TypeContext>(_ctx, getState());
  enterRule(_localctx, 2, pblangParser::RuleType);
  size_t _la = 0;

#if __cplusplus > 201703L
  auto onExit = finally([=, this] {
#else
  auto onExit = finally([=] {
#endif
    exitRule();
  });
  try {
    enterOuterAlt(_localctx, 1);
    setState(54);
    match(pblangParser::T__0);
    setState(55);
    match(pblangParser::ID);
    setState(57);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__1) {
      setState(56);
      antlrcpp::downCast<TypeContext *>(_localctx)->builtin = match(pblangParser::T__1);
    }
    setState(61);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__2) {
      setState(59);
      match(pblangParser::T__2);
      setState(60);
      match(pblangParser::ID);
    }
    setState(65);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__3) {
      setState(63);
      match(pblangParser::T__3);
      setState(64);
      defaultValue();
    }
    setState(69);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__4) {
      setState(67);
      match(pblangParser::T__4);
      setState(68);
      match(pblangParser::ID);
    }
    setState(74);
    _errHandler->sync(this);
    _la = _input->LA(1);
    while (_la == pblangParser::ID) {
      setState(71);
      namedType();
      setState(76);
      _errHandler->sync(this);
      _la = _input->LA(1);
    }

  }
  catch (RecognitionException &e) {
    _errHandler->reportError(this, e);
    _localctx->exception = std::current_exception();
    _errHandler->recover(this, _localctx->exception);
  }

  return _localctx;
}

//----------------- NamedTypeContext ------------------------------------------------------------------

pblangParser::NamedTypeContext::NamedTypeContext(ParserRuleContext *parent, size_t invokingState)
  : ParserRuleContext(parent, invokingState) {
}

std::vector<tree::TerminalNode *> pblangParser::NamedTypeContext::ID() {
  return getTokens(pblangParser::ID);
}

tree::TerminalNode* pblangParser::NamedTypeContext::ID(size_t i) {
  return getToken(pblangParser::ID, i);
}

pblangParser::DefaultValueContext* pblangParser::NamedTypeContext::defaultValue() {
  return getRuleContext<pblangParser::DefaultValueContext>(0);
}


size_t pblangParser::NamedTypeContext::getRuleIndex() const {
  return pblangParser::RuleNamedType;
}

void pblangParser::NamedTypeContext::enterRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<pblangListener *>(listener);
  if (parserListener != nullptr)
    parserListener->enterNamedType(this);
}

void pblangParser::NamedTypeContext::exitRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<pblangListener *>(listener);
  if (parserListener != nullptr)
    parserListener->exitNamedType(this);
}

pblangParser::NamedTypeContext* pblangParser::namedType() {
  NamedTypeContext *_localctx = _tracker.createInstance<NamedTypeContext>(_ctx, getState());
  enterRule(_localctx, 4, pblangParser::RuleNamedType);
  size_t _la = 0;

#if __cplusplus > 201703L
  auto onExit = finally([=, this] {
#else
  auto onExit = finally([=] {
#endif
    exitRule();
  });
  try {
    enterOuterAlt(_localctx, 1);
    setState(77);
    match(pblangParser::ID);
    setState(78);
    match(pblangParser::T__5);
    setState(83);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__6) {
      setState(79);
      match(pblangParser::T__6);
      setState(80);
      match(pblangParser::T__7);
      setState(81);
      match(pblangParser::ID);
      setState(82);
      match(pblangParser::T__8);
    }
    setState(85);
    match(pblangParser::ID);
    setState(88);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__3) {
      setState(86);
      match(pblangParser::T__3);
      setState(87);
      defaultValue();
    }
    setState(93);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__7) {
      setState(90);
      match(pblangParser::T__7);
      setState(91);
      match(pblangParser::ID);
      setState(92);
      match(pblangParser::T__8);
    }

  }
  catch (RecognitionException &e) {
    _errHandler->reportError(this, e);
    _localctx->exception = std::current_exception();
    _errHandler->recover(this, _localctx->exception);
  }

  return _localctx;
}

//----------------- DefaultValueContext ------------------------------------------------------------------

pblangParser::DefaultValueContext::DefaultValueContext(ParserRuleContext *parent, size_t invokingState)
  : ParserRuleContext(parent, invokingState) {
}

tree::TerminalNode* pblangParser::DefaultValueContext::INT() {
  return getToken(pblangParser::INT, 0);
}

tree::TerminalNode* pblangParser::DefaultValueContext::FLOAT() {
  return getToken(pblangParser::FLOAT, 0);
}


size_t pblangParser::DefaultValueContext::getRuleIndex() const {
  return pblangParser::RuleDefaultValue;
}

void pblangParser::DefaultValueContext::enterRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<pblangListener *>(listener);
  if (parserListener != nullptr)
    parserListener->enterDefaultValue(this);
}

void pblangParser::DefaultValueContext::exitRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<pblangListener *>(listener);
  if (parserListener != nullptr)
    parserListener->exitDefaultValue(this);
}

pblangParser::DefaultValueContext* pblangParser::defaultValue() {
  DefaultValueContext *_localctx = _tracker.createInstance<DefaultValueContext>(_ctx, getState());
  enterRule(_localctx, 6, pblangParser::RuleDefaultValue);
  size_t _la = 0;

#if __cplusplus > 201703L
  auto onExit = finally([=, this] {
#else
  auto onExit = finally([=] {
#endif
    exitRule();
  });
  try {
    enterOuterAlt(_localctx, 1);
    setState(95);
    _la = _input->LA(1);
    if (!(_la == pblangParser::FLOAT

    || _la == pblangParser::INT)) {
    _errHandler->recoverInline(this);
    }
    else {
      _errHandler->reportMatch(this);
      consume();
    }

  }
  catch (RecognitionException &e) {
    _errHandler->reportError(this, e);
    _localctx->exception = std::current_exception();
    _errHandler->recover(this, _localctx->exception);
  }

  return _localctx;
}

//----------------- SchemaItemContext ------------------------------------------------------------------

pblangParser::SchemaItemContext::SchemaItemContext(ParserRuleContext *parent, size_t invokingState)
  : ParserRuleContext(parent, invokingState) {
}

std::vector<tree::TerminalNode *> pblangParser::SchemaItemContext::ID() {
  return getTokens(pblangParser::ID);
}

tree::TerminalNode* pblangParser::SchemaItemContext::ID(size_t i) {
  return getToken(pblangParser::ID, i);
}

pblangParser::DefaultValueContext* pblangParser::SchemaItemContext::defaultValue() {
  return getRuleContext<pblangParser::DefaultValueContext>(0);
}


size_t pblangParser::SchemaItemContext::getRuleIndex() const {
  return pblangParser::RuleSchemaItem;
}

void pblangParser::SchemaItemContext::enterRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<pblangListener *>(listener);
  if (parserListener != nullptr)
    parserListener->enterSchemaItem(this);
}

void pblangParser::SchemaItemContext::exitRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<pblangListener *>(listener);
  if (parserListener != nullptr)
    parserListener->exitSchemaItem(this);
}

pblangParser::SchemaItemContext* pblangParser::schemaItem() {
  SchemaItemContext *_localctx = _tracker.createInstance<SchemaItemContext>(_ctx, getState());
  enterRule(_localctx, 8, pblangParser::RuleSchemaItem);
  size_t _la = 0;

#if __cplusplus > 201703L
  auto onExit = finally([=, this] {
#else
  auto onExit = finally([=] {
#endif
    exitRule();
  });
  try {
    enterOuterAlt(_localctx, 1);
    setState(97);
    match(pblangParser::ID);
    setState(98);
    match(pblangParser::T__5);
    setState(99);
    match(pblangParser::ID);
    setState(102);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__3) {
      setState(100);
      match(pblangParser::T__3);
      setState(101);
      defaultValue();
    }
    setState(107);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__7) {
      setState(104);
      match(pblangParser::T__7);
      setState(105);
      match(pblangParser::ID);
      setState(106);
      match(pblangParser::T__8);
    }

  }
  catch (RecognitionException &e) {
    _errHandler->reportError(this, e);
    _localctx->exception = std::current_exception();
    _errHandler->recover(this, _localctx->exception);
  }

  return _localctx;
}

//----------------- StoreContext ------------------------------------------------------------------

pblangParser::StoreContext::StoreContext(ParserRuleContext *parent, size_t invokingState)
  : ParserRuleContext(parent, invokingState) {
}

std::vector<tree::TerminalNode *> pblangParser::StoreContext::ID() {
  return getTokens(pblangParser::ID);
}

tree::TerminalNode* pblangParser::StoreContext::ID(size_t i) {
  return getToken(pblangParser::ID, i);
}

std::vector<pblangParser::SchemaItemContext *> pblangParser::StoreContext::schemaItem() {
  return getRuleContexts<pblangParser::SchemaItemContext>();
}

pblangParser::SchemaItemContext* pblangParser::StoreContext::schemaItem(size_t i) {
  return getRuleContext<pblangParser::SchemaItemContext>(i);
}


size_t pblangParser::StoreContext::getRuleIndex() const {
  return pblangParser::RuleStore;
}

void pblangParser::StoreContext::enterRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<pblangListener *>(listener);
  if (parserListener != nullptr)
    parserListener->enterStore(this);
}

void pblangParser::StoreContext::exitRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<pblangListener *>(listener);
  if (parserListener != nullptr)
    parserListener->exitStore(this);
}

pblangParser::StoreContext* pblangParser::store() {
  StoreContext *_localctx = _tracker.createInstance<StoreContext>(_ctx, getState());
  enterRule(_localctx, 10, pblangParser::RuleStore);
  size_t _la = 0;

#if __cplusplus > 201703L
  auto onExit = finally([=, this] {
#else
  auto onExit = finally([=] {
#endif
    exitRule();
  });
  try {
    enterOuterAlt(_localctx, 1);
    setState(109);
    match(pblangParser::T__9);
    setState(110);
    match(pblangParser::ID);
    setState(113);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__10) {
      setState(111);
      match(pblangParser::T__10);
      setState(112);
      match(pblangParser::ID);
    }
    setState(119);
    _errHandler->sync(this);
    _la = _input->LA(1);
    while (_la == pblangParser::T__11) {
      setState(115);
      match(pblangParser::T__11);
      setState(116);
      schemaItem();
      setState(121);
      _errHandler->sync(this);
      _la = _input->LA(1);
    }

  }
  catch (RecognitionException &e) {
    _errHandler->reportError(this, e);
    _localctx->exception = std::current_exception();
    _errHandler->recover(this, _localctx->exception);
  }

  return _localctx;
}

//----------------- UnitContext ------------------------------------------------------------------

pblangParser::UnitContext::UnitContext(ParserRuleContext *parent, size_t invokingState)
  : ParserRuleContext(parent, invokingState) {
}

std::vector<tree::TerminalNode *> pblangParser::UnitContext::ID() {
  return getTokens(pblangParser::ID);
}

tree::TerminalNode* pblangParser::UnitContext::ID(size_t i) {
  return getToken(pblangParser::ID, i);
}

tree::TerminalNode* pblangParser::UnitContext::STRING() {
  return getToken(pblangParser::STRING, 0);
}


size_t pblangParser::UnitContext::getRuleIndex() const {
  return pblangParser::RuleUnit;
}

void pblangParser::UnitContext::enterRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<pblangListener *>(listener);
  if (parserListener != nullptr)
    parserListener->enterUnit(this);
}

void pblangParser::UnitContext::exitRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<pblangListener *>(listener);
  if (parserListener != nullptr)
    parserListener->exitUnit(this);
}

pblangParser::UnitContext* pblangParser::unit() {
  UnitContext *_localctx = _tracker.createInstance<UnitContext>(_ctx, getState());
  enterRule(_localctx, 12, pblangParser::RuleUnit);

#if __cplusplus > 201703L
  auto onExit = finally([=, this] {
#else
  auto onExit = finally([=] {
#endif
    exitRule();
  });
  try {
    enterOuterAlt(_localctx, 1);
    setState(122);
    match(pblangParser::T__12);
    setState(123);
    match(pblangParser::ID);
    setState(124);
    match(pblangParser::T__5);
    setState(129);
    _errHandler->sync(this);
    switch (_input->LA(1)) {
      case pblangParser::T__7: {
        setState(125);
        match(pblangParser::T__7);
        setState(126);
        match(pblangParser::STRING);
        setState(127);
        match(pblangParser::T__8);
        break;
      }

      case pblangParser::ID: {
        setState(128);
        match(pblangParser::ID);
        break;
      }

    default:
      throw NoViableAltException(this);
    }

  }
  catch (RecognitionException &e) {
    _errHandler->reportError(this, e);
    _localctx->exception = std::current_exception();
    _errHandler->recover(this, _localctx->exception);
  }

  return _localctx;
}

//----------------- SbmlModelContext ------------------------------------------------------------------

pblangParser::SbmlModelContext::SbmlModelContext(ParserRuleContext *parent, size_t invokingState)
  : ParserRuleContext(parent, invokingState) {
}

tree::TerminalNode* pblangParser::SbmlModelContext::ID() {
  return getToken(pblangParser::ID, 0);
}

tree::TerminalNode* pblangParser::SbmlModelContext::STRING() {
  return getToken(pblangParser::STRING, 0);
}

std::vector<pblangParser::SchemaItemContext *> pblangParser::SbmlModelContext::schemaItem() {
  return getRuleContexts<pblangParser::SchemaItemContext>();
}

pblangParser::SchemaItemContext* pblangParser::SbmlModelContext::schemaItem(size_t i) {
  return getRuleContext<pblangParser::SchemaItemContext>(i);
}


size_t pblangParser::SbmlModelContext::getRuleIndex() const {
  return pblangParser::RuleSbmlModel;
}

void pblangParser::SbmlModelContext::enterRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<pblangListener *>(listener);
  if (parserListener != nullptr)
    parserListener->enterSbmlModel(this);
}

void pblangParser::SbmlModelContext::exitRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<pblangListener *>(listener);
  if (parserListener != nullptr)
    parserListener->exitSbmlModel(this);
}

pblangParser::SbmlModelContext* pblangParser::sbmlModel() {
  SbmlModelContext *_localctx = _tracker.createInstance<SbmlModelContext>(_ctx, getState());
  enterRule(_localctx, 14, pblangParser::RuleSbmlModel);
  size_t _la = 0;

#if __cplusplus > 201703L
  auto onExit = finally([=, this] {
#else
  auto onExit = finally([=] {
#endif
    exitRule();
  });
  try {
    enterOuterAlt(_localctx, 1);
    setState(131);
    match(pblangParser::T__13);
    setState(132);
    match(pblangParser::ID);
    setState(133);
    match(pblangParser::T__14);
    setState(134);
    match(pblangParser::STRING);
    setState(139);
    _errHandler->sync(this);
    _la = _input->LA(1);
    while (_la == pblangParser::T__15) {
      setState(135);
      match(pblangParser::T__15);
      setState(136);
      schemaItem();
      setState(141);
      _errHandler->sync(this);
      _la = _input->LA(1);
    }
    setState(146);
    _errHandler->sync(this);
    _la = _input->LA(1);
    while (_la == pblangParser::T__16) {
      setState(142);
      match(pblangParser::T__16);
      setState(143);
      schemaItem();
      setState(148);
      _errHandler->sync(this);
      _la = _input->LA(1);
    }

  }
  catch (RecognitionException &e) {
    _errHandler->reportError(this, e);
    _localctx->exception = std::current_exception();
    _errHandler->recover(this, _localctx->exception);
  }

  return _localctx;
}

//----------------- ProcessDefContext ------------------------------------------------------------------

pblangParser::ProcessDefContext::ProcessDefContext(ParserRuleContext *parent, size_t invokingState)
  : ParserRuleContext(parent, invokingState) {
}

std::vector<tree::TerminalNode *> pblangParser::ProcessDefContext::ID() {
  return getTokens(pblangParser::ID);
}

tree::TerminalNode* pblangParser::ProcessDefContext::ID(size_t i) {
  return getToken(pblangParser::ID, i);
}

std::vector<pblangParser::SchemaItemContext *> pblangParser::ProcessDefContext::schemaItem() {
  return getRuleContexts<pblangParser::SchemaItemContext>();
}

pblangParser::SchemaItemContext* pblangParser::ProcessDefContext::schemaItem(size_t i) {
  return getRuleContext<pblangParser::SchemaItemContext>(i);
}

std::vector<pblangParser::UpdateContext *> pblangParser::ProcessDefContext::update() {
  return getRuleContexts<pblangParser::UpdateContext>();
}

pblangParser::UpdateContext* pblangParser::ProcessDefContext::update(size_t i) {
  return getRuleContext<pblangParser::UpdateContext>(i);
}


size_t pblangParser::ProcessDefContext::getRuleIndex() const {
  return pblangParser::RuleProcessDef;
}

void pblangParser::ProcessDefContext::enterRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<pblangListener *>(listener);
  if (parserListener != nullptr)
    parserListener->enterProcessDef(this);
}

void pblangParser::ProcessDefContext::exitRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<pblangListener *>(listener);
  if (parserListener != nullptr)
    parserListener->exitProcessDef(this);
}

pblangParser::ProcessDefContext* pblangParser::processDef() {
  ProcessDefContext *_localctx = _tracker.createInstance<ProcessDefContext>(_ctx, getState());
  enterRule(_localctx, 16, pblangParser::RuleProcessDef);
  size_t _la = 0;

#if __cplusplus > 201703L
  auto onExit = finally([=, this] {
#else
  auto onExit = finally([=] {
#endif
    exitRule();
  });
  try {
    enterOuterAlt(_localctx, 1);
    setState(149);
    match(pblangParser::T__17);
    setState(150);
    match(pblangParser::ID);
    setState(155);
    _errHandler->sync(this);
    _la = _input->LA(1);
    while (_la == pblangParser::T__15) {
      setState(151);
      match(pblangParser::T__15);
      setState(152);
      schemaItem();
      setState(157);
      _errHandler->sync(this);
      _la = _input->LA(1);
    }
    setState(162);
    _errHandler->sync(this);
    _la = _input->LA(1);
    while (_la == pblangParser::T__16) {
      setState(158);
      match(pblangParser::T__16);
      setState(159);
      schemaItem();
      setState(164);
      _errHandler->sync(this);
      _la = _input->LA(1);
    }
    setState(172);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__18) {
      setState(165);
      match(pblangParser::T__18);
      setState(169);
      _errHandler->sync(this);
      _la = _input->LA(1);
      while (_la == pblangParser::ID) {
        setState(166);
        match(pblangParser::ID);
        setState(171);
        _errHandler->sync(this);
        _la = _input->LA(1);
      }
    }
    setState(181);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__19) {
      setState(174);
      match(pblangParser::T__19);
      setState(178);
      _errHandler->sync(this);
      _la = _input->LA(1);
      while (_la == pblangParser::ID) {
        setState(175);
        match(pblangParser::ID);
        setState(180);
        _errHandler->sync(this);
        _la = _input->LA(1);
      }
    }
    setState(190);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__20) {
      setState(183);
      match(pblangParser::T__20);
      setState(187);
      _errHandler->sync(this);
      _la = _input->LA(1);
      while (_la == pblangParser::ID) {
        setState(184);
        update();
        setState(189);
        _errHandler->sync(this);
        _la = _input->LA(1);
      }
    }

  }
  catch (RecognitionException &e) {
    _errHandler->reportError(this, e);
    _localctx->exception = std::current_exception();
    _errHandler->recover(this, _localctx->exception);
  }

  return _localctx;
}

//----------------- ProcessContext ------------------------------------------------------------------

pblangParser::ProcessContext::ProcessContext(ParserRuleContext *parent, size_t invokingState)
  : ParserRuleContext(parent, invokingState) {
}

std::vector<tree::TerminalNode *> pblangParser::ProcessContext::ID() {
  return getTokens(pblangParser::ID);
}

tree::TerminalNode* pblangParser::ProcessContext::ID(size_t i) {
  return getToken(pblangParser::ID, i);
}


size_t pblangParser::ProcessContext::getRuleIndex() const {
  return pblangParser::RuleProcess;
}

void pblangParser::ProcessContext::enterRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<pblangListener *>(listener);
  if (parserListener != nullptr)
    parserListener->enterProcess(this);
}

void pblangParser::ProcessContext::exitRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<pblangListener *>(listener);
  if (parserListener != nullptr)
    parserListener->exitProcess(this);
}

pblangParser::ProcessContext* pblangParser::process() {
  ProcessContext *_localctx = _tracker.createInstance<ProcessContext>(_ctx, getState());
  enterRule(_localctx, 18, pblangParser::RuleProcess);
  size_t _la = 0;

#if __cplusplus > 201703L
  auto onExit = finally([=, this] {
#else
  auto onExit = finally([=] {
#endif
    exitRule();
  });
  try {
    enterOuterAlt(_localctx, 1);
    setState(192);
    match(pblangParser::ID);
    setState(193);
    match(pblangParser::T__5);
    setState(194);
    match(pblangParser::ID);
    setState(202);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__21) {
      setState(195);
      match(pblangParser::T__21);
      setState(199);
      _errHandler->sync(this);
      _la = _input->LA(1);
      while (_la == pblangParser::ID) {
        setState(196);
        match(pblangParser::ID);
        setState(201);
        _errHandler->sync(this);
        _la = _input->LA(1);
      }
    }

  }
  catch (RecognitionException &e) {
    _errHandler->reportError(this, e);
    _localctx->exception = std::current_exception();
    _errHandler->recover(this, _localctx->exception);
  }

  return _localctx;
}

//----------------- CompositeDefContext ------------------------------------------------------------------

pblangParser::CompositeDefContext::CompositeDefContext(ParserRuleContext *parent, size_t invokingState)
  : ParserRuleContext(parent, invokingState) {
}

std::vector<tree::TerminalNode *> pblangParser::CompositeDefContext::ID() {
  return getTokens(pblangParser::ID);
}

tree::TerminalNode* pblangParser::CompositeDefContext::ID(size_t i) {
  return getToken(pblangParser::ID, i);
}

std::vector<pblangParser::ProcessContext *> pblangParser::CompositeDefContext::process() {
  return getRuleContexts<pblangParser::ProcessContext>();
}

pblangParser::ProcessContext* pblangParser::CompositeDefContext::process(size_t i) {
  return getRuleContext<pblangParser::ProcessContext>(i);
}


size_t pblangParser::CompositeDefContext::getRuleIndex() const {
  return pblangParser::RuleCompositeDef;
}

void pblangParser::CompositeDefContext::enterRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<pblangListener *>(listener);
  if (parserListener != nullptr)
    parserListener->enterCompositeDef(this);
}

void pblangParser::CompositeDefContext::exitRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<pblangListener *>(listener);
  if (parserListener != nullptr)
    parserListener->exitCompositeDef(this);
}

pblangParser::CompositeDefContext* pblangParser::compositeDef() {
  CompositeDefContext *_localctx = _tracker.createInstance<CompositeDefContext>(_ctx, getState());
  enterRule(_localctx, 20, pblangParser::RuleCompositeDef);
  size_t _la = 0;

#if __cplusplus > 201703L
  auto onExit = finally([=, this] {
#else
  auto onExit = finally([=] {
#endif
    exitRule();
  });
  try {
    enterOuterAlt(_localctx, 1);
    setState(204);
    match(pblangParser::T__22);
    setState(205);
    match(pblangParser::ID);
    setState(213);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__21) {
      setState(206);
      match(pblangParser::T__21);
      setState(210);
      _errHandler->sync(this);
      _la = _input->LA(1);
      while (_la == pblangParser::ID) {
        setState(207);
        match(pblangParser::ID);
        setState(212);
        _errHandler->sync(this);
        _la = _input->LA(1);
      }
    }
    setState(219);
    _errHandler->sync(this);
    _la = _input->LA(1);
    while (_la == pblangParser::T__23) {
      setState(215);
      match(pblangParser::T__23);
      setState(216);
      process();
      setState(221);
      _errHandler->sync(this);
      _la = _input->LA(1);
    }

  }
  catch (RecognitionException &e) {
    _errHandler->reportError(this, e);
    _localctx->exception = std::current_exception();
    _errHandler->recover(this, _localctx->exception);
  }

  return _localctx;
}

//----------------- UpdateContext ------------------------------------------------------------------

pblangParser::UpdateContext::UpdateContext(ParserRuleContext *parent, size_t invokingState)
  : ParserRuleContext(parent, invokingState) {
}

tree::TerminalNode* pblangParser::UpdateContext::ID() {
  return getToken(pblangParser::ID, 0);
}

pblangParser::ExpressionContext* pblangParser::UpdateContext::expression() {
  return getRuleContext<pblangParser::ExpressionContext>(0);
}


size_t pblangParser::UpdateContext::getRuleIndex() const {
  return pblangParser::RuleUpdate;
}

void pblangParser::UpdateContext::enterRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<pblangListener *>(listener);
  if (parserListener != nullptr)
    parserListener->enterUpdate(this);
}

void pblangParser::UpdateContext::exitRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<pblangListener *>(listener);
  if (parserListener != nullptr)
    parserListener->exitUpdate(this);
}

pblangParser::UpdateContext* pblangParser::update() {
  UpdateContext *_localctx = _tracker.createInstance<UpdateContext>(_ctx, getState());
  enterRule(_localctx, 22, pblangParser::RuleUpdate);

#if __cplusplus > 201703L
  auto onExit = finally([=, this] {
#else
  auto onExit = finally([=] {
#endif
    exitRule();
  });
  try {
    enterOuterAlt(_localctx, 1);
    setState(222);
    match(pblangParser::ID);
    setState(223);
    match(pblangParser::T__24);
    setState(224);
    expression();
    setState(225);
    match(pblangParser::T__25);

  }
  catch (RecognitionException &e) {
    _errHandler->reportError(this, e);
    _localctx->exception = std::current_exception();
    _errHandler->recover(this, _localctx->exception);
  }

  return _localctx;
}

//----------------- DefinitionContext ------------------------------------------------------------------

pblangParser::DefinitionContext::DefinitionContext(ParserRuleContext *parent, size_t invokingState)
  : ParserRuleContext(parent, invokingState) {
}

tree::TerminalNode* pblangParser::DefinitionContext::ID() {
  return getToken(pblangParser::ID, 0);
}

std::vector<pblangParser::DeclaredParameterContext *> pblangParser::DefinitionContext::declaredParameter() {
  return getRuleContexts<pblangParser::DeclaredParameterContext>();
}

pblangParser::DeclaredParameterContext* pblangParser::DefinitionContext::declaredParameter(size_t i) {
  return getRuleContext<pblangParser::DeclaredParameterContext>(i);
}

pblangParser::ExpressionContext* pblangParser::DefinitionContext::expression() {
  return getRuleContext<pblangParser::ExpressionContext>(0);
}


size_t pblangParser::DefinitionContext::getRuleIndex() const {
  return pblangParser::RuleDefinition;
}

void pblangParser::DefinitionContext::enterRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<pblangListener *>(listener);
  if (parserListener != nullptr)
    parserListener->enterDefinition(this);
}

void pblangParser::DefinitionContext::exitRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<pblangListener *>(listener);
  if (parserListener != nullptr)
    parserListener->exitDefinition(this);
}

pblangParser::DefinitionContext* pblangParser::definition() {
  DefinitionContext *_localctx = _tracker.createInstance<DefinitionContext>(_ctx, getState());
  enterRule(_localctx, 24, pblangParser::RuleDefinition);
  size_t _la = 0;

#if __cplusplus > 201703L
  auto onExit = finally([=, this] {
#else
  auto onExit = finally([=] {
#endif
    exitRule();
  });
  try {
    enterOuterAlt(_localctx, 1);
    setState(227);
    match(pblangParser::T__26);
    setState(228);
    match(pblangParser::ID);
    setState(240);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__27) {
      setState(229);
      match(pblangParser::T__27);
      setState(230);
      declaredParameter();
      setState(235);
      _errHandler->sync(this);
      _la = _input->LA(1);
      while (_la == pblangParser::T__28) {
        setState(231);
        match(pblangParser::T__28);
        setState(232);
        declaredParameter();
        setState(237);
        _errHandler->sync(this);
        _la = _input->LA(1);
      }
      setState(238);
      match(pblangParser::T__29);
    }
    setState(242);
    match(pblangParser::T__5);
    setState(247);
    _errHandler->sync(this);
    switch (_input->LA(1)) {
      case pblangParser::T__1: {
        setState(243);
        antlrcpp::downCast<DefinitionContext *>(_localctx)->builtin = match(pblangParser::T__1);
        break;
      }

      case pblangParser::T__27:
      case pblangParser::ID:
      case pblangParser::FLOAT: {
        setState(244);
        expression();
        setState(245);
        match(pblangParser::T__25);
        break;
      }

    default:
      throw NoViableAltException(this);
    }

  }
  catch (RecognitionException &e) {
    _errHandler->reportError(this, e);
    _localctx->exception = std::current_exception();
    _errHandler->recover(this, _localctx->exception);
  }

  return _localctx;
}

//----------------- DeclaredParameterContext ------------------------------------------------------------------

pblangParser::DeclaredParameterContext::DeclaredParameterContext(ParserRuleContext *parent, size_t invokingState)
  : ParserRuleContext(parent, invokingState) {
}

tree::TerminalNode* pblangParser::DeclaredParameterContext::ID() {
  return getToken(pblangParser::ID, 0);
}


size_t pblangParser::DeclaredParameterContext::getRuleIndex() const {
  return pblangParser::RuleDeclaredParameter;
}

void pblangParser::DeclaredParameterContext::enterRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<pblangListener *>(listener);
  if (parserListener != nullptr)
    parserListener->enterDeclaredParameter(this);
}

void pblangParser::DeclaredParameterContext::exitRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<pblangListener *>(listener);
  if (parserListener != nullptr)
    parserListener->exitDeclaredParameter(this);
}

pblangParser::DeclaredParameterContext* pblangParser::declaredParameter() {
  DeclaredParameterContext *_localctx = _tracker.createInstance<DeclaredParameterContext>(_ctx, getState());
  enterRule(_localctx, 26, pblangParser::RuleDeclaredParameter);

#if __cplusplus > 201703L
  auto onExit = finally([=, this] {
#else
  auto onExit = finally([=] {
#endif
    exitRule();
  });
  try {
    enterOuterAlt(_localctx, 1);
    setState(249);
    match(pblangParser::ID);

  }
  catch (RecognitionException &e) {
    _errHandler->reportError(this, e);
    _localctx->exception = std::current_exception();
    _errHandler->recover(this, _localctx->exception);
  }

  return _localctx;
}

//----------------- ExpressionContext ------------------------------------------------------------------

pblangParser::ExpressionContext::ExpressionContext(ParserRuleContext *parent, size_t invokingState)
  : ParserRuleContext(parent, invokingState) {
}

pblangParser::AdditionContext* pblangParser::ExpressionContext::addition() {
  return getRuleContext<pblangParser::AdditionContext>(0);
}


size_t pblangParser::ExpressionContext::getRuleIndex() const {
  return pblangParser::RuleExpression;
}

void pblangParser::ExpressionContext::enterRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<pblangListener *>(listener);
  if (parserListener != nullptr)
    parserListener->enterExpression(this);
}

void pblangParser::ExpressionContext::exitRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<pblangListener *>(listener);
  if (parserListener != nullptr)
    parserListener->exitExpression(this);
}

pblangParser::ExpressionContext* pblangParser::expression() {
  ExpressionContext *_localctx = _tracker.createInstance<ExpressionContext>(_ctx, getState());
  enterRule(_localctx, 28, pblangParser::RuleExpression);

#if __cplusplus > 201703L
  auto onExit = finally([=, this] {
#else
  auto onExit = finally([=] {
#endif
    exitRule();
  });
  try {
    enterOuterAlt(_localctx, 1);
    setState(251);
    addition();

  }
  catch (RecognitionException &e) {
    _errHandler->reportError(this, e);
    _localctx->exception = std::current_exception();
    _errHandler->recover(this, _localctx->exception);
  }

  return _localctx;
}

//----------------- AdditionContext ------------------------------------------------------------------

pblangParser::AdditionContext::AdditionContext(ParserRuleContext *parent, size_t invokingState)
  : ParserRuleContext(parent, invokingState) {
}

std::vector<pblangParser::MultiplicationContext *> pblangParser::AdditionContext::multiplication() {
  return getRuleContexts<pblangParser::MultiplicationContext>();
}

pblangParser::MultiplicationContext* pblangParser::AdditionContext::multiplication(size_t i) {
  return getRuleContext<pblangParser::MultiplicationContext>(i);
}


size_t pblangParser::AdditionContext::getRuleIndex() const {
  return pblangParser::RuleAddition;
}

void pblangParser::AdditionContext::enterRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<pblangListener *>(listener);
  if (parserListener != nullptr)
    parserListener->enterAddition(this);
}

void pblangParser::AdditionContext::exitRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<pblangListener *>(listener);
  if (parserListener != nullptr)
    parserListener->exitAddition(this);
}

pblangParser::AdditionContext* pblangParser::addition() {
  AdditionContext *_localctx = _tracker.createInstance<AdditionContext>(_ctx, getState());
  enterRule(_localctx, 30, pblangParser::RuleAddition);
  size_t _la = 0;

#if __cplusplus > 201703L
  auto onExit = finally([=, this] {
#else
  auto onExit = finally([=] {
#endif
    exitRule();
  });
  try {
    enterOuterAlt(_localctx, 1);
    setState(253);
    multiplication();
    setState(258);
    _errHandler->sync(this);
    _la = _input->LA(1);
    while (_la == pblangParser::T__30

    || _la == pblangParser::T__31) {
      setState(254);
      _la = _input->LA(1);
      if (!(_la == pblangParser::T__30

      || _la == pblangParser::T__31)) {
      _errHandler->recoverInline(this);
      }
      else {
        _errHandler->reportMatch(this);
        consume();
      }
      setState(255);
      multiplication();
      setState(260);
      _errHandler->sync(this);
      _la = _input->LA(1);
    }

  }
  catch (RecognitionException &e) {
    _errHandler->reportError(this, e);
    _localctx->exception = std::current_exception();
    _errHandler->recover(this, _localctx->exception);
  }

  return _localctx;
}

//----------------- MultiplicationContext ------------------------------------------------------------------

pblangParser::MultiplicationContext::MultiplicationContext(ParserRuleContext *parent, size_t invokingState)
  : ParserRuleContext(parent, invokingState) {
}

std::vector<pblangParser::ExponentiationContext *> pblangParser::MultiplicationContext::exponentiation() {
  return getRuleContexts<pblangParser::ExponentiationContext>();
}

pblangParser::ExponentiationContext* pblangParser::MultiplicationContext::exponentiation(size_t i) {
  return getRuleContext<pblangParser::ExponentiationContext>(i);
}


size_t pblangParser::MultiplicationContext::getRuleIndex() const {
  return pblangParser::RuleMultiplication;
}

void pblangParser::MultiplicationContext::enterRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<pblangListener *>(listener);
  if (parserListener != nullptr)
    parserListener->enterMultiplication(this);
}

void pblangParser::MultiplicationContext::exitRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<pblangListener *>(listener);
  if (parserListener != nullptr)
    parserListener->exitMultiplication(this);
}

pblangParser::MultiplicationContext* pblangParser::multiplication() {
  MultiplicationContext *_localctx = _tracker.createInstance<MultiplicationContext>(_ctx, getState());
  enterRule(_localctx, 32, pblangParser::RuleMultiplication);
  size_t _la = 0;

#if __cplusplus > 201703L
  auto onExit = finally([=, this] {
#else
  auto onExit = finally([=] {
#endif
    exitRule();
  });
  try {
    enterOuterAlt(_localctx, 1);
    setState(261);
    exponentiation();
    setState(266);
    _errHandler->sync(this);
    _la = _input->LA(1);
    while (_la == pblangParser::T__32

    || _la == pblangParser::T__33) {
      setState(262);
      _la = _input->LA(1);
      if (!(_la == pblangParser::T__32

      || _la == pblangParser::T__33)) {
      _errHandler->recoverInline(this);
      }
      else {
        _errHandler->reportMatch(this);
        consume();
      }
      setState(263);
      exponentiation();
      setState(268);
      _errHandler->sync(this);
      _la = _input->LA(1);
    }

  }
  catch (RecognitionException &e) {
    _errHandler->reportError(this, e);
    _localctx->exception = std::current_exception();
    _errHandler->recover(this, _localctx->exception);
  }

  return _localctx;
}

//----------------- ExponentiationContext ------------------------------------------------------------------

pblangParser::ExponentiationContext::ExponentiationContext(ParserRuleContext *parent, size_t invokingState)
  : ParserRuleContext(parent, invokingState) {
}

std::vector<pblangParser::ModuloContext *> pblangParser::ExponentiationContext::modulo() {
  return getRuleContexts<pblangParser::ModuloContext>();
}

pblangParser::ModuloContext* pblangParser::ExponentiationContext::modulo(size_t i) {
  return getRuleContext<pblangParser::ModuloContext>(i);
}


size_t pblangParser::ExponentiationContext::getRuleIndex() const {
  return pblangParser::RuleExponentiation;
}

void pblangParser::ExponentiationContext::enterRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<pblangListener *>(listener);
  if (parserListener != nullptr)
    parserListener->enterExponentiation(this);
}

void pblangParser::ExponentiationContext::exitRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<pblangListener *>(listener);
  if (parserListener != nullptr)
    parserListener->exitExponentiation(this);
}

pblangParser::ExponentiationContext* pblangParser::exponentiation() {
  ExponentiationContext *_localctx = _tracker.createInstance<ExponentiationContext>(_ctx, getState());
  enterRule(_localctx, 34, pblangParser::RuleExponentiation);
  size_t _la = 0;

#if __cplusplus > 201703L
  auto onExit = finally([=, this] {
#else
  auto onExit = finally([=] {
#endif
    exitRule();
  });
  try {
    enterOuterAlt(_localctx, 1);
    setState(269);
    modulo();
    setState(274);
    _errHandler->sync(this);
    _la = _input->LA(1);
    while (_la == pblangParser::T__34) {
      setState(270);
      match(pblangParser::T__34);
      setState(271);
      modulo();
      setState(276);
      _errHandler->sync(this);
      _la = _input->LA(1);
    }

  }
  catch (RecognitionException &e) {
    _errHandler->reportError(this, e);
    _localctx->exception = std::current_exception();
    _errHandler->recover(this, _localctx->exception);
  }

  return _localctx;
}

//----------------- ModuloContext ------------------------------------------------------------------

pblangParser::ModuloContext::ModuloContext(ParserRuleContext *parent, size_t invokingState)
  : ParserRuleContext(parent, invokingState) {
}

std::vector<pblangParser::PrimaryExpressionContext *> pblangParser::ModuloContext::primaryExpression() {
  return getRuleContexts<pblangParser::PrimaryExpressionContext>();
}

pblangParser::PrimaryExpressionContext* pblangParser::ModuloContext::primaryExpression(size_t i) {
  return getRuleContext<pblangParser::PrimaryExpressionContext>(i);
}


size_t pblangParser::ModuloContext::getRuleIndex() const {
  return pblangParser::RuleModulo;
}

void pblangParser::ModuloContext::enterRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<pblangListener *>(listener);
  if (parserListener != nullptr)
    parserListener->enterModulo(this);
}

void pblangParser::ModuloContext::exitRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<pblangListener *>(listener);
  if (parserListener != nullptr)
    parserListener->exitModulo(this);
}

pblangParser::ModuloContext* pblangParser::modulo() {
  ModuloContext *_localctx = _tracker.createInstance<ModuloContext>(_ctx, getState());
  enterRule(_localctx, 36, pblangParser::RuleModulo);
  size_t _la = 0;

#if __cplusplus > 201703L
  auto onExit = finally([=, this] {
#else
  auto onExit = finally([=] {
#endif
    exitRule();
  });
  try {
    enterOuterAlt(_localctx, 1);
    setState(277);
    primaryExpression();
    setState(282);
    _errHandler->sync(this);
    _la = _input->LA(1);
    while (_la == pblangParser::T__35) {
      setState(278);
      match(pblangParser::T__35);
      setState(279);
      primaryExpression();
      setState(284);
      _errHandler->sync(this);
      _la = _input->LA(1);
    }

  }
  catch (RecognitionException &e) {
    _errHandler->reportError(this, e);
    _localctx->exception = std::current_exception();
    _errHandler->recover(this, _localctx->exception);
  }

  return _localctx;
}

//----------------- PrimaryExpressionContext ------------------------------------------------------------------

pblangParser::PrimaryExpressionContext::PrimaryExpressionContext(ParserRuleContext *parent, size_t invokingState)
  : ParserRuleContext(parent, invokingState) {
}

std::vector<pblangParser::ExpressionContext *> pblangParser::PrimaryExpressionContext::expression() {
  return getRuleContexts<pblangParser::ExpressionContext>();
}

pblangParser::ExpressionContext* pblangParser::PrimaryExpressionContext::expression(size_t i) {
  return getRuleContext<pblangParser::ExpressionContext>(i);
}

tree::TerminalNode* pblangParser::PrimaryExpressionContext::FLOAT() {
  return getToken(pblangParser::FLOAT, 0);
}

tree::TerminalNode* pblangParser::PrimaryExpressionContext::ID() {
  return getToken(pblangParser::ID, 0);
}


size_t pblangParser::PrimaryExpressionContext::getRuleIndex() const {
  return pblangParser::RulePrimaryExpression;
}

void pblangParser::PrimaryExpressionContext::enterRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<pblangListener *>(listener);
  if (parserListener != nullptr)
    parserListener->enterPrimaryExpression(this);
}

void pblangParser::PrimaryExpressionContext::exitRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<pblangListener *>(listener);
  if (parserListener != nullptr)
    parserListener->exitPrimaryExpression(this);
}

pblangParser::PrimaryExpressionContext* pblangParser::primaryExpression() {
  PrimaryExpressionContext *_localctx = _tracker.createInstance<PrimaryExpressionContext>(_ctx, getState());
  enterRule(_localctx, 38, pblangParser::RulePrimaryExpression);
  size_t _la = 0;

#if __cplusplus > 201703L
  auto onExit = finally([=, this] {
#else
  auto onExit = finally([=] {
#endif
    exitRule();
  });
  try {
    setState(305);
    _errHandler->sync(this);
    switch (getInterpreter<atn::ParserATNSimulator>()->adaptivePredict(_input, 39, _ctx)) {
    case 1: {
      enterOuterAlt(_localctx, 1);
      setState(285);
      match(pblangParser::T__27);
      setState(286);
      expression();
      setState(287);
      match(pblangParser::T__29);
      break;
    }

    case 2: {
      enterOuterAlt(_localctx, 2);
      setState(289);
      match(pblangParser::FLOAT);
      break;
    }

    case 3: {
      enterOuterAlt(_localctx, 3);
      setState(290);
      match(pblangParser::ID);
      setState(302);
      _errHandler->sync(this);

      _la = _input->LA(1);
      if (_la == pblangParser::T__27) {
        setState(291);
        match(pblangParser::T__27);
        setState(292);
        expression();
        setState(297);
        _errHandler->sync(this);
        _la = _input->LA(1);
        while (_la == pblangParser::T__28) {
          setState(293);
          match(pblangParser::T__28);
          setState(294);
          expression();
          setState(299);
          _errHandler->sync(this);
          _la = _input->LA(1);
        }
        setState(300);
        match(pblangParser::T__29);
      }
      break;
    }

    case 4: {
      enterOuterAlt(_localctx, 4);
      setState(304);
      match(pblangParser::ID);
      break;
    }

    default:
      break;
    }

  }
  catch (RecognitionException &e) {
    _errHandler->reportError(this, e);
    _localctx->exception = std::current_exception();
    _errHandler->recover(this, _localctx->exception);
  }

  return _localctx;
}

void pblangParser::initialize() {
#if ANTLR4_USE_THREAD_LOCAL_CACHE
  pblangParserInitialize();
#else
  ::antlr4::internal::call_once(pblangParserOnceFlag, pblangParserInitialize);
#endif
}
