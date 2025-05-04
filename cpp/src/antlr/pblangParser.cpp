
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
      "storeState", "unit", "sbmlModel", "sbmlParameter", "sbmlVariable",
      "processDef", "processParameter", "processVariable", "processInput",
      "processOutput", "process", "compositeDef", "update", "definition",
      "declaredParameter", "expression", "addition", "multiplication", "exponentiation",
      "modulo", "primaryExpression"
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
  	4,1,43,336,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,6,2,
  	7,7,7,2,8,7,8,2,9,7,9,2,10,7,10,2,11,7,11,2,12,7,12,2,13,7,13,2,14,7,
  	14,2,15,7,15,2,16,7,16,2,17,7,17,2,18,7,18,2,19,7,19,2,20,7,20,2,21,7,
  	21,2,22,7,22,2,23,7,23,2,24,7,24,2,25,7,25,2,26,7,26,1,0,1,0,1,0,1,0,
  	1,0,1,0,1,0,5,0,62,8,0,10,0,12,0,65,9,0,1,0,1,0,1,1,1,1,1,1,3,1,72,8,
  	1,1,1,1,1,3,1,76,8,1,1,1,1,1,3,1,80,8,1,1,1,1,1,3,1,84,8,1,1,1,5,1,87,
  	8,1,10,1,12,1,90,9,1,1,2,1,2,1,2,1,2,1,2,1,2,3,2,98,8,2,1,2,1,2,1,2,3,
  	2,103,8,2,1,2,1,2,1,2,3,2,108,8,2,1,3,1,3,1,4,1,4,1,4,1,4,1,4,3,4,117,
  	8,4,1,4,1,4,1,4,3,4,122,8,4,1,5,1,5,1,5,1,5,3,5,128,8,5,1,5,1,5,5,5,132,
  	8,5,10,5,12,5,135,9,5,1,6,1,6,1,7,1,7,1,7,1,7,1,7,1,7,1,7,3,7,146,8,7,
  	1,8,1,8,1,8,1,8,1,8,5,8,153,8,8,10,8,12,8,156,9,8,1,8,5,8,159,8,8,10,
  	8,12,8,162,9,8,1,9,1,9,1,9,1,10,1,10,1,10,1,11,1,11,1,11,5,11,173,8,11,
  	10,11,12,11,176,9,11,1,11,5,11,179,8,11,10,11,12,11,182,9,11,1,11,1,11,
  	5,11,186,8,11,10,11,12,11,189,9,11,3,11,191,8,11,1,11,1,11,5,11,195,8,
  	11,10,11,12,11,198,9,11,3,11,200,8,11,1,11,1,11,5,11,204,8,11,10,11,12,
  	11,207,9,11,3,11,209,8,11,1,12,1,12,1,12,1,13,1,13,1,13,1,14,1,14,1,15,
  	1,15,1,16,1,16,1,16,1,16,1,16,5,16,226,8,16,10,16,12,16,229,9,16,3,16,
  	231,8,16,1,17,1,17,1,17,1,17,5,17,237,8,17,10,17,12,17,240,9,17,3,17,
  	242,8,17,1,17,1,17,5,17,246,8,17,10,17,12,17,249,9,17,1,18,1,18,1,18,
  	1,18,1,18,1,19,1,19,1,19,1,19,1,19,1,19,5,19,262,8,19,10,19,12,19,265,
  	9,19,1,19,1,19,3,19,269,8,19,1,19,1,19,1,19,1,19,1,19,3,19,276,8,19,1,
  	20,1,20,1,21,1,21,1,22,1,22,1,22,5,22,285,8,22,10,22,12,22,288,9,22,1,
  	23,1,23,1,23,5,23,293,8,23,10,23,12,23,296,9,23,1,24,1,24,1,24,5,24,301,
  	8,24,10,24,12,24,304,9,24,1,25,1,25,1,25,5,25,309,8,25,10,25,12,25,312,
  	9,25,1,26,1,26,1,26,1,26,1,26,1,26,1,26,1,26,1,26,1,26,5,26,324,8,26,
  	10,26,12,26,327,9,26,1,26,1,26,3,26,331,8,26,1,26,3,26,334,8,26,1,26,
  	0,0,27,0,2,4,6,8,10,12,14,16,18,20,22,24,26,28,30,32,34,36,38,40,42,44,
  	46,48,50,52,0,3,1,0,38,39,1,0,31,32,1,0,33,34,355,0,63,1,0,0,0,2,68,1,
  	0,0,0,4,91,1,0,0,0,6,109,1,0,0,0,8,111,1,0,0,0,10,123,1,0,0,0,12,136,
  	1,0,0,0,14,138,1,0,0,0,16,147,1,0,0,0,18,163,1,0,0,0,20,166,1,0,0,0,22,
  	169,1,0,0,0,24,210,1,0,0,0,26,213,1,0,0,0,28,216,1,0,0,0,30,218,1,0,0,
  	0,32,220,1,0,0,0,34,232,1,0,0,0,36,250,1,0,0,0,38,255,1,0,0,0,40,277,
  	1,0,0,0,42,279,1,0,0,0,44,281,1,0,0,0,46,289,1,0,0,0,48,297,1,0,0,0,50,
  	305,1,0,0,0,52,333,1,0,0,0,54,62,3,2,1,0,55,62,3,38,19,0,56,62,3,14,7,
  	0,57,62,3,22,11,0,58,62,3,10,5,0,59,62,3,34,17,0,60,62,3,16,8,0,61,54,
  	1,0,0,0,61,55,1,0,0,0,61,56,1,0,0,0,61,57,1,0,0,0,61,58,1,0,0,0,61,59,
  	1,0,0,0,61,60,1,0,0,0,62,65,1,0,0,0,63,61,1,0,0,0,63,64,1,0,0,0,64,66,
  	1,0,0,0,65,63,1,0,0,0,66,67,5,0,0,1,67,1,1,0,0,0,68,69,5,1,0,0,69,71,
  	5,37,0,0,70,72,5,2,0,0,71,70,1,0,0,0,71,72,1,0,0,0,72,75,1,0,0,0,73,74,
  	5,3,0,0,74,76,5,37,0,0,75,73,1,0,0,0,75,76,1,0,0,0,76,79,1,0,0,0,77,78,
  	5,4,0,0,78,80,3,6,3,0,79,77,1,0,0,0,79,80,1,0,0,0,80,83,1,0,0,0,81,82,
  	5,5,0,0,82,84,5,37,0,0,83,81,1,0,0,0,83,84,1,0,0,0,84,88,1,0,0,0,85,87,
  	3,4,2,0,86,85,1,0,0,0,87,90,1,0,0,0,88,86,1,0,0,0,88,89,1,0,0,0,89,3,
  	1,0,0,0,90,88,1,0,0,0,91,92,5,37,0,0,92,97,5,6,0,0,93,94,5,7,0,0,94,95,
  	5,8,0,0,95,96,5,37,0,0,96,98,5,9,0,0,97,93,1,0,0,0,97,98,1,0,0,0,98,99,
  	1,0,0,0,99,102,5,37,0,0,100,101,5,4,0,0,101,103,3,6,3,0,102,100,1,0,0,
  	0,102,103,1,0,0,0,103,107,1,0,0,0,104,105,5,8,0,0,105,106,5,37,0,0,106,
  	108,5,9,0,0,107,104,1,0,0,0,107,108,1,0,0,0,108,5,1,0,0,0,109,110,7,0,
  	0,0,110,7,1,0,0,0,111,112,5,37,0,0,112,113,5,6,0,0,113,116,5,37,0,0,114,
  	115,5,4,0,0,115,117,3,6,3,0,116,114,1,0,0,0,116,117,1,0,0,0,117,121,1,
  	0,0,0,118,119,5,8,0,0,119,120,5,37,0,0,120,122,5,9,0,0,121,118,1,0,0,
  	0,121,122,1,0,0,0,122,9,1,0,0,0,123,124,5,10,0,0,124,127,5,37,0,0,125,
  	126,5,11,0,0,126,128,5,37,0,0,127,125,1,0,0,0,127,128,1,0,0,0,128,133,
  	1,0,0,0,129,130,5,12,0,0,130,132,3,12,6,0,131,129,1,0,0,0,132,135,1,0,
  	0,0,133,131,1,0,0,0,133,134,1,0,0,0,134,11,1,0,0,0,135,133,1,0,0,0,136,
  	137,3,8,4,0,137,13,1,0,0,0,138,139,5,13,0,0,139,140,5,37,0,0,140,145,
  	5,6,0,0,141,142,5,8,0,0,142,143,5,40,0,0,143,146,5,9,0,0,144,146,5,37,
  	0,0,145,141,1,0,0,0,145,144,1,0,0,0,146,15,1,0,0,0,147,148,5,14,0,0,148,
  	149,5,37,0,0,149,150,5,15,0,0,150,154,5,40,0,0,151,153,3,18,9,0,152,151,
  	1,0,0,0,153,156,1,0,0,0,154,152,1,0,0,0,154,155,1,0,0,0,155,160,1,0,0,
  	0,156,154,1,0,0,0,157,159,3,20,10,0,158,157,1,0,0,0,159,162,1,0,0,0,160,
  	158,1,0,0,0,160,161,1,0,0,0,161,17,1,0,0,0,162,160,1,0,0,0,163,164,5,
  	16,0,0,164,165,3,8,4,0,165,19,1,0,0,0,166,167,5,17,0,0,167,168,3,8,4,
  	0,168,21,1,0,0,0,169,170,5,18,0,0,170,174,5,37,0,0,171,173,3,24,12,0,
  	172,171,1,0,0,0,173,176,1,0,0,0,174,172,1,0,0,0,174,175,1,0,0,0,175,180,
  	1,0,0,0,176,174,1,0,0,0,177,179,3,26,13,0,178,177,1,0,0,0,179,182,1,0,
  	0,0,180,178,1,0,0,0,180,181,1,0,0,0,181,190,1,0,0,0,182,180,1,0,0,0,183,
  	187,5,19,0,0,184,186,3,28,14,0,185,184,1,0,0,0,186,189,1,0,0,0,187,185,
  	1,0,0,0,187,188,1,0,0,0,188,191,1,0,0,0,189,187,1,0,0,0,190,183,1,0,0,
  	0,190,191,1,0,0,0,191,199,1,0,0,0,192,196,5,20,0,0,193,195,3,30,15,0,
  	194,193,1,0,0,0,195,198,1,0,0,0,196,194,1,0,0,0,196,197,1,0,0,0,197,200,
  	1,0,0,0,198,196,1,0,0,0,199,192,1,0,0,0,199,200,1,0,0,0,200,208,1,0,0,
  	0,201,205,5,21,0,0,202,204,3,36,18,0,203,202,1,0,0,0,204,207,1,0,0,0,
  	205,203,1,0,0,0,205,206,1,0,0,0,206,209,1,0,0,0,207,205,1,0,0,0,208,201,
  	1,0,0,0,208,209,1,0,0,0,209,23,1,0,0,0,210,211,5,16,0,0,211,212,3,8,4,
  	0,212,25,1,0,0,0,213,214,5,17,0,0,214,215,3,8,4,0,215,27,1,0,0,0,216,
  	217,5,37,0,0,217,29,1,0,0,0,218,219,5,37,0,0,219,31,1,0,0,0,220,221,5,
  	37,0,0,221,222,5,6,0,0,222,230,5,37,0,0,223,227,5,22,0,0,224,226,5,37,
  	0,0,225,224,1,0,0,0,226,229,1,0,0,0,227,225,1,0,0,0,227,228,1,0,0,0,228,
  	231,1,0,0,0,229,227,1,0,0,0,230,223,1,0,0,0,230,231,1,0,0,0,231,33,1,
  	0,0,0,232,233,5,23,0,0,233,241,5,37,0,0,234,238,5,22,0,0,235,237,5,37,
  	0,0,236,235,1,0,0,0,237,240,1,0,0,0,238,236,1,0,0,0,238,239,1,0,0,0,239,
  	242,1,0,0,0,240,238,1,0,0,0,241,234,1,0,0,0,241,242,1,0,0,0,242,247,1,
  	0,0,0,243,244,5,24,0,0,244,246,3,32,16,0,245,243,1,0,0,0,246,249,1,0,
  	0,0,247,245,1,0,0,0,247,248,1,0,0,0,248,35,1,0,0,0,249,247,1,0,0,0,250,
  	251,5,37,0,0,251,252,5,25,0,0,252,253,3,42,21,0,253,254,5,26,0,0,254,
  	37,1,0,0,0,255,256,5,27,0,0,256,268,5,37,0,0,257,258,5,28,0,0,258,263,
  	3,40,20,0,259,260,5,29,0,0,260,262,3,40,20,0,261,259,1,0,0,0,262,265,
  	1,0,0,0,263,261,1,0,0,0,263,264,1,0,0,0,264,266,1,0,0,0,265,263,1,0,0,
  	0,266,267,5,30,0,0,267,269,1,0,0,0,268,257,1,0,0,0,268,269,1,0,0,0,269,
  	270,1,0,0,0,270,275,5,6,0,0,271,276,5,2,0,0,272,273,3,42,21,0,273,274,
  	5,26,0,0,274,276,1,0,0,0,275,271,1,0,0,0,275,272,1,0,0,0,276,39,1,0,0,
  	0,277,278,5,37,0,0,278,41,1,0,0,0,279,280,3,44,22,0,280,43,1,0,0,0,281,
  	286,3,46,23,0,282,283,7,1,0,0,283,285,3,46,23,0,284,282,1,0,0,0,285,288,
  	1,0,0,0,286,284,1,0,0,0,286,287,1,0,0,0,287,45,1,0,0,0,288,286,1,0,0,
  	0,289,294,3,48,24,0,290,291,7,2,0,0,291,293,3,48,24,0,292,290,1,0,0,0,
  	293,296,1,0,0,0,294,292,1,0,0,0,294,295,1,0,0,0,295,47,1,0,0,0,296,294,
  	1,0,0,0,297,302,3,50,25,0,298,299,5,35,0,0,299,301,3,50,25,0,300,298,
  	1,0,0,0,301,304,1,0,0,0,302,300,1,0,0,0,302,303,1,0,0,0,303,49,1,0,0,
  	0,304,302,1,0,0,0,305,310,3,52,26,0,306,307,5,36,0,0,307,309,3,52,26,
  	0,308,306,1,0,0,0,309,312,1,0,0,0,310,308,1,0,0,0,310,311,1,0,0,0,311,
  	51,1,0,0,0,312,310,1,0,0,0,313,314,5,28,0,0,314,315,3,42,21,0,315,316,
  	5,30,0,0,316,334,1,0,0,0,317,334,5,38,0,0,318,330,5,37,0,0,319,320,5,
  	28,0,0,320,325,3,42,21,0,321,322,5,29,0,0,322,324,3,42,21,0,323,321,1,
  	0,0,0,324,327,1,0,0,0,325,323,1,0,0,0,325,326,1,0,0,0,326,328,1,0,0,0,
  	327,325,1,0,0,0,328,329,5,30,0,0,329,331,1,0,0,0,330,319,1,0,0,0,330,
  	331,1,0,0,0,331,334,1,0,0,0,332,334,5,37,0,0,333,313,1,0,0,0,333,317,
  	1,0,0,0,333,318,1,0,0,0,333,332,1,0,0,0,334,53,1,0,0,0,40,61,63,71,75,
  	79,83,88,97,102,107,116,121,127,133,145,154,160,174,180,187,190,196,199,
  	205,208,227,230,238,241,247,263,268,275,286,294,302,310,325,330,333
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
    setState(63);
    _errHandler->sync(this);
    _la = _input->LA(1);
    while ((((_la & ~ 0x3fULL) == 0) &&
      ((1ULL << _la) & 142894082) != 0)) {
      setState(61);
      _errHandler->sync(this);
      switch (_input->LA(1)) {
        case pblangParser::T__0: {
          setState(54);
          type();
          break;
        }

        case pblangParser::T__26: {
          setState(55);
          definition();
          break;
        }

        case pblangParser::T__12: {
          setState(56);
          unit();
          break;
        }

        case pblangParser::T__17: {
          setState(57);
          processDef();
          break;
        }

        case pblangParser::T__9: {
          setState(58);
          store();
          break;
        }

        case pblangParser::T__22: {
          setState(59);
          compositeDef();
          break;
        }

        case pblangParser::T__13: {
          setState(60);
          sbmlModel();
          break;
        }

      default:
        throw NoViableAltException(this);
      }
      setState(65);
      _errHandler->sync(this);
      _la = _input->LA(1);
    }
    setState(66);
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
    setState(68);
    match(pblangParser::T__0);
    setState(69);
    match(pblangParser::ID);
    setState(71);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__1) {
      setState(70);
      antlrcpp::downCast<TypeContext *>(_localctx)->builtin = match(pblangParser::T__1);
    }
    setState(75);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__2) {
      setState(73);
      match(pblangParser::T__2);
      setState(74);
      match(pblangParser::ID);
    }
    setState(79);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__3) {
      setState(77);
      match(pblangParser::T__3);
      setState(78);
      defaultValue();
    }
    setState(83);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__4) {
      setState(81);
      match(pblangParser::T__4);
      setState(82);
      match(pblangParser::ID);
    }
    setState(88);
    _errHandler->sync(this);
    _la = _input->LA(1);
    while (_la == pblangParser::ID) {
      setState(85);
      namedType();
      setState(90);
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
    setState(91);
    match(pblangParser::ID);
    setState(92);
    match(pblangParser::T__5);
    setState(97);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__6) {
      setState(93);
      match(pblangParser::T__6);
      setState(94);
      match(pblangParser::T__7);
      setState(95);
      match(pblangParser::ID);
      setState(96);
      match(pblangParser::T__8);
    }
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
    setState(109);
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
    setState(111);
    match(pblangParser::ID);
    setState(112);
    match(pblangParser::T__5);
    setState(113);
    match(pblangParser::ID);
    setState(116);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__3) {
      setState(114);
      match(pblangParser::T__3);
      setState(115);
      defaultValue();
    }
    setState(121);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__7) {
      setState(118);
      match(pblangParser::T__7);
      setState(119);
      match(pblangParser::ID);
      setState(120);
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

std::vector<pblangParser::StoreStateContext *> pblangParser::StoreContext::storeState() {
  return getRuleContexts<pblangParser::StoreStateContext>();
}

pblangParser::StoreStateContext* pblangParser::StoreContext::storeState(size_t i) {
  return getRuleContext<pblangParser::StoreStateContext>(i);
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
    setState(123);
    match(pblangParser::T__9);
    setState(124);
    match(pblangParser::ID);
    setState(127);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__10) {
      setState(125);
      match(pblangParser::T__10);
      setState(126);
      match(pblangParser::ID);
    }
    setState(133);
    _errHandler->sync(this);
    _la = _input->LA(1);
    while (_la == pblangParser::T__11) {
      setState(129);
      match(pblangParser::T__11);
      setState(130);
      storeState();
      setState(135);
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

//----------------- StoreStateContext ------------------------------------------------------------------

pblangParser::StoreStateContext::StoreStateContext(ParserRuleContext *parent, size_t invokingState)
  : ParserRuleContext(parent, invokingState) {
}

pblangParser::SchemaItemContext* pblangParser::StoreStateContext::schemaItem() {
  return getRuleContext<pblangParser::SchemaItemContext>(0);
}


size_t pblangParser::StoreStateContext::getRuleIndex() const {
  return pblangParser::RuleStoreState;
}

void pblangParser::StoreStateContext::enterRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<pblangListener *>(listener);
  if (parserListener != nullptr)
    parserListener->enterStoreState(this);
}

void pblangParser::StoreStateContext::exitRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<pblangListener *>(listener);
  if (parserListener != nullptr)
    parserListener->exitStoreState(this);
}

