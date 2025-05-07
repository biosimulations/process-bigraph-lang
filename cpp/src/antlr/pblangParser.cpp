
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
      "model", "typeDef", "namedType", "defaultValue", "schemaItem", "store",
      "storeState", "unit", "sbmlModel", "sbmlParameter", "sbmlVariable",
      "processDef", "pythonRef", "processParameter", "processVariable",
      "processInput", "processOutput", "process", "compositeDef", "update",
      "definition", "declaredParameter", "expression", "addition", "multiplication",
      "exponentiation", "modulo", "primaryExpression"
    },
    std::vector<std::string>{
      "", "'type'", "'builtin'", "'extends'", "'default'", "'update'", "':'",
      "'maybe'", "'['", "']'", "'store'", "'parent'", "'state'", "'unit'",
      "'sbml'", "'file'", "'param'", "'var'", "'process_def'", "'inputs'",
      "'outputs'", "'updates'", "'path'", "'.'", "'stores'", "'composite_def'",
      "'process'", "':='", "';'", "'def'", "'('", "','", "')'", "'+'", "'-'",
      "'*'", "'/'", "'^'", "'%'"
    },
    std::vector<std::string>{
      "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
      "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
      "", "", "", "", "", "ID", "FLOAT", "INT", "STRING", "WS", "ML_COMMENT",
      "SL_COMMENT"
    }
  );
  static const int32_t serializedATNSegment[] = {
  	4,1,45,350,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,6,2,
  	7,7,7,2,8,7,8,2,9,7,9,2,10,7,10,2,11,7,11,2,12,7,12,2,13,7,13,2,14,7,
  	14,2,15,7,15,2,16,7,16,2,17,7,17,2,18,7,18,2,19,7,19,2,20,7,20,2,21,7,
  	21,2,22,7,22,2,23,7,23,2,24,7,24,2,25,7,25,2,26,7,26,2,27,7,27,1,0,1,
  	0,1,0,1,0,1,0,1,0,1,0,5,0,64,8,0,10,0,12,0,67,9,0,1,0,1,0,1,1,1,1,1,1,
  	3,1,74,8,1,1,1,1,1,3,1,78,8,1,1,1,1,1,3,1,82,8,1,1,1,1,1,3,1,86,8,1,1,
  	1,5,1,89,8,1,10,1,12,1,92,9,1,1,2,1,2,1,2,1,2,1,2,1,2,3,2,100,8,2,1,2,
  	1,2,1,2,3,2,105,8,2,1,2,1,2,1,2,3,2,110,8,2,1,3,1,3,1,4,1,4,1,4,1,4,1,
  	4,3,4,119,8,4,1,4,1,4,1,4,3,4,124,8,4,1,5,1,5,1,5,1,5,3,5,130,8,5,1,5,
  	1,5,5,5,134,8,5,10,5,12,5,137,9,5,1,6,1,6,1,7,1,7,1,7,1,7,1,7,1,7,1,7,
  	3,7,148,8,7,1,8,1,8,1,8,1,8,1,8,5,8,155,8,8,10,8,12,8,158,9,8,1,8,5,8,
  	161,8,8,10,8,12,8,164,9,8,1,9,1,9,1,9,1,10,1,10,1,10,1,11,1,11,1,11,3,
  	11,175,8,11,1,11,5,11,178,8,11,10,11,12,11,181,9,11,1,11,5,11,184,8,11,
  	10,11,12,11,187,9,11,1,11,1,11,5,11,191,8,11,10,11,12,11,194,9,11,3,11,
  	196,8,11,1,11,1,11,5,11,200,8,11,10,11,12,11,203,9,11,3,11,205,8,11,1,
  	11,1,11,5,11,209,8,11,10,11,12,11,212,9,11,3,11,214,8,11,1,12,1,12,1,
  	12,1,12,5,12,220,8,12,10,12,12,12,223,9,12,1,13,1,13,1,13,1,14,1,14,1,
  	14,1,15,1,15,1,16,1,16,1,17,1,17,1,17,1,17,1,17,5,17,240,8,17,10,17,12,
  	17,243,9,17,3,17,245,8,17,1,18,1,18,1,18,1,18,5,18,251,8,18,10,18,12,
  	18,254,9,18,3,18,256,8,18,1,18,1,18,5,18,260,8,18,10,18,12,18,263,9,18,
  	1,19,1,19,1,19,1,19,1,19,1,20,1,20,1,20,1,20,1,20,1,20,5,20,276,8,20,
  	10,20,12,20,279,9,20,1,20,1,20,3,20,283,8,20,1,20,1,20,1,20,1,20,1,20,
  	3,20,290,8,20,1,21,1,21,1,22,1,22,1,23,1,23,1,23,5,23,299,8,23,10,23,
  	12,23,302,9,23,1,24,1,24,1,24,5,24,307,8,24,10,24,12,24,310,9,24,1,25,
  	1,25,1,25,5,25,315,8,25,10,25,12,25,318,9,25,1,26,1,26,1,26,5,26,323,
  	8,26,10,26,12,26,326,9,26,1,27,1,27,1,27,1,27,1,27,1,27,1,27,1,27,1,27,
  	1,27,5,27,338,8,27,10,27,12,27,341,9,27,1,27,1,27,3,27,345,8,27,1,27,
  	3,27,348,8,27,1,27,0,0,28,0,2,4,6,8,10,12,14,16,18,20,22,24,26,28,30,
  	32,34,36,38,40,42,44,46,48,50,52,54,0,3,1,0,40,41,1,0,33,34,1,0,35,36,
  	370,0,65,1,0,0,0,2,70,1,0,0,0,4,93,1,0,0,0,6,111,1,0,0,0,8,113,1,0,0,
  	0,10,125,1,0,0,0,12,138,1,0,0,0,14,140,1,0,0,0,16,149,1,0,0,0,18,165,
  	1,0,0,0,20,168,1,0,0,0,22,171,1,0,0,0,24,215,1,0,0,0,26,224,1,0,0,0,28,
  	227,1,0,0,0,30,230,1,0,0,0,32,232,1,0,0,0,34,234,1,0,0,0,36,246,1,0,0,
  	0,38,264,1,0,0,0,40,269,1,0,0,0,42,291,1,0,0,0,44,293,1,0,0,0,46,295,
  	1,0,0,0,48,303,1,0,0,0,50,311,1,0,0,0,52,319,1,0,0,0,54,347,1,0,0,0,56,
  	64,3,2,1,0,57,64,3,40,20,0,58,64,3,14,7,0,59,64,3,22,11,0,60,64,3,10,
  	5,0,61,64,3,36,18,0,62,64,3,16,8,0,63,56,1,0,0,0,63,57,1,0,0,0,63,58,
  	1,0,0,0,63,59,1,0,0,0,63,60,1,0,0,0,63,61,1,0,0,0,63,62,1,0,0,0,64,67,
  	1,0,0,0,65,63,1,0,0,0,65,66,1,0,0,0,66,68,1,0,0,0,67,65,1,0,0,0,68,69,
  	5,0,0,1,69,1,1,0,0,0,70,71,5,1,0,0,71,73,5,39,0,0,72,74,5,2,0,0,73,72,
  	1,0,0,0,73,74,1,0,0,0,74,77,1,0,0,0,75,76,5,3,0,0,76,78,5,39,0,0,77,75,
  	1,0,0,0,77,78,1,0,0,0,78,81,1,0,0,0,79,80,5,4,0,0,80,82,3,6,3,0,81,79,
  	1,0,0,0,81,82,1,0,0,0,82,85,1,0,0,0,83,84,5,5,0,0,84,86,5,39,0,0,85,83,
  	1,0,0,0,85,86,1,0,0,0,86,90,1,0,0,0,87,89,3,4,2,0,88,87,1,0,0,0,89,92,
  	1,0,0,0,90,88,1,0,0,0,90,91,1,0,0,0,91,3,1,0,0,0,92,90,1,0,0,0,93,94,
  	5,39,0,0,94,99,5,6,0,0,95,96,5,7,0,0,96,97,5,8,0,0,97,98,5,39,0,0,98,
  	100,5,9,0,0,99,95,1,0,0,0,99,100,1,0,0,0,100,101,1,0,0,0,101,104,5,39,
  	0,0,102,103,5,4,0,0,103,105,3,6,3,0,104,102,1,0,0,0,104,105,1,0,0,0,105,
  	109,1,0,0,0,106,107,5,8,0,0,107,108,5,39,0,0,108,110,5,9,0,0,109,106,
  	1,0,0,0,109,110,1,0,0,0,110,5,1,0,0,0,111,112,7,0,0,0,112,7,1,0,0,0,113,
  	114,5,39,0,0,114,115,5,6,0,0,115,118,5,39,0,0,116,117,5,4,0,0,117,119,
  	3,6,3,0,118,116,1,0,0,0,118,119,1,0,0,0,119,123,1,0,0,0,120,121,5,8,0,
  	0,121,122,5,39,0,0,122,124,5,9,0,0,123,120,1,0,0,0,123,124,1,0,0,0,124,
  	9,1,0,0,0,125,126,5,10,0,0,126,129,5,39,0,0,127,128,5,11,0,0,128,130,
  	5,39,0,0,129,127,1,0,0,0,129,130,1,0,0,0,130,135,1,0,0,0,131,132,5,12,
  	0,0,132,134,3,12,6,0,133,131,1,0,0,0,134,137,1,0,0,0,135,133,1,0,0,0,
  	135,136,1,0,0,0,136,11,1,0,0,0,137,135,1,0,0,0,138,139,3,8,4,0,139,13,
  	1,0,0,0,140,141,5,13,0,0,141,142,5,39,0,0,142,147,5,6,0,0,143,144,5,8,
  	0,0,144,145,5,42,0,0,145,148,5,9,0,0,146,148,5,39,0,0,147,143,1,0,0,0,
  	147,146,1,0,0,0,148,15,1,0,0,0,149,150,5,14,0,0,150,151,5,39,0,0,151,
  	152,5,15,0,0,152,156,5,42,0,0,153,155,3,18,9,0,154,153,1,0,0,0,155,158,
  	1,0,0,0,156,154,1,0,0,0,156,157,1,0,0,0,157,162,1,0,0,0,158,156,1,0,0,
  	0,159,161,3,20,10,0,160,159,1,0,0,0,161,164,1,0,0,0,162,160,1,0,0,0,162,
  	163,1,0,0,0,163,17,1,0,0,0,164,162,1,0,0,0,165,166,5,16,0,0,166,167,3,
  	8,4,0,167,19,1,0,0,0,168,169,5,17,0,0,169,170,3,8,4,0,170,21,1,0,0,0,
  	171,172,5,18,0,0,172,174,5,39,0,0,173,175,3,24,12,0,174,173,1,0,0,0,174,
  	175,1,0,0,0,175,179,1,0,0,0,176,178,3,26,13,0,177,176,1,0,0,0,178,181,
  	1,0,0,0,179,177,1,0,0,0,179,180,1,0,0,0,180,185,1,0,0,0,181,179,1,0,0,
  	0,182,184,3,28,14,0,183,182,1,0,0,0,184,187,1,0,0,0,185,183,1,0,0,0,185,
  	186,1,0,0,0,186,195,1,0,0,0,187,185,1,0,0,0,188,192,5,19,0,0,189,191,
  	3,30,15,0,190,189,1,0,0,0,191,194,1,0,0,0,192,190,1,0,0,0,192,193,1,0,
  	0,0,193,196,1,0,0,0,194,192,1,0,0,0,195,188,1,0,0,0,195,196,1,0,0,0,196,
  	204,1,0,0,0,197,201,5,20,0,0,198,200,3,32,16,0,199,198,1,0,0,0,200,203,
  	1,0,0,0,201,199,1,0,0,0,201,202,1,0,0,0,202,205,1,0,0,0,203,201,1,0,0,
  	0,204,197,1,0,0,0,204,205,1,0,0,0,205,213,1,0,0,0,206,210,5,21,0,0,207,
  	209,3,38,19,0,208,207,1,0,0,0,209,212,1,0,0,0,210,208,1,0,0,0,210,211,
  	1,0,0,0,211,214,1,0,0,0,212,210,1,0,0,0,213,206,1,0,0,0,213,214,1,0,0,
  	0,214,23,1,0,0,0,215,216,5,22,0,0,216,221,5,39,0,0,217,218,5,23,0,0,218,
  	220,5,39,0,0,219,217,1,0,0,0,220,223,1,0,0,0,221,219,1,0,0,0,221,222,
  	1,0,0,0,222,25,1,0,0,0,223,221,1,0,0,0,224,225,5,16,0,0,225,226,3,8,4,
  	0,226,27,1,0,0,0,227,228,5,17,0,0,228,229,3,8,4,0,229,29,1,0,0,0,230,
  	231,5,39,0,0,231,31,1,0,0,0,232,233,5,39,0,0,233,33,1,0,0,0,234,235,5,
  	39,0,0,235,236,5,6,0,0,236,244,5,39,0,0,237,241,5,24,0,0,238,240,5,39,
  	0,0,239,238,1,0,0,0,240,243,1,0,0,0,241,239,1,0,0,0,241,242,1,0,0,0,242,
  	245,1,0,0,0,243,241,1,0,0,0,244,237,1,0,0,0,244,245,1,0,0,0,245,35,1,
  	0,0,0,246,247,5,25,0,0,247,255,5,39,0,0,248,252,5,24,0,0,249,251,5,39,
  	0,0,250,249,1,0,0,0,251,254,1,0,0,0,252,250,1,0,0,0,252,253,1,0,0,0,253,
  	256,1,0,0,0,254,252,1,0,0,0,255,248,1,0,0,0,255,256,1,0,0,0,256,261,1,
  	0,0,0,257,258,5,26,0,0,258,260,3,34,17,0,259,257,1,0,0,0,260,263,1,0,
  	0,0,261,259,1,0,0,0,261,262,1,0,0,0,262,37,1,0,0,0,263,261,1,0,0,0,264,
  	265,5,39,0,0,265,266,5,27,0,0,266,267,3,44,22,0,267,268,5,28,0,0,268,
  	39,1,0,0,0,269,270,5,29,0,0,270,282,5,39,0,0,271,272,5,30,0,0,272,277,
  	3,42,21,0,273,274,5,31,0,0,274,276,3,42,21,0,275,273,1,0,0,0,276,279,
  	1,0,0,0,277,275,1,0,0,0,277,278,1,0,0,0,278,280,1,0,0,0,279,277,1,0,0,
  	0,280,281,5,32,0,0,281,283,1,0,0,0,282,271,1,0,0,0,282,283,1,0,0,0,283,
  	284,1,0,0,0,284,289,5,6,0,0,285,290,5,2,0,0,286,287,3,44,22,0,287,288,
  	5,28,0,0,288,290,1,0,0,0,289,285,1,0,0,0,289,286,1,0,0,0,290,41,1,0,0,
  	0,291,292,5,39,0,0,292,43,1,0,0,0,293,294,3,46,23,0,294,45,1,0,0,0,295,
  	300,3,48,24,0,296,297,7,1,0,0,297,299,3,48,24,0,298,296,1,0,0,0,299,302,
  	1,0,0,0,300,298,1,0,0,0,300,301,1,0,0,0,301,47,1,0,0,0,302,300,1,0,0,
  	0,303,308,3,50,25,0,304,305,7,2,0,0,305,307,3,50,25,0,306,304,1,0,0,0,
  	307,310,1,0,0,0,308,306,1,0,0,0,308,309,1,0,0,0,309,49,1,0,0,0,310,308,
  	1,0,0,0,311,316,3,52,26,0,312,313,5,37,0,0,313,315,3,52,26,0,314,312,
  	1,0,0,0,315,318,1,0,0,0,316,314,1,0,0,0,316,317,1,0,0,0,317,51,1,0,0,
  	0,318,316,1,0,0,0,319,324,3,54,27,0,320,321,5,38,0,0,321,323,3,54,27,
  	0,322,320,1,0,0,0,323,326,1,0,0,0,324,322,1,0,0,0,324,325,1,0,0,0,325,
  	53,1,0,0,0,326,324,1,0,0,0,327,328,5,30,0,0,328,329,3,44,22,0,329,330,
  	5,32,0,0,330,348,1,0,0,0,331,348,5,40,0,0,332,344,5,39,0,0,333,334,5,
  	30,0,0,334,339,3,44,22,0,335,336,5,31,0,0,336,338,3,44,22,0,337,335,1,
  	0,0,0,338,341,1,0,0,0,339,337,1,0,0,0,339,340,1,0,0,0,340,342,1,0,0,0,
  	341,339,1,0,0,0,342,343,5,32,0,0,343,345,1,0,0,0,344,333,1,0,0,0,344,
  	345,1,0,0,0,345,348,1,0,0,0,346,348,5,39,0,0,347,327,1,0,0,0,347,331,
  	1,0,0,0,347,332,1,0,0,0,347,346,1,0,0,0,348,55,1,0,0,0,42,63,65,73,77,
  	81,85,90,99,104,109,118,123,129,135,147,156,162,174,179,185,192,195,201,
  	204,210,213,221,241,244,252,255,261,277,282,289,300,308,316,324,339,344,
  	347
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

std::vector<pblangParser::TypeDefContext *> pblangParser::ModelContext::typeDef() {
  return getRuleContexts<pblangParser::TypeDefContext>();
}

pblangParser::TypeDefContext* pblangParser::ModelContext::typeDef(size_t i) {
  return getRuleContext<pblangParser::TypeDefContext>(i);
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
    setState(65);
    _errHandler->sync(this);
    _la = _input->LA(1);
    while ((((_la & ~ 0x3fULL) == 0) &&
      ((1ULL << _la) & 570713090) != 0)) {
      setState(63);
      _errHandler->sync(this);
      switch (_input->LA(1)) {
        case pblangParser::T__0: {
          setState(56);
          typeDef();
          break;
        }

        case pblangParser::T__28: {
          setState(57);
          definition();
          break;
        }

        case pblangParser::T__12: {
          setState(58);
          unit();
          break;
        }

        case pblangParser::T__17: {
          setState(59);
          processDef();
          break;
        }

        case pblangParser::T__9: {
          setState(60);
          store();
          break;
        }

        case pblangParser::T__24: {
          setState(61);
          compositeDef();
          break;
        }

        case pblangParser::T__13: {
          setState(62);
          sbmlModel();
          break;
        }

      default:
        throw NoViableAltException(this);
      }
      setState(67);
      _errHandler->sync(this);
      _la = _input->LA(1);
    }
    setState(68);
    match(pblangParser::EOF);

  }
  catch (RecognitionException &e) {
    _errHandler->reportError(this, e);
    _localctx->exception = std::current_exception();
    _errHandler->recover(this, _localctx->exception);
  }

  return _localctx;
}