pblangParser::StoreStateContext* pblangParser::storeState() {
  StoreStateContext *_localctx = _tracker.createInstance<StoreStateContext>(_ctx, getState());
  enterRule(_localctx, 12, pblangParser::RuleStoreState);

#if __cplusplus > 201703L
  auto onExit = finally([=, this] {
#else
  auto onExit = finally([=] {
#endif
    exitRule();
  });
  try {
    enterOuterAlt(_localctx, 1);
    setState(136);
    schemaItem();

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
  enterRule(_localctx, 14, pblangParser::RuleUnit);

#if __cplusplus > 201703L
  auto onExit = finally([=, this] {
#else
  auto onExit = finally([=] {
#endif
    exitRule();
  });
  try {
    enterOuterAlt(_localctx, 1);
    setState(138);
    match(pblangParser::T__12);
    setState(139);
    match(pblangParser::ID);
    setState(140);
    match(pblangParser::T__5);
    setState(145);
    _errHandler->sync(this);
    switch (_input->LA(1)) {
      case pblangParser::T__7: {
        setState(141);
        match(pblangParser::T__7);
        setState(142);
        match(pblangParser::STRING);
        setState(143);
        match(pblangParser::T__8);
        break;
      }

      case pblangParser::ID: {
        setState(144);
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

std::vector<pblangParser::SbmlParameterContext *> pblangParser::SbmlModelContext::sbmlParameter() {
  return getRuleContexts<pblangParser::SbmlParameterContext>();
}

pblangParser::SbmlParameterContext* pblangParser::SbmlModelContext::sbmlParameter(size_t i) {
  return getRuleContext<pblangParser::SbmlParameterContext>(i);
}

std::vector<pblangParser::SbmlVariableContext *> pblangParser::SbmlModelContext::sbmlVariable() {
  return getRuleContexts<pblangParser::SbmlVariableContext>();
}

pblangParser::SbmlVariableContext* pblangParser::SbmlModelContext::sbmlVariable(size_t i) {
  return getRuleContext<pblangParser::SbmlVariableContext>(i);
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
  enterRule(_localctx, 16, pblangParser::RuleSbmlModel);
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
    setState(147);
    match(pblangParser::T__13);
    setState(148);
    match(pblangParser::ID);
    setState(149);
    match(pblangParser::T__14);
    setState(150);
    match(pblangParser::STRING);
    setState(154);
    _errHandler->sync(this);
    _la = _input->LA(1);
    while (_la == pblangParser::T__15) {
      setState(151);
      sbmlParameter();
      setState(156);
      _errHandler->sync(this);
      _la = _input->LA(1);
    }
    setState(160);
    _errHandler->sync(this);
    _la = _input->LA(1);
    while (_la == pblangParser::T__16) {
      setState(157);
      sbmlVariable();
      setState(162);
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

//----------------- SbmlParameterContext ------------------------------------------------------------------

pblangParser::SbmlParameterContext::SbmlParameterContext(ParserRuleContext *parent, size_t invokingState)
  : ParserRuleContext(parent, invokingState) {
}

pblangParser::SchemaItemContext* pblangParser::SbmlParameterContext::schemaItem() {
  return getRuleContext<pblangParser::SchemaItemContext>(0);
}


size_t pblangParser::SbmlParameterContext::getRuleIndex() const {
  return pblangParser::RuleSbmlParameter;
}

void pblangParser::SbmlParameterContext::enterRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<pblangListener *>(listener);
  if (parserListener != nullptr)
    parserListener->enterSbmlParameter(this);
}

void pblangParser::SbmlParameterContext::exitRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<pblangListener *>(listener);
  if (parserListener != nullptr)
    parserListener->exitSbmlParameter(this);
}

pblangParser::SbmlParameterContext* pblangParser::sbmlParameter() {
  SbmlParameterContext *_localctx = _tracker.createInstance<SbmlParameterContext>(_ctx, getState());
  enterRule(_localctx, 18, pblangParser::RuleSbmlParameter);

#if __cplusplus > 201703L
  auto onExit = finally([=, this] {
#else
  auto onExit = finally([=] {
#endif
    exitRule();
  });
  try {
    enterOuterAlt(_localctx, 1);
    setState(163);
    match(pblangParser::T__15);
    setState(164);
    schemaItem();

  }
  catch (RecognitionException &e) {
    _errHandler->reportError(this, e);
    _localctx->exception = std::current_exception();
    _errHandler->recover(this, _localctx->exception);
  }

  return _localctx;
}

//----------------- SbmlVariableContext ------------------------------------------------------------------

pblangParser::SbmlVariableContext::SbmlVariableContext(ParserRuleContext *parent, size_t invokingState)
  : ParserRuleContext(parent, invokingState) {
}

pblangParser::SchemaItemContext* pblangParser::SbmlVariableContext::schemaItem() {
  return getRuleContext<pblangParser::SchemaItemContext>(0);
}


size_t pblangParser::SbmlVariableContext::getRuleIndex() const {
  return pblangParser::RuleSbmlVariable;
}

void pblangParser::SbmlVariableContext::enterRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<pblangListener *>(listener);
  if (parserListener != nullptr)
    parserListener->enterSbmlVariable(this);
}

void pblangParser::SbmlVariableContext::exitRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<pblangListener *>(listener);
  if (parserListener != nullptr)
    parserListener->exitSbmlVariable(this);
}

pblangParser::SbmlVariableContext* pblangParser::sbmlVariable() {
  SbmlVariableContext *_localctx = _tracker.createInstance<SbmlVariableContext>(_ctx, getState());
  enterRule(_localctx, 20, pblangParser::RuleSbmlVariable);

#if __cplusplus > 201703L
  auto onExit = finally([=, this] {
#else
  auto onExit = finally([=] {
#endif
    exitRule();
  });
  try {
    enterOuterAlt(_localctx, 1);
    setState(166);
    match(pblangParser::T__16);
    setState(167);
    schemaItem();

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

tree::TerminalNode* pblangParser::ProcessDefContext::ID() {
  return getToken(pblangParser::ID, 0);
}

std::vector<pblangParser::ProcessParameterContext *> pblangParser::ProcessDefContext::processParameter() {
  return getRuleContexts<pblangParser::ProcessParameterContext>();
}

pblangParser::ProcessParameterContext* pblangParser::ProcessDefContext::processParameter(size_t i) {
  return getRuleContext<pblangParser::ProcessParameterContext>(i);
}

std::vector<pblangParser::ProcessVariableContext *> pblangParser::ProcessDefContext::processVariable() {
  return getRuleContexts<pblangParser::ProcessVariableContext>();
}

pblangParser::ProcessVariableContext* pblangParser::ProcessDefContext::processVariable(size_t i) {
  return getRuleContext<pblangParser::ProcessVariableContext>(i);
}

std::vector<pblangParser::ProcessInputContext *> pblangParser::ProcessDefContext::processInput() {
  return getRuleContexts<pblangParser::ProcessInputContext>();
}

pblangParser::ProcessInputContext* pblangParser::ProcessDefContext::processInput(size_t i) {
  return getRuleContext<pblangParser::ProcessInputContext>(i);
}

std::vector<pblangParser::ProcessOutputContext *> pblangParser::ProcessDefContext::processOutput() {
  return getRuleContexts<pblangParser::ProcessOutputContext>();
}

pblangParser::ProcessOutputContext* pblangParser::ProcessDefContext::processOutput(size_t i) {
  return getRuleContext<pblangParser::ProcessOutputContext>(i);
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
  enterRule(_localctx, 22, pblangParser::RuleProcessDef);
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
    setState(169);
    match(pblangParser::T__17);
    setState(170);
    match(pblangParser::ID);
    setState(174);
    _errHandler->sync(this);
    _la = _input->LA(1);
    while (_la == pblangParser::T__15) {
      setState(171);
      processParameter();
      setState(176);
      _errHandler->sync(this);
      _la = _input->LA(1);
    }
    setState(180);
    _errHandler->sync(this);
    _la = _input->LA(1);
    while (_la == pblangParser::T__16) {
      setState(177);
      processVariable();
      setState(182);
      _errHandler->sync(this);
      _la = _input->LA(1);
    }
    setState(190);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__18) {
      setState(183);
      match(pblangParser::T__18);
      setState(187);
      _errHandler->sync(this);
      _la = _input->LA(1);
      while (_la == pblangParser::ID) {
        setState(184);
        processInput();
        setState(189);
        _errHandler->sync(this);
        _la = _input->LA(1);
      }
    }
    setState(199);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__19) {
      setState(192);
      match(pblangParser::T__19);
      setState(196);
      _errHandler->sync(this);
      _la = _input->LA(1);
      while (_la == pblangParser::ID) {
        setState(193);
        processOutput();
        setState(198);
        _errHandler->sync(this);
        _la = _input->LA(1);
      }
    }
    setState(208);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__20) {
      setState(201);
      match(pblangParser::T__20);
      setState(205);
      _errHandler->sync(this);
      _la = _input->LA(1);
      while (_la == pblangParser::ID) {
        setState(202);
        update();
        setState(207);
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

//----------------- ProcessParameterContext ------------------------------------------------------------------

pblangParser::ProcessParameterContext::ProcessParameterContext(ParserRuleContext *parent, size_t invokingState)
  : ParserRuleContext(parent, invokingState) {
}

pblangParser::SchemaItemContext* pblangParser::ProcessParameterContext::schemaItem() {
  return getRuleContext<pblangParser::SchemaItemContext>(0);
}


size_t pblangParser::ProcessParameterContext::getRuleIndex() const {
  return pblangParser::RuleProcessParameter;
}

void pblangParser::ProcessParameterContext::enterRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<pblangListener *>(listener);
  if (parserListener != nullptr)
    parserListener->enterProcessParameter(this);
}

void pblangParser::ProcessParameterContext::exitRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<pblangListener *>(listener);
  if (parserListener != nullptr)
    parserListener->exitProcessParameter(this);
}

pblangParser::ProcessParameterContext* pblangParser::processParameter() {
  ProcessParameterContext *_localctx = _tracker.createInstance<ProcessParameterContext>(_ctx, getState());
  enterRule(_localctx, 24, pblangParser::RuleProcessParameter);

#if __cplusplus > 201703L
  auto onExit = finally([=, this] {
#else
  auto onExit = finally([=] {
#endif
    exitRule();
  });
  try {
    enterOuterAlt(_localctx, 1);
    setState(210);
    match(pblangParser::T__15);
    setState(211);
    schemaItem();

  }
  catch (RecognitionException &e) {
    _errHandler->reportError(this, e);
    _localctx->exception = std::current_exception();
    _errHandler->recover(this, _localctx->exception);
  }

  return _localctx;
}

//----------------- ProcessVariableContext ------------------------------------------------------------------

pblangParser::ProcessVariableContext::ProcessVariableContext(ParserRuleContext *parent, size_t invokingState)
  : ParserRuleContext(parent, invokingState) {
}

pblangParser::SchemaItemContext* pblangParser::ProcessVariableContext::schemaItem() {
  return getRuleContext<pblangParser::SchemaItemContext>(0);
}


size_t pblangParser::ProcessVariableContext::getRuleIndex() const {
  return pblangParser::RuleProcessVariable;
}

void pblangParser::ProcessVariableContext::enterRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<pblangListener *>(listener);
  if (parserListener != nullptr)
    parserListener->enterProcessVariable(this);
}

void pblangParser::ProcessVariableContext::exitRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<pblangListener *>(listener);
  if (parserListener != nullptr)
    parserListener->exitProcessVariable(this);
}

pblangParser::ProcessVariableContext* pblangParser::processVariable() {
  ProcessVariableContext *_localctx = _tracker.createInstance<ProcessVariableContext>(_ctx, getState());
  enterRule(_localctx, 26, pblangParser::RuleProcessVariable);

#if __cplusplus > 201703L
  auto onExit = finally([=, this] {
#else
  auto onExit = finally([=] {
#endif
    exitRule();
  });
  try {
    enterOuterAlt(_localctx, 1);
    setState(213);
    match(pblangParser::T__16);
    setState(214);
    schemaItem();

  }
  catch (RecognitionException &e) {
    _errHandler->reportError(this, e);
    _localctx->exception = std::current_exception();
    _errHandler->recover(this, _localctx->exception);
  }

  return _localctx;
}

//----------------- ProcessInputContext ------------------------------------------------------------------

pblangParser::ProcessInputContext::ProcessInputContext(ParserRuleContext *parent, size_t invokingState)
  : ParserRuleContext(parent, invokingState) {
}

tree::TerminalNode* pblangParser::ProcessInputContext::ID() {
  return getToken(pblangParser::ID, 0);
}


size_t pblangParser::ProcessInputContext::getRuleIndex() const {
  return pblangParser::RuleProcessInput;
}

void pblangParser::ProcessInputContext::enterRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<pblangListener *>(listener);
  if (parserListener != nullptr)
    parserListener->enterProcessInput(this);
}

void pblangParser::ProcessInputContext::exitRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<pblangListener *>(listener);
  if (parserListener != nullptr)
    parserListener->exitProcessInput(this);
}

pblangParser::ProcessInputContext* pblangParser::processInput() {
  ProcessInputContext *_localctx = _tracker.createInstance<ProcessInputContext>(_ctx, getState());
  enterRule(_localctx, 28, pblangParser::RuleProcessInput);

#if __cplusplus > 201703L
  auto onExit = finally([=, this] {
#else
  auto onExit = finally([=] {
#endif
    exitRule();
  });
  try {
    enterOuterAlt(_localctx, 1);
    setState(216);
    match(pblangParser::ID);

  }
  catch (RecognitionException &e) {
    _errHandler->reportError(this, e);
    _localctx->exception = std::current_exception();
    _errHandler->recover(this, _localctx->exception);
  }

  return _localctx;
}

//----------------- ProcessOutputContext ------------------------------------------------------------------

pblangParser::ProcessOutputContext::ProcessOutputContext(ParserRuleContext *parent, size_t invokingState)
  : ParserRuleContext(parent, invokingState) {
}

tree::TerminalNode* pblangParser::ProcessOutputContext::ID() {
  return getToken(pblangParser::ID, 0);
}


size_t pblangParser::ProcessOutputContext::getRuleIndex() const {
  return pblangParser::RuleProcessOutput;
}

void pblangParser::ProcessOutputContext::enterRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<pblangListener *>(listener);
  if (parserListener != nullptr)
    parserListener->enterProcessOutput(this);
}

void pblangParser::ProcessOutputContext::exitRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<pblangListener *>(listener);
  if (parserListener != nullptr)
    parserListener->exitProcessOutput(this);
}

pblangParser::ProcessOutputContext* pblangParser::processOutput() {
  ProcessOutputContext *_localctx = _tracker.createInstance<ProcessOutputContext>(_ctx, getState());
  enterRule(_localctx, 30, pblangParser::RuleProcessOutput);

#if __cplusplus > 201703L
  auto onExit = finally([=, this] {
#else
  auto onExit = finally([=] {
#endif
    exitRule();
  });
  try {
    enterOuterAlt(_localctx, 1);
    setState(218);
    match(pblangParser::ID);

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
  enterRule(_localctx, 32, pblangParser::RuleProcess);
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
    setState(220);
    match(pblangParser::ID);
    setState(221);
    match(pblangParser::T__5);
    setState(222);
    match(pblangParser::ID);
    setState(230);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__21) {
      setState(223);
      match(pblangParser::T__21);
      setState(227);
      _errHandler->sync(this);
      _la = _input->LA(1);
      while (_la == pblangParser::ID) {
        setState(224);
        match(pblangParser::ID);
        setState(229);
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
  enterRule(_localctx, 34, pblangParser::RuleCompositeDef);
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
    setState(232);
    match(pblangParser::T__22);
    setState(233);
    match(pblangParser::ID);
    setState(241);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__21) {
      setState(234);
      match(pblangParser::T__21);
      setState(238);
      _errHandler->sync(this);
      _la = _input->LA(1);
      while (_la == pblangParser::ID) {
        setState(235);
        match(pblangParser::ID);
        setState(240);
        _errHandler->sync(this);
        _la = _input->LA(1);
      }
    }
    setState(247);
    _errHandler->sync(this);
    _la = _input->LA(1);
    while (_la == pblangParser::T__23) {
      setState(243);
      match(pblangParser::T__23);
      setState(244);
      process();
      setState(249);
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
  enterRule(_localctx, 36, pblangParser::RuleUpdate);

#if __cplusplus > 201703L
  auto onExit = finally([=, this] {
#else
  auto onExit = finally([=] {
#endif
    exitRule();
  });
  try {
    enterOuterAlt(_localctx, 1);
    setState(250);
    match(pblangParser::ID);
    setState(251);
    match(pblangParser::T__24);
    setState(252);
    expression();
    setState(253);
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
  enterRule(_localctx, 38, pblangParser::RuleDefinition);
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
    setState(255);
    match(pblangParser::T__26);
    setState(256);
    match(pblangParser::ID);
    setState(268);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__27) {
      setState(257);
      match(pblangParser::T__27);
      setState(258);
      declaredParameter();
      setState(263);
      _errHandler->sync(this);
      _la = _input->LA(1);
      while (_la == pblangParser::T__28) {
        setState(259);
        match(pblangParser::T__28);
        setState(260);
        declaredParameter();
        setState(265);
        _errHandler->sync(this);
        _la = _input->LA(1);
      }
      setState(266);
      match(pblangParser::T__29);
    }
    setState(270);
    match(pblangParser::T__5);
    setState(275);
    _errHandler->sync(this);
    switch (_input->LA(1)) {
      case pblangParser::T__1: {
        setState(271);
        antlrcpp::downCast<DefinitionContext *>(_localctx)->builtin = match(pblangParser::T__1);
        break;
      }

      case pblangParser::T__27:
      case pblangParser::ID:
      case pblangParser::FLOAT: {
        setState(272);
        expression();
        setState(273);
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
  enterRule(_localctx, 40, pblangParser::RuleDeclaredParameter);

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
  enterRule(_localctx, 42, pblangParser::RuleExpression);

#if __cplusplus > 201703L
  auto onExit = finally([=, this] {
#else
  auto onExit = finally([=] {
#endif
    exitRule();
  });
  try {
    enterOuterAlt(_localctx, 1);
    setState(279);
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
  enterRule(_localctx, 44, pblangParser::RuleAddition);
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
    setState(281);
    multiplication();
    setState(286);
    _errHandler->sync(this);
    _la = _input->LA(1);
    while (_la == pblangParser::T__30

    || _la == pblangParser::T__31) {
      setState(282);
      _la = _input->LA(1);
      if (!(_la == pblangParser::T__30

      || _la == pblangParser::T__31)) {
      _errHandler->recoverInline(this);
      }
      else {
        _errHandler->reportMatch(this);
        consume();
      }
      setState(283);
      multiplication();
      setState(288);
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
  enterRule(_localctx, 46, pblangParser::RuleMultiplication);
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
    setState(289);
    exponentiation();
    setState(294);
    _errHandler->sync(this);
    _la = _input->LA(1);
    while (_la == pblangParser::T__32

    || _la == pblangParser::T__33) {
      setState(290);
      _la = _input->LA(1);
      if (!(_la == pblangParser::T__32

      || _la == pblangParser::T__33)) {
      _errHandler->recoverInline(this);
      }
      else {
        _errHandler->reportMatch(this);
        consume();
      }
      setState(291);
      exponentiation();
      setState(296);
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
  enterRule(_localctx, 48, pblangParser::RuleExponentiation);
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
    setState(297);
    modulo();
    setState(302);
    _errHandler->sync(this);
    _la = _input->LA(1);
    while (_la == pblangParser::T__34) {
      setState(298);
      match(pblangParser::T__34);
      setState(299);
      modulo();
      setState(304);
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
  enterRule(_localctx, 50, pblangParser::RuleModulo);
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
    setState(305);
    primaryExpression();
    setState(310);
    _errHandler->sync(this);
    _la = _input->LA(1);
    while (_la == pblangParser::T__35) {
      setState(306);
      match(pblangParser::T__35);
      setState(307);
      primaryExpression();
      setState(312);
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
  enterRule(_localctx, 52, pblangParser::RulePrimaryExpression);
  size_t _la = 0;

#if __cplusplus > 201703L
  auto onExit = finally([=, this] {
#else
  auto onExit = finally([=] {
#endif
    exitRule();
  });
  try {
    setState(333);
    _errHandler->sync(this);
    switch (getInterpreter<atn::ParserATNSimulator>()->adaptivePredict(_input, 39, _ctx)) {
    case 1: {
      enterOuterAlt(_localctx, 1);
      setState(313);
      match(pblangParser::T__27);
      setState(314);
      expression();
      setState(315);
      match(pblangParser::T__29);
      break;
    }

    case 2: {
      enterOuterAlt(_localctx, 2);
      setState(317);
      match(pblangParser::FLOAT);
      break;
    }

    case 3: {
      enterOuterAlt(_localctx, 3);
      setState(318);
      match(pblangParser::ID);
      setState(330);
      _errHandler->sync(this);

      _la = _input->LA(1);
      if (_la == pblangParser::T__27) {
        setState(319);
        match(pblangParser::T__27);
        setState(320);
        expression();
        setState(325);
        _errHandler->sync(this);
        _la = _input->LA(1);
        while (_la == pblangParser::T__28) {
          setState(321);
          match(pblangParser::T__28);
          setState(322);
          expression();
          setState(327);
          _errHandler->sync(this);
          _la = _input->LA(1);
        }
        setState(328);
        match(pblangParser::T__29);
      }
      break;
    }

    case 4: {
      enterOuterAlt(_localctx, 4);
      setState(332);
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