//----------------- TypeDefContext ------------------------------------------------------------------

pblangParser::TypeDefContext::TypeDefContext(ParserRuleContext *parent, size_t invokingState)
  : ParserRuleContext(parent, invokingState) {
}

std::vector<tree::TerminalNode *> pblangParser::TypeDefContext::ID() {
  return getTokens(pblangParser::ID);
}

tree::TerminalNode* pblangParser::TypeDefContext::ID(size_t i) {
  return getToken(pblangParser::ID, i);
}

pblangParser::DefaultValueContext* pblangParser::TypeDefContext::defaultValue() {
  return getRuleContext<pblangParser::DefaultValueContext>(0);
}

std::vector<pblangParser::NamedTypeContext *> pblangParser::TypeDefContext::namedType() {
  return getRuleContexts<pblangParser::NamedTypeContext>();
}

pblangParser::NamedTypeContext* pblangParser::TypeDefContext::namedType(size_t i) {
  return getRuleContext<pblangParser::NamedTypeContext>(i);
}


size_t pblangParser::TypeDefContext::getRuleIndex() const {
  return pblangParser::RuleTypeDef;
}

void pblangParser::TypeDefContext::enterRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<pblangListener *>(listener);
  if (parserListener != nullptr)
    parserListener->enterTypeDef(this);
}

void pblangParser::TypeDefContext::exitRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<pblangListener *>(listener);
  if (parserListener != nullptr)
    parserListener->exitTypeDef(this);
}

pblangParser::TypeDefContext* pblangParser::typeDef() {
  TypeDefContext *_localctx = _tracker.createInstance<TypeDefContext>(_ctx, getState());
  enterRule(_localctx, 2, pblangParser::RuleTypeDef);
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
    setState(70);
    match(pblangParser::T__0);
    setState(71);
    antlrcpp::downCast<TypeDefContext *>(_localctx)->name = match(pblangParser::ID);
    setState(73);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__1) {
      setState(72);
      antlrcpp::downCast<TypeDefContext *>(_localctx)->builtin = match(pblangParser::T__1);
    }
    setState(77);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__2) {
      setState(75);
      match(pblangParser::T__2);
      setState(76);
      match(pblangParser::ID);
    }
    setState(81);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__3) {
      setState(79);
      match(pblangParser::T__3);
      setState(80);
      defaultValue();
    }
    setState(85);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__4) {
      setState(83);
      match(pblangParser::T__4);
      setState(84);
      match(pblangParser::ID);
    }
    setState(90);
    _errHandler->sync(this);
    _la = _input->LA(1);
    while (_la == pblangParser::ID) {
      setState(87);
      namedType();
      setState(92);
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
    setState(93);
    antlrcpp::downCast<NamedTypeContext *>(_localctx)->name = match(pblangParser::ID);
    setState(94);
    match(pblangParser::T__5);
    setState(99);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__6) {
      setState(95);
      match(pblangParser::T__6);
      setState(96);
      match(pblangParser::T__7);
      setState(97);
      antlrcpp::downCast<NamedTypeContext *>(_localctx)->optional_type_ref = match(pblangParser::ID);
      setState(98);
      match(pblangParser::T__8);
    }
    setState(101);
    antlrcpp::downCast<NamedTypeContext *>(_localctx)->type_ref = match(pblangParser::ID);
    setState(104);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__3) {
      setState(102);
      match(pblangParser::T__3);
      setState(103);
      defaultValue();
    }
    setState(109);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__7) {
      setState(106);
      match(pblangParser::T__7);
      setState(107);
      antlrcpp::downCast<NamedTypeContext *>(_localctx)->unit_ref = match(pblangParser::ID);
      setState(108);
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
    setState(111);
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
    setState(113);
    antlrcpp::downCast<SchemaItemContext *>(_localctx)->name = match(pblangParser::ID);
    setState(114);
    match(pblangParser::T__5);
    setState(115);
    antlrcpp::downCast<SchemaItemContext *>(_localctx)->type_ref = match(pblangParser::ID);
    setState(118);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__3) {
      setState(116);
      match(pblangParser::T__3);
      setState(117);
      defaultValue();
    }
    setState(123);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__7) {
      setState(120);
      match(pblangParser::T__7);
      setState(121);
      antlrcpp::downCast<SchemaItemContext *>(_localctx)->unit_ref = match(pblangParser::ID);
      setState(122);
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
    setState(125);
    match(pblangParser::T__9);
    setState(126);
    match(pblangParser::ID);
    setState(129);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__10) {
      setState(127);
      match(pblangParser::T__10);
      setState(128);
      match(pblangParser::ID);
    }
    setState(135);
    _errHandler->sync(this);
    _la = _input->LA(1);
    while (_la == pblangParser::T__11) {
      setState(131);
      match(pblangParser::T__11);
      setState(132);
      storeState();
      setState(137);
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
    setState(138);
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
    setState(140);
    match(pblangParser::T__12);
    setState(141);
    match(pblangParser::ID);
    setState(142);
    match(pblangParser::T__5);
    setState(147);
    _errHandler->sync(this);
    switch (_input->LA(1)) {
      case pblangParser::T__7: {
        setState(143);
        match(pblangParser::T__7);
        setState(144);
        match(pblangParser::STRING);
        setState(145);
        match(pblangParser::T__8);
        break;
      }

      case pblangParser::ID: {
        setState(146);
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
    setState(149);
    match(pblangParser::T__13);
    setState(150);
    match(pblangParser::ID);
    setState(151);
    match(pblangParser::T__14);
    setState(152);
    match(pblangParser::STRING);
    setState(156);
    _errHandler->sync(this);
    _la = _input->LA(1);
    while (_la == pblangParser::T__15) {
      setState(153);
      sbmlParameter();
      setState(158);
      _errHandler->sync(this);
      _la = _input->LA(1);
    }
    setState(162);
    _errHandler->sync(this);
    _la = _input->LA(1);
    while (_la == pblangParser::T__16) {
      setState(159);
      sbmlVariable();
      setState(164);
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
    setState(165);
    match(pblangParser::T__15);
    setState(166);
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
    setState(168);
    match(pblangParser::T__16);
    setState(169);
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

pblangParser::PythonRefContext* pblangParser::ProcessDefContext::pythonRef() {
  return getRuleContext<pblangParser::PythonRefContext>(0);
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
    setState(171);
    match(pblangParser::T__17);
    setState(172);
    match(pblangParser::ID);
    setState(174);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__21) {
      setState(173);
      pythonRef();
    }
    setState(179);
    _errHandler->sync(this);
    _la = _input->LA(1);
    while (_la == pblangParser::T__15) {
      setState(176);
      processParameter();
      setState(181);
      _errHandler->sync(this);
      _la = _input->LA(1);
    }
    setState(185);
    _errHandler->sync(this);
    _la = _input->LA(1);
    while (_la == pblangParser::T__16) {
      setState(182);
      processVariable();
      setState(187);
      _errHandler->sync(this);
      _la = _input->LA(1);
    }
    setState(195);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__18) {
      setState(188);
      match(pblangParser::T__18);
      setState(192);
      _errHandler->sync(this);
      _la = _input->LA(1);
      while (_la == pblangParser::ID) {
        setState(189);
        processInput();
        setState(194);
        _errHandler->sync(this);
        _la = _input->LA(1);
      }
    }
    setState(204);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__19) {
      setState(197);
      match(pblangParser::T__19);
      setState(201);
      _errHandler->sync(this);
      _la = _input->LA(1);
      while (_la == pblangParser::ID) {
        setState(198);
        processOutput();
        setState(203);
        _errHandler->sync(this);
        _la = _input->LA(1);
      }
    }
    setState(213);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__20) {
      setState(206);
      match(pblangParser::T__20);
      setState(210);
      _errHandler->sync(this);
      _la = _input->LA(1);
      while (_la == pblangParser::ID) {
        setState(207);
        update();
        setState(212);
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

//----------------- PythonRefContext ------------------------------------------------------------------

pblangParser::PythonRefContext::PythonRefContext(ParserRuleContext *parent, size_t invokingState)
  : ParserRuleContext(parent, invokingState) {
}

std::vector<tree::TerminalNode *> pblangParser::PythonRefContext::ID() {
  return getTokens(pblangParser::ID);
}

tree::TerminalNode* pblangParser::PythonRefContext::ID(size_t i) {
  return getToken(pblangParser::ID, i);
}


size_t pblangParser::PythonRefContext::getRuleIndex() const {
  return pblangParser::RulePythonRef;
}

void pblangParser::PythonRefContext::enterRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<pblangListener *>(listener);
  if (parserListener != nullptr)
    parserListener->enterPythonRef(this);
}

void pblangParser::PythonRefContext::exitRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<pblangListener *>(listener);
  if (parserListener != nullptr)
    parserListener->exitPythonRef(this);
}

pblangParser::PythonRefContext* pblangParser::pythonRef() {
  PythonRefContext *_localctx = _tracker.createInstance<PythonRefContext>(_ctx, getState());
  enterRule(_localctx, 24, pblangParser::RulePythonRef);
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
    setState(215);
    match(pblangParser::T__21);
    setState(216);
    match(pblangParser::ID);
    setState(221);
    _errHandler->sync(this);
    _la = _input->LA(1);
    while (_la == pblangParser::T__22) {
      setState(217);
      match(pblangParser::T__22);
      setState(218);
      match(pblangParser::ID);
      setState(223);
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
  enterRule(_localctx, 26, pblangParser::RuleProcessParameter);

#if __cplusplus > 201703L
  auto onExit = finally([=, this] {
#else
  auto onExit = finally([=] {
#endif
    exitRule();
  });
  try {
    enterOuterAlt(_localctx, 1);
    setState(224);
    match(pblangParser::T__15);
    setState(225);
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
  enterRule(_localctx, 28, pblangParser::RuleProcessVariable);

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
    match(pblangParser::T__16);
    setState(228);
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
  enterRule(_localctx, 30, pblangParser::RuleProcessInput);

#if __cplusplus > 201703L
  auto onExit = finally([=, this] {
#else
  auto onExit = finally([=] {
#endif
    exitRule();
  });
  try {
    enterOuterAlt(_localctx, 1);
    setState(230);
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
  enterRule(_localctx, 32, pblangParser::RuleProcessOutput);

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
  enterRule(_localctx, 34, pblangParser::RuleProcess);
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
    setState(234);
    antlrcpp::downCast<ProcessContext *>(_localctx)->name = match(pblangParser::ID);
    setState(235);
    match(pblangParser::T__5);
    setState(236);
    antlrcpp::downCast<ProcessContext *>(_localctx)->process_def_ref = match(pblangParser::ID);
    setState(244);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__23) {
      setState(237);
      match(pblangParser::T__23);
      setState(241);
      _errHandler->sync(this);
      _la = _input->LA(1);
      while (_la == pblangParser::ID) {
        setState(238);
        antlrcpp::downCast<ProcessContext *>(_localctx)->store_def = match(pblangParser::ID);
        setState(243);
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
  enterRule(_localctx, 36, pblangParser::RuleCompositeDef);
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
    setState(246);
    match(pblangParser::T__24);
    setState(247);
    match(pblangParser::ID);
    setState(255);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__23) {
      setState(248);
      match(pblangParser::T__23);
      setState(252);
      _errHandler->sync(this);
      _la = _input->LA(1);
      while (_la == pblangParser::ID) {
        setState(249);
        match(pblangParser::ID);
        setState(254);
        _errHandler->sync(this);
        _la = _input->LA(1);
      }
    }
    setState(261);
    _errHandler->sync(this);
    _la = _input->LA(1);
    while (_la == pblangParser::T__25) {
      setState(257);
      match(pblangParser::T__25);
      setState(258);
      process();
      setState(263);
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

pblangParser::ExpressionContext* pblangParser::UpdateContext::expression() {
  return getRuleContext<pblangParser::ExpressionContext>(0);
}

tree::TerminalNode* pblangParser::UpdateContext::ID() {
  return getToken(pblangParser::ID, 0);
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
  enterRule(_localctx, 38, pblangParser::RuleUpdate);

#if __cplusplus > 201703L
  auto onExit = finally([=, this] {
#else
  auto onExit = finally([=] {
#endif
    exitRule();
  });
  try {
    enterOuterAlt(_localctx, 1);
    setState(264);
    antlrcpp::downCast<UpdateContext *>(_localctx)->lhs = match(pblangParser::ID);
    setState(265);
    match(pblangParser::T__26);
    setState(266);
    expression();
    setState(267);
    match(pblangParser::T__27);

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
  enterRule(_localctx, 40, pblangParser::RuleDefinition);
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
    match(pblangParser::T__28);
    setState(270);
    match(pblangParser::ID);
    setState(282);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__29) {
      setState(271);
      match(pblangParser::T__29);
      setState(272);
      declaredParameter();
      setState(277);
      _errHandler->sync(this);
      _la = _input->LA(1);
      while (_la == pblangParser::T__30) {
        setState(273);
        match(pblangParser::T__30);
        setState(274);
        declaredParameter();
        setState(279);
        _errHandler->sync(this);
        _la = _input->LA(1);
      }
      setState(280);
      match(pblangParser::T__31);
    }
    setState(284);
    match(pblangParser::T__5);
    setState(289);
    _errHandler->sync(this);
    switch (_input->LA(1)) {
      case pblangParser::T__1: {
        setState(285);
        antlrcpp::downCast<DefinitionContext *>(_localctx)->builtin = match(pblangParser::T__1);
        break;
      }

      case pblangParser::T__29:
      case pblangParser::ID:
      case pblangParser::FLOAT: {
        setState(286);
        expression();
        setState(287);
        match(pblangParser::T__27);
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
  enterRule(_localctx, 42, pblangParser::RuleDeclaredParameter);

#if __cplusplus > 201703L
  auto onExit = finally([=, this] {
#else
  auto onExit = finally([=] {
#endif
    exitRule();
  });
  try {
    enterOuterAlt(_localctx, 1);
    setState(291);
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
  enterRule(_localctx, 44, pblangParser::RuleExpression);

#if __cplusplus > 201703L
  auto onExit = finally([=, this] {
#else
  auto onExit = finally([=] {
#endif
    exitRule();
  });
  try {
    enterOuterAlt(_localctx, 1);
    setState(293);
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
  enterRule(_localctx, 46, pblangParser::RuleAddition);
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
    setState(295);
    multiplication();
    setState(300);
    _errHandler->sync(this);
    _la = _input->LA(1);
    while (_la == pblangParser::T__32

    || _la == pblangParser::T__33) {
      setState(296);
      _la = _input->LA(1);
      if (!(_la == pblangParser::T__32

      || _la == pblangParser::T__33)) {
      _errHandler->recoverInline(this);
      }
      else {
        _errHandler->reportMatch(this);
        consume();
      }
      setState(297);
      multiplication();
      setState(302);
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
  enterRule(_localctx, 48, pblangParser::RuleMultiplication);
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
    setState(303);
    exponentiation();
    setState(308);
    _errHandler->sync(this);
    _la = _input->LA(1);
    while (_la == pblangParser::T__34

    || _la == pblangParser::T__35) {
      setState(304);
      _la = _input->LA(1);
      if (!(_la == pblangParser::T__34

      || _la == pblangParser::T__35)) {
      _errHandler->recoverInline(this);
      }
      else {
        _errHandler->reportMatch(this);
        consume();
      }
      setState(305);
      exponentiation();
      setState(310);
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
  enterRule(_localctx, 50, pblangParser::RuleExponentiation);
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
    setState(311);
    modulo();
    setState(316);
    _errHandler->sync(this);
    _la = _input->LA(1);
    while (_la == pblangParser::T__36) {
      setState(312);
      match(pblangParser::T__36);
      setState(313);
      modulo();
      setState(318);
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
  enterRule(_localctx, 52, pblangParser::RuleModulo);
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
    setState(319);
    primaryExpression();
    setState(324);
    _errHandler->sync(this);
    _la = _input->LA(1);
    while (_la == pblangParser::T__37) {
      setState(320);
      match(pblangParser::T__37);
      setState(321);
      primaryExpression();
      setState(326);
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
  enterRule(_localctx, 54, pblangParser::RulePrimaryExpression);
  size_t _la = 0;

#if __cplusplus > 201703L
  auto onExit = finally([=, this] {
#else
  auto onExit = finally([=] {
#endif
    exitRule();
  });
  try {
    setState(347);
    _errHandler->sync(this);
    switch (getInterpreter<atn::ParserATNSimulator>()->adaptivePredict(_input, 41, _ctx)) {
    case 1: {
      enterOuterAlt(_localctx, 1);
      setState(327);
      match(pblangParser::T__29);
      setState(328);
      expression();
      setState(329);
      match(pblangParser::T__31);
      break;
    }

    case 2: {
      enterOuterAlt(_localctx, 2);
      setState(331);
      match(pblangParser::FLOAT);
      break;
    }

    case 3: {
      enterOuterAlt(_localctx, 3);
      setState(332);
      match(pblangParser::ID);
      setState(344);
      _errHandler->sync(this);

      _la = _input->LA(1);
      if (_la == pblangParser::T__29) {
        setState(333);
        match(pblangParser::T__29);
        setState(334);
        expression();
        setState(339);
        _errHandler->sync(this);
        _la = _input->LA(1);
        while (_la == pblangParser::T__30) {
          setState(335);
          match(pblangParser::T__30);
          setState(336);
          expression();
          setState(341);
          _errHandler->sync(this);
          _la = _input->LA(1);
        }
        setState(342);
        match(pblangParser::T__31);
      }
      break;
    }

    case 4: {
      enterOuterAlt(_localctx, 4);
      setState(346);
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
