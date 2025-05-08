
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
      "model", "typeDef", "namedType", "defaultValue", "schemaItem", "storeDefRef",
      "storeDef", "storeDefStateDef", "unit", "sbmlModel", "sbmlParameter",
      "sbmlVariable", "processDef", "pythonPath", "processParameter", "processVariable",
      "processInput", "processOutput", "process", "store", "compositeDef",
      "update", "definition", "declaredParameter", "expression", "addition",
      "multiplication", "exponentiation", "modulo", "primaryExpression"
    },
    std::vector<std::string>{
      "", "'type'", "'builtin'", "'extends'", "'default'", "'update'", "':'",
      "'maybe'", "'['", "']'", "'store_def'", "'parent'", "'state_def'",
      "'unit'", "'sbml'", "'file'", "'param'", "'var'", "'process_def'",
      "'inputs'", "'outputs'", "'updates'", "'path'", "'.'", "'process'",
      "'stores'", "'store'", "'composite_def'", "':='", "';'", "'def'",
      "'('", "','", "')'", "'+'", "'-'", "'*'", "'/'", "'^'", "'%'"
    },
    std::vector<std::string>{
      "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
      "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
      "", "", "", "", "", "", "ID", "FLOAT", "INT", "STRING", "WS", "ML_COMMENT",
      "SL_COMMENT"
    }
  );
  static const int32_t serializedATNSegment[] = {
  	4,1,46,362,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,6,2,
  	7,7,7,2,8,7,8,2,9,7,9,2,10,7,10,2,11,7,11,2,12,7,12,2,13,7,13,2,14,7,
  	14,2,15,7,15,2,16,7,16,2,17,7,17,2,18,7,18,2,19,7,19,2,20,7,20,2,21,7,
  	21,2,22,7,22,2,23,7,23,2,24,7,24,2,25,7,25,2,26,7,26,2,27,7,27,2,28,7,
  	28,2,29,7,29,1,0,1,0,1,0,1,0,1,0,1,0,1,0,5,0,68,8,0,10,0,12,0,71,9,0,
  	1,0,1,0,1,1,1,1,1,1,3,1,78,8,1,1,1,1,1,3,1,82,8,1,1,1,1,1,3,1,86,8,1,
  	1,1,1,1,3,1,90,8,1,1,1,5,1,93,8,1,10,1,12,1,96,9,1,1,2,1,2,1,2,1,2,1,
  	2,1,2,3,2,104,8,2,1,2,1,2,1,2,3,2,109,8,2,1,2,1,2,1,2,3,2,114,8,2,1,3,
  	1,3,1,4,1,4,1,4,1,4,1,4,3,4,123,8,4,1,4,1,4,1,4,3,4,128,8,4,1,5,1,5,1,
  	6,1,6,1,6,1,6,3,6,136,8,6,1,6,1,6,5,6,140,8,6,10,6,12,6,143,9,6,1,7,1,
  	7,1,8,1,8,1,8,1,8,1,8,1,8,1,8,3,8,154,8,8,1,9,1,9,1,9,1,9,1,9,5,9,161,
  	8,9,10,9,12,9,164,9,9,1,9,5,9,167,8,9,10,9,12,9,170,9,9,1,10,1,10,1,10,
  	1,11,1,11,1,11,1,12,1,12,1,12,3,12,181,8,12,1,12,5,12,184,8,12,10,12,
  	12,12,187,9,12,1,12,5,12,190,8,12,10,12,12,12,193,9,12,1,12,1,12,5,12,
  	197,8,12,10,12,12,12,200,9,12,3,12,202,8,12,1,12,1,12,5,12,206,8,12,10,
  	12,12,12,209,9,12,3,12,211,8,12,1,12,1,12,5,12,215,8,12,10,12,12,12,218,
  	9,12,3,12,220,8,12,1,13,1,13,1,13,1,13,5,13,226,8,13,10,13,12,13,229,
  	9,13,1,14,1,14,1,14,1,15,1,15,1,15,1,16,1,16,1,17,1,17,1,18,1,18,1,18,
  	1,18,1,18,1,18,5,18,247,8,18,10,18,12,18,250,9,18,3,18,252,8,18,1,19,
  	1,19,1,19,1,19,5,19,258,8,19,10,19,12,19,261,9,19,1,20,1,20,1,20,5,20,
  	266,8,20,10,20,12,20,269,9,20,1,20,5,20,272,8,20,10,20,12,20,275,9,20,
  	1,21,1,21,1,21,1,21,1,21,1,22,1,22,1,22,1,22,1,22,1,22,5,22,288,8,22,
  	10,22,12,22,291,9,22,1,22,1,22,3,22,295,8,22,1,22,1,22,1,22,1,22,1,22,
  	3,22,302,8,22,1,23,1,23,1,24,1,24,1,25,1,25,1,25,5,25,311,8,25,10,25,
  	12,25,314,9,25,1,26,1,26,1,26,5,26,319,8,26,10,26,12,26,322,9,26,1,27,
  	1,27,1,27,5,27,327,8,27,10,27,12,27,330,9,27,1,28,1,28,1,28,5,28,335,
  	8,28,10,28,12,28,338,9,28,1,29,1,29,1,29,1,29,1,29,1,29,1,29,1,29,1,29,
  	1,29,5,29,350,8,29,10,29,12,29,353,9,29,1,29,1,29,3,29,357,8,29,1,29,
  	3,29,360,8,29,1,29,0,0,30,0,2,4,6,8,10,12,14,16,18,20,22,24,26,28,30,
  	32,34,36,38,40,42,44,46,48,50,52,54,56,58,0,3,1,0,41,42,1,0,34,35,1,0,
  	36,37,380,0,69,1,0,0,0,2,74,1,0,0,0,4,97,1,0,0,0,6,115,1,0,0,0,8,117,
  	1,0,0,0,10,129,1,0,0,0,12,131,1,0,0,0,14,144,1,0,0,0,16,146,1,0,0,0,18,
  	155,1,0,0,0,20,171,1,0,0,0,22,174,1,0,0,0,24,177,1,0,0,0,26,221,1,0,0,
  	0,28,230,1,0,0,0,30,233,1,0,0,0,32,236,1,0,0,0,34,238,1,0,0,0,36,240,
  	1,0,0,0,38,253,1,0,0,0,40,262,1,0,0,0,42,276,1,0,0,0,44,281,1,0,0,0,46,
  	303,1,0,0,0,48,305,1,0,0,0,50,307,1,0,0,0,52,315,1,0,0,0,54,323,1,0,0,
  	0,56,331,1,0,0,0,58,359,1,0,0,0,60,68,3,2,1,0,61,68,3,44,22,0,62,68,3,
  	16,8,0,63,68,3,24,12,0,64,68,3,12,6,0,65,68,3,40,20,0,66,68,3,18,9,0,
  	67,60,1,0,0,0,67,61,1,0,0,0,67,62,1,0,0,0,67,63,1,0,0,0,67,64,1,0,0,0,
  	67,65,1,0,0,0,67,66,1,0,0,0,68,71,1,0,0,0,69,67,1,0,0,0,69,70,1,0,0,0,
  	70,72,1,0,0,0,71,69,1,0,0,0,72,73,5,0,0,1,73,1,1,0,0,0,74,75,5,1,0,0,
  	75,77,5,40,0,0,76,78,5,2,0,0,77,76,1,0,0,0,77,78,1,0,0,0,78,81,1,0,0,
  	0,79,80,5,3,0,0,80,82,5,40,0,0,81,79,1,0,0,0,81,82,1,0,0,0,82,85,1,0,
  	0,0,83,84,5,4,0,0,84,86,3,6,3,0,85,83,1,0,0,0,85,86,1,0,0,0,86,89,1,0,
  	0,0,87,88,5,5,0,0,88,90,5,40,0,0,89,87,1,0,0,0,89,90,1,0,0,0,90,94,1,
  	0,0,0,91,93,3,4,2,0,92,91,1,0,0,0,93,96,1,0,0,0,94,92,1,0,0,0,94,95,1,
  	0,0,0,95,3,1,0,0,0,96,94,1,0,0,0,97,98,5,40,0,0,98,103,5,6,0,0,99,100,
  	5,7,0,0,100,101,5,8,0,0,101,102,5,40,0,0,102,104,5,9,0,0,103,99,1,0,0,
  	0,103,104,1,0,0,0,104,105,1,0,0,0,105,108,5,40,0,0,106,107,5,4,0,0,107,
  	109,3,6,3,0,108,106,1,0,0,0,108,109,1,0,0,0,109,113,1,0,0,0,110,111,5,
  	8,0,0,111,112,5,40,0,0,112,114,5,9,0,0,113,110,1,0,0,0,113,114,1,0,0,
  	0,114,5,1,0,0,0,115,116,7,0,0,0,116,7,1,0,0,0,117,118,5,40,0,0,118,119,
  	5,6,0,0,119,122,5,40,0,0,120,121,5,4,0,0,121,123,3,6,3,0,122,120,1,0,
  	0,0,122,123,1,0,0,0,123,127,1,0,0,0,124,125,5,8,0,0,125,126,5,40,0,0,
  	126,128,5,9,0,0,127,124,1,0,0,0,127,128,1,0,0,0,128,9,1,0,0,0,129,130,
  	5,40,0,0,130,11,1,0,0,0,131,132,5,10,0,0,132,135,5,40,0,0,133,134,5,11,
  	0,0,134,136,3,10,5,0,135,133,1,0,0,0,135,136,1,0,0,0,136,141,1,0,0,0,
  	137,138,5,12,0,0,138,140,3,14,7,0,139,137,1,0,0,0,140,143,1,0,0,0,141,
  	139,1,0,0,0,141,142,1,0,0,0,142,13,1,0,0,0,143,141,1,0,0,0,144,145,3,
  	8,4,0,145,15,1,0,0,0,146,147,5,13,0,0,147,148,5,40,0,0,148,153,5,6,0,
  	0,149,150,5,8,0,0,150,151,5,43,0,0,151,154,5,9,0,0,152,154,5,40,0,0,153,
  	149,1,0,0,0,153,152,1,0,0,0,154,17,1,0,0,0,155,156,5,14,0,0,156,157,5,
  	40,0,0,157,158,5,15,0,0,158,162,5,43,0,0,159,161,3,20,10,0,160,159,1,
  	0,0,0,161,164,1,0,0,0,162,160,1,0,0,0,162,163,1,0,0,0,163,168,1,0,0,0,
  	164,162,1,0,0,0,165,167,3,22,11,0,166,165,1,0,0,0,167,170,1,0,0,0,168,
  	166,1,0,0,0,168,169,1,0,0,0,169,19,1,0,0,0,170,168,1,0,0,0,171,172,5,
  	16,0,0,172,173,3,8,4,0,173,21,1,0,0,0,174,175,5,17,0,0,175,176,3,8,4,
  	0,176,23,1,0,0,0,177,178,5,18,0,0,178,180,5,40,0,0,179,181,3,26,13,0,
  	180,179,1,0,0,0,180,181,1,0,0,0,181,185,1,0,0,0,182,184,3,28,14,0,183,
  	182,1,0,0,0,184,187,1,0,0,0,185,183,1,0,0,0,185,186,1,0,0,0,186,191,1,
  	0,0,0,187,185,1,0,0,0,188,190,3,30,15,0,189,188,1,0,0,0,190,193,1,0,0,
  	0,191,189,1,0,0,0,191,192,1,0,0,0,192,201,1,0,0,0,193,191,1,0,0,0,194,
  	198,5,19,0,0,195,197,3,32,16,0,196,195,1,0,0,0,197,200,1,0,0,0,198,196,
  	1,0,0,0,198,199,1,0,0,0,199,202,1,0,0,0,200,198,1,0,0,0,201,194,1,0,0,
  	0,201,202,1,0,0,0,202,210,1,0,0,0,203,207,5,20,0,0,204,206,3,34,17,0,
  	205,204,1,0,0,0,206,209,1,0,0,0,207,205,1,0,0,0,207,208,1,0,0,0,208,211,
  	1,0,0,0,209,207,1,0,0,0,210,203,1,0,0,0,210,211,1,0,0,0,211,219,1,0,0,
  	0,212,216,5,21,0,0,213,215,3,42,21,0,214,213,1,0,0,0,215,218,1,0,0,0,
  	216,214,1,0,0,0,216,217,1,0,0,0,217,220,1,0,0,0,218,216,1,0,0,0,219,212,
  	1,0,0,0,219,220,1,0,0,0,220,25,1,0,0,0,221,222,5,22,0,0,222,227,5,40,
  	0,0,223,224,5,23,0,0,224,226,5,40,0,0,225,223,1,0,0,0,226,229,1,0,0,0,
  	227,225,1,0,0,0,227,228,1,0,0,0,228,27,1,0,0,0,229,227,1,0,0,0,230,231,
  	5,16,0,0,231,232,3,8,4,0,232,29,1,0,0,0,233,234,5,17,0,0,234,235,3,8,
  	4,0,235,31,1,0,0,0,236,237,5,40,0,0,237,33,1,0,0,0,238,239,5,40,0,0,239,
  	35,1,0,0,0,240,241,5,24,0,0,241,242,5,40,0,0,242,243,5,6,0,0,243,251,
  	5,40,0,0,244,248,5,25,0,0,245,247,3,10,5,0,246,245,1,0,0,0,247,250,1,
  	0,0,0,248,246,1,0,0,0,248,249,1,0,0,0,249,252,1,0,0,0,250,248,1,0,0,0,
  	251,244,1,0,0,0,251,252,1,0,0,0,252,37,1,0,0,0,253,254,5,26,0,0,254,255,
  	5,40,0,0,255,259,5,6,0,0,256,258,5,40,0,0,257,256,1,0,0,0,258,261,1,0,
  	0,0,259,257,1,0,0,0,259,260,1,0,0,0,260,39,1,0,0,0,261,259,1,0,0,0,262,
  	263,5,27,0,0,263,267,5,40,0,0,264,266,3,38,19,0,265,264,1,0,0,0,266,269,
  	1,0,0,0,267,265,1,0,0,0,267,268,1,0,0,0,268,273,1,0,0,0,269,267,1,0,0,
  	0,270,272,3,36,18,0,271,270,1,0,0,0,272,275,1,0,0,0,273,271,1,0,0,0,273,
  	274,1,0,0,0,274,41,1,0,0,0,275,273,1,0,0,0,276,277,5,40,0,0,277,278,5,
  	28,0,0,278,279,3,48,24,0,279,280,5,29,0,0,280,43,1,0,0,0,281,282,5,30,
  	0,0,282,294,5,40,0,0,283,284,5,31,0,0,284,289,3,46,23,0,285,286,5,32,
  	0,0,286,288,3,46,23,0,287,285,1,0,0,0,288,291,1,0,0,0,289,287,1,0,0,0,
  	289,290,1,0,0,0,290,292,1,0,0,0,291,289,1,0,0,0,292,293,5,33,0,0,293,
  	295,1,0,0,0,294,283,1,0,0,0,294,295,1,0,0,0,295,296,1,0,0,0,296,301,5,
  	6,0,0,297,302,5,2,0,0,298,299,3,48,24,0,299,300,5,29,0,0,300,302,1,0,
  	0,0,301,297,1,0,0,0,301,298,1,0,0,0,302,45,1,0,0,0,303,304,5,40,0,0,304,
  	47,1,0,0,0,305,306,3,50,25,0,306,49,1,0,0,0,307,312,3,52,26,0,308,309,
  	7,1,0,0,309,311,3,52,26,0,310,308,1,0,0,0,311,314,1,0,0,0,312,310,1,0,
  	0,0,312,313,1,0,0,0,313,51,1,0,0,0,314,312,1,0,0,0,315,320,3,54,27,0,
  	316,317,7,2,0,0,317,319,3,54,27,0,318,316,1,0,0,0,319,322,1,0,0,0,320,
  	318,1,0,0,0,320,321,1,0,0,0,321,53,1,0,0,0,322,320,1,0,0,0,323,328,3,
  	56,28,0,324,325,5,38,0,0,325,327,3,56,28,0,326,324,1,0,0,0,327,330,1,
  	0,0,0,328,326,1,0,0,0,328,329,1,0,0,0,329,55,1,0,0,0,330,328,1,0,0,0,
  	331,336,3,58,29,0,332,333,5,39,0,0,333,335,3,58,29,0,334,332,1,0,0,0,
  	335,338,1,0,0,0,336,334,1,0,0,0,336,337,1,0,0,0,337,57,1,0,0,0,338,336,
  	1,0,0,0,339,340,5,31,0,0,340,341,3,48,24,0,341,342,5,33,0,0,342,360,1,
  	0,0,0,343,360,5,41,0,0,344,356,5,40,0,0,345,346,5,31,0,0,346,351,3,48,
  	24,0,347,348,5,32,0,0,348,350,3,48,24,0,349,347,1,0,0,0,350,353,1,0,0,
  	0,351,349,1,0,0,0,351,352,1,0,0,0,352,354,1,0,0,0,353,351,1,0,0,0,354,
  	355,5,33,0,0,355,357,1,0,0,0,356,345,1,0,0,0,356,357,1,0,0,0,357,360,
  	1,0,0,0,358,360,5,40,0,0,359,339,1,0,0,0,359,343,1,0,0,0,359,344,1,0,
  	0,0,359,358,1,0,0,0,360,59,1,0,0,0,42,67,69,77,81,85,89,94,103,108,113,
  	122,127,135,141,153,162,168,180,185,191,198,201,207,210,216,219,227,248,
  	251,259,267,273,289,294,301,312,320,328,336,351,356,359
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

std::vector<pblangParser::StoreDefContext *> pblangParser::ModelContext::storeDef() {
  return getRuleContexts<pblangParser::StoreDefContext>();
}

pblangParser::StoreDefContext* pblangParser::ModelContext::storeDef(size_t i) {
  return getRuleContext<pblangParser::StoreDefContext>(i);
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
    setState(69);
    _errHandler->sync(this);
    _la = _input->LA(1);
    while ((((_la & ~ 0x3fULL) == 0) &&
      ((1ULL << _la) & 1208247298) != 0)) {
      setState(67);
      _errHandler->sync(this);
      switch (_input->LA(1)) {
        case pblangParser::T__0: {
          setState(60);
          typeDef();
          break;
        }

        case pblangParser::T__29: {
          setState(61);
          definition();
          break;
        }

        case pblangParser::T__12: {
          setState(62);
          unit();
          break;
        }

        case pblangParser::T__17: {
          setState(63);
          processDef();
          break;
        }

        case pblangParser::T__9: {
          setState(64);
          storeDef();
          break;
        }

        case pblangParser::T__26: {
          setState(65);
          compositeDef();
          break;
        }

        case pblangParser::T__13: {
          setState(66);
          sbmlModel();
          break;
        }

      default:
        throw NoViableAltException(this);
      }
      setState(71);
      _errHandler->sync(this);
      _la = _input->LA(1);
    }
    setState(72);
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
    setState(74);
    match(pblangParser::T__0);
    setState(75);
    antlrcpp::downCast<TypeDefContext *>(_localctx)->name = match(pblangParser::ID);
    setState(77);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__1) {
      setState(76);
      antlrcpp::downCast<TypeDefContext *>(_localctx)->builtin = match(pblangParser::T__1);
    }
    setState(81);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__2) {
      setState(79);
      match(pblangParser::T__2);
      setState(80);
      match(pblangParser::ID);
    }
    setState(85);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__3) {
      setState(83);
      match(pblangParser::T__3);
      setState(84);
      defaultValue();
    }
    setState(89);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__4) {
      setState(87);
      match(pblangParser::T__4);
      setState(88);
      match(pblangParser::ID);
    }
    setState(94);
    _errHandler->sync(this);
    _la = _input->LA(1);
    while (_la == pblangParser::ID) {
      setState(91);
      namedType();
      setState(96);
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
    setState(97);
    antlrcpp::downCast<NamedTypeContext *>(_localctx)->name = match(pblangParser::ID);
    setState(98);
    match(pblangParser::T__5);
    setState(103);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__6) {
      setState(99);
      match(pblangParser::T__6);
      setState(100);
      match(pblangParser::T__7);
      setState(101);
      antlrcpp::downCast<NamedTypeContext *>(_localctx)->optional_type_ref = match(pblangParser::ID);
      setState(102);
      match(pblangParser::T__8);
    }
    setState(105);
    antlrcpp::downCast<NamedTypeContext *>(_localctx)->type_ref = match(pblangParser::ID);
    setState(108);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__3) {
      setState(106);
      match(pblangParser::T__3);
      setState(107);
      defaultValue();
    }
    setState(113);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__7) {
      setState(110);
      match(pblangParser::T__7);
      setState(111);
      antlrcpp::downCast<NamedTypeContext *>(_localctx)->unit_ref = match(pblangParser::ID);
      setState(112);
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
    setState(115);
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
    setState(117);
    antlrcpp::downCast<SchemaItemContext *>(_localctx)->name = match(pblangParser::ID);
    setState(118);
    match(pblangParser::T__5);
    setState(119);
    antlrcpp::downCast<SchemaItemContext *>(_localctx)->type_ref = match(pblangParser::ID);
    setState(122);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__3) {
      setState(120);
      match(pblangParser::T__3);
      setState(121);
      defaultValue();
    }
    setState(127);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__7) {
      setState(124);
      match(pblangParser::T__7);
      setState(125);
      antlrcpp::downCast<SchemaItemContext *>(_localctx)->unit_ref = match(pblangParser::ID);
      setState(126);
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

//----------------- StoreDefRefContext ------------------------------------------------------------------

pblangParser::StoreDefRefContext::StoreDefRefContext(ParserRuleContext *parent, size_t invokingState)
  : ParserRuleContext(parent, invokingState) {
}

tree::TerminalNode* pblangParser::StoreDefRefContext::ID() {
  return getToken(pblangParser::ID, 0);
}


size_t pblangParser::StoreDefRefContext::getRuleIndex() const {
  return pblangParser::RuleStoreDefRef;
}

void pblangParser::StoreDefRefContext::enterRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<pblangListener *>(listener);
  if (parserListener != nullptr)
    parserListener->enterStoreDefRef(this);
}

void pblangParser::StoreDefRefContext::exitRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<pblangListener *>(listener);
  if (parserListener != nullptr)
    parserListener->exitStoreDefRef(this);
}

pblangParser::StoreDefRefContext* pblangParser::storeDefRef() {
  StoreDefRefContext *_localctx = _tracker.createInstance<StoreDefRefContext>(_ctx, getState());
  enterRule(_localctx, 10, pblangParser::RuleStoreDefRef);

#if __cplusplus > 201703L
  auto onExit = finally([=, this] {
#else
  auto onExit = finally([=] {
#endif
    exitRule();
  });
  try {
    enterOuterAlt(_localctx, 1);
    setState(129);
    match(pblangParser::ID);

  }
  catch (RecognitionException &e) {
    _errHandler->reportError(this, e);
    _localctx->exception = std::current_exception();
    _errHandler->recover(this, _localctx->exception);
  }

  return _localctx;
}

//----------------- StoreDefContext ------------------------------------------------------------------

pblangParser::StoreDefContext::StoreDefContext(ParserRuleContext *parent, size_t invokingState)
  : ParserRuleContext(parent, invokingState) {
}

tree::TerminalNode* pblangParser::StoreDefContext::ID() {
  return getToken(pblangParser::ID, 0);
}

pblangParser::StoreDefRefContext* pblangParser::StoreDefContext::storeDefRef() {
  return getRuleContext<pblangParser::StoreDefRefContext>(0);
}

std::vector<pblangParser::StoreDefStateDefContext *> pblangParser::StoreDefContext::storeDefStateDef() {
  return getRuleContexts<pblangParser::StoreDefStateDefContext>();
}

pblangParser::StoreDefStateDefContext* pblangParser::StoreDefContext::storeDefStateDef(size_t i) {
  return getRuleContext<pblangParser::StoreDefStateDefContext>(i);
}


size_t pblangParser::StoreDefContext::getRuleIndex() const {
  return pblangParser::RuleStoreDef;
}

void pblangParser::StoreDefContext::enterRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<pblangListener *>(listener);
  if (parserListener != nullptr)
    parserListener->enterStoreDef(this);
}

void pblangParser::StoreDefContext::exitRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<pblangListener *>(listener);
  if (parserListener != nullptr)
    parserListener->exitStoreDef(this);
}

pblangParser::StoreDefContext* pblangParser::storeDef() {
  StoreDefContext *_localctx = _tracker.createInstance<StoreDefContext>(_ctx, getState());
  enterRule(_localctx, 12, pblangParser::RuleStoreDef);
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
    match(pblangParser::T__9);
    setState(132);
    antlrcpp::downCast<StoreDefContext *>(_localctx)->name = match(pblangParser::ID);
    setState(135);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__10) {
      setState(133);
      match(pblangParser::T__10);
      setState(134);
      storeDefRef();
    }
    setState(141);
    _errHandler->sync(this);
    _la = _input->LA(1);
    while (_la == pblangParser::T__11) {
      setState(137);
      match(pblangParser::T__11);
      setState(138);
      storeDefStateDef();
      setState(143);
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

//----------------- StoreDefStateDefContext ------------------------------------------------------------------

pblangParser::StoreDefStateDefContext::StoreDefStateDefContext(ParserRuleContext *parent, size_t invokingState)
  : ParserRuleContext(parent, invokingState) {
}

pblangParser::SchemaItemContext* pblangParser::StoreDefStateDefContext::schemaItem() {
  return getRuleContext<pblangParser::SchemaItemContext>(0);
}


size_t pblangParser::StoreDefStateDefContext::getRuleIndex() const {
  return pblangParser::RuleStoreDefStateDef;
}

void pblangParser::StoreDefStateDefContext::enterRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<pblangListener *>(listener);
  if (parserListener != nullptr)
    parserListener->enterStoreDefStateDef(this);
}

void pblangParser::StoreDefStateDefContext::exitRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<pblangListener *>(listener);
  if (parserListener != nullptr)
    parserListener->exitStoreDefStateDef(this);
}

pblangParser::StoreDefStateDefContext* pblangParser::storeDefStateDef() {
  StoreDefStateDefContext *_localctx = _tracker.createInstance<StoreDefStateDefContext>(_ctx, getState());
  enterRule(_localctx, 14, pblangParser::RuleStoreDefStateDef);

#if __cplusplus > 201703L
  auto onExit = finally([=, this] {
#else
  auto onExit = finally([=] {
#endif
    exitRule();
  });
  try {
    enterOuterAlt(_localctx, 1);
    setState(144);
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
  enterRule(_localctx, 16, pblangParser::RuleUnit);

#if __cplusplus > 201703L
  auto onExit = finally([=, this] {
#else
  auto onExit = finally([=] {
#endif
    exitRule();
  });
  try {
    enterOuterAlt(_localctx, 1);
    setState(146);
    match(pblangParser::T__12);
    setState(147);
    antlrcpp::downCast<UnitContext *>(_localctx)->name = match(pblangParser::ID);
    setState(148);
    match(pblangParser::T__5);
    setState(153);
    _errHandler->sync(this);
    switch (_input->LA(1)) {
      case pblangParser::T__7: {
        setState(149);
        match(pblangParser::T__7);
        setState(150);
        match(pblangParser::STRING);
        setState(151);
        match(pblangParser::T__8);
        break;
      }

      case pblangParser::ID: {
        setState(152);
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

tree::TerminalNode* pblangParser::SbmlModelContext::STRING() {
  return getToken(pblangParser::STRING, 0);
}

tree::TerminalNode* pblangParser::SbmlModelContext::ID() {
  return getToken(pblangParser::ID, 0);
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
  enterRule(_localctx, 18, pblangParser::RuleSbmlModel);
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
    setState(155);
    match(pblangParser::T__13);
    setState(156);
    antlrcpp::downCast<SbmlModelContext *>(_localctx)->name = match(pblangParser::ID);
    setState(157);
    match(pblangParser::T__14);
    setState(158);
    match(pblangParser::STRING);
    setState(162);
    _errHandler->sync(this);
    _la = _input->LA(1);
    while (_la == pblangParser::T__15) {
      setState(159);
      sbmlParameter();
      setState(164);
      _errHandler->sync(this);
      _la = _input->LA(1);
    }
    setState(168);
    _errHandler->sync(this);
    _la = _input->LA(1);
    while (_la == pblangParser::T__16) {
      setState(165);
      sbmlVariable();
      setState(170);
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
  enterRule(_localctx, 20, pblangParser::RuleSbmlParameter);

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
    match(pblangParser::T__15);
    setState(172);
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
  enterRule(_localctx, 22, pblangParser::RuleSbmlVariable);

#if __cplusplus > 201703L
  auto onExit = finally([=, this] {
#else
  auto onExit = finally([=] {
#endif
    exitRule();
  });
  try {
    enterOuterAlt(_localctx, 1);
    setState(174);
    match(pblangParser::T__16);
    setState(175);
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

pblangParser::PythonPathContext* pblangParser::ProcessDefContext::pythonPath() {
  return getRuleContext<pblangParser::PythonPathContext>(0);
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
  enterRule(_localctx, 24, pblangParser::RuleProcessDef);
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
    setState(177);
    match(pblangParser::T__17);
    setState(178);
    match(pblangParser::ID);
    setState(180);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__21) {
      setState(179);
      pythonPath();
    }
    setState(185);
    _errHandler->sync(this);
    _la = _input->LA(1);
    while (_la == pblangParser::T__15) {
      setState(182);
      processParameter();
      setState(187);
      _errHandler->sync(this);
      _la = _input->LA(1);
    }
    setState(191);
    _errHandler->sync(this);
    _la = _input->LA(1);
    while (_la == pblangParser::T__16) {
      setState(188);
      processVariable();
      setState(193);
      _errHandler->sync(this);
      _la = _input->LA(1);
    }
    setState(201);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__18) {
      setState(194);
      match(pblangParser::T__18);
      setState(198);
      _errHandler->sync(this);
      _la = _input->LA(1);
      while (_la == pblangParser::ID) {
        setState(195);
        processInput();
        setState(200);
        _errHandler->sync(this);
        _la = _input->LA(1);
      }
    }
    setState(210);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__19) {
      setState(203);
      match(pblangParser::T__19);
      setState(207);
      _errHandler->sync(this);
      _la = _input->LA(1);
      while (_la == pblangParser::ID) {
        setState(204);
        processOutput();
        setState(209);
        _errHandler->sync(this);
        _la = _input->LA(1);
      }
    }
    setState(219);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__20) {
      setState(212);
      match(pblangParser::T__20);
      setState(216);
      _errHandler->sync(this);
      _la = _input->LA(1);
      while (_la == pblangParser::ID) {
        setState(213);
        update();
        setState(218);
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

//----------------- PythonPathContext ------------------------------------------------------------------

pblangParser::PythonPathContext::PythonPathContext(ParserRuleContext *parent, size_t invokingState)
  : ParserRuleContext(parent, invokingState) {
}

std::vector<tree::TerminalNode *> pblangParser::PythonPathContext::ID() {
  return getTokens(pblangParser::ID);
}

tree::TerminalNode* pblangParser::PythonPathContext::ID(size_t i) {
  return getToken(pblangParser::ID, i);
}


size_t pblangParser::PythonPathContext::getRuleIndex() const {
  return pblangParser::RulePythonPath;
}

void pblangParser::PythonPathContext::enterRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<pblangListener *>(listener);
  if (parserListener != nullptr)
    parserListener->enterPythonPath(this);
}

void pblangParser::PythonPathContext::exitRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<pblangListener *>(listener);
  if (parserListener != nullptr)
    parserListener->exitPythonPath(this);
}

pblangParser::PythonPathContext* pblangParser::pythonPath() {
  PythonPathContext *_localctx = _tracker.createInstance<PythonPathContext>(_ctx, getState());
  enterRule(_localctx, 26, pblangParser::RulePythonPath);
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
    setState(221);
    match(pblangParser::T__21);
    setState(222);
    match(pblangParser::ID);
    setState(227);
    _errHandler->sync(this);
    _la = _input->LA(1);
    while (_la == pblangParser::T__22) {
      setState(223);
      match(pblangParser::T__22);
      setState(224);
      match(pblangParser::ID);
      setState(229);
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
  enterRule(_localctx, 28, pblangParser::RuleProcessParameter);

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
    match(pblangParser::T__15);
    setState(231);
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
  enterRule(_localctx, 30, pblangParser::RuleProcessVariable);

#if __cplusplus > 201703L
  auto onExit = finally([=, this] {
#else
  auto onExit = finally([=] {
#endif
    exitRule();
  });
  try {
    enterOuterAlt(_localctx, 1);
    setState(233);
    match(pblangParser::T__16);
    setState(234);
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
  enterRule(_localctx, 32, pblangParser::RuleProcessInput);

#if __cplusplus > 201703L
  auto onExit = finally([=, this] {
#else
  auto onExit = finally([=] {
#endif
    exitRule();
  });
  try {
    enterOuterAlt(_localctx, 1);
    setState(236);
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
  enterRule(_localctx, 34, pblangParser::RuleProcessOutput);

#if __cplusplus > 201703L
  auto onExit = finally([=, this] {
#else
  auto onExit = finally([=] {
#endif
    exitRule();
  });
  try {
    enterOuterAlt(_localctx, 1);
    setState(238);
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

std::vector<pblangParser::StoreDefRefContext *> pblangParser::ProcessContext::storeDefRef() {
  return getRuleContexts<pblangParser::StoreDefRefContext>();
}

pblangParser::StoreDefRefContext* pblangParser::ProcessContext::storeDefRef(size_t i) {
  return getRuleContext<pblangParser::StoreDefRefContext>(i);
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
  enterRule(_localctx, 36, pblangParser::RuleProcess);
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
    setState(240);
    match(pblangParser::T__23);
    setState(241);
    antlrcpp::downCast<ProcessContext *>(_localctx)->name = match(pblangParser::ID);
    setState(242);
    match(pblangParser::T__5);
    setState(243);
    antlrcpp::downCast<ProcessContext *>(_localctx)->process_def_ref = match(pblangParser::ID);
    setState(251);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__24) {
      setState(244);
      match(pblangParser::T__24);
      setState(248);
      _errHandler->sync(this);
      _la = _input->LA(1);
      while (_la == pblangParser::ID) {
        setState(245);
        storeDefRef();
        setState(250);
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
  enterRule(_localctx, 38, pblangParser::RuleStore);
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
    match(pblangParser::T__25);
    setState(254);
    antlrcpp::downCast<StoreContext *>(_localctx)->name = match(pblangParser::ID);
    setState(255);
    match(pblangParser::T__5);
    setState(259);
    _errHandler->sync(this);
    _la = _input->LA(1);
    while (_la == pblangParser::ID) {
      setState(256);
      antlrcpp::downCast<StoreContext *>(_localctx)->store_def = match(pblangParser::ID);
      setState(261);
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

//----------------- CompositeDefContext ------------------------------------------------------------------

pblangParser::CompositeDefContext::CompositeDefContext(ParserRuleContext *parent, size_t invokingState)
  : ParserRuleContext(parent, invokingState) {
}

tree::TerminalNode* pblangParser::CompositeDefContext::ID() {
  return getToken(pblangParser::ID, 0);
}

std::vector<pblangParser::StoreContext *> pblangParser::CompositeDefContext::store() {
  return getRuleContexts<pblangParser::StoreContext>();
}

pblangParser::StoreContext* pblangParser::CompositeDefContext::store(size_t i) {
  return getRuleContext<pblangParser::StoreContext>(i);
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
  enterRule(_localctx, 40, pblangParser::RuleCompositeDef);
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
    setState(262);
    match(pblangParser::T__26);
    setState(263);
    antlrcpp::downCast<CompositeDefContext *>(_localctx)->name = match(pblangParser::ID);
    setState(267);
    _errHandler->sync(this);
    _la = _input->LA(1);
    while (_la == pblangParser::T__25) {
      setState(264);
      store();
      setState(269);
      _errHandler->sync(this);
      _la = _input->LA(1);
    }
    setState(273);
    _errHandler->sync(this);
    _la = _input->LA(1);
    while (_la == pblangParser::T__23) {
      setState(270);
      process();
      setState(275);
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
  enterRule(_localctx, 42, pblangParser::RuleUpdate);

#if __cplusplus > 201703L
  auto onExit = finally([=, this] {
#else
  auto onExit = finally([=] {
#endif
    exitRule();
  });
  try {
    enterOuterAlt(_localctx, 1);
    setState(276);
    antlrcpp::downCast<UpdateContext *>(_localctx)->lhs = match(pblangParser::ID);
    setState(277);
    match(pblangParser::T__27);
    setState(278);
    expression();
    setState(279);
    match(pblangParser::T__28);

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
  enterRule(_localctx, 44, pblangParser::RuleDefinition);
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
    match(pblangParser::T__29);
    setState(282);
    match(pblangParser::ID);
    setState(294);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__30) {
      setState(283);
      match(pblangParser::T__30);
      setState(284);
      declaredParameter();
      setState(289);
      _errHandler->sync(this);
      _la = _input->LA(1);
      while (_la == pblangParser::T__31) {
        setState(285);
        match(pblangParser::T__31);
        setState(286);
        declaredParameter();
        setState(291);
        _errHandler->sync(this);
        _la = _input->LA(1);
      }
      setState(292);
      match(pblangParser::T__32);
    }
    setState(296);
    match(pblangParser::T__5);
    setState(301);
    _errHandler->sync(this);
    switch (_input->LA(1)) {
      case pblangParser::T__1: {
        setState(297);
        antlrcpp::downCast<DefinitionContext *>(_localctx)->builtin = match(pblangParser::T__1);
        break;
      }

      case pblangParser::T__30:
      case pblangParser::ID:
      case pblangParser::FLOAT: {
        setState(298);
        expression();
        setState(299);
        match(pblangParser::T__28);
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
  enterRule(_localctx, 46, pblangParser::RuleDeclaredParameter);

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
  enterRule(_localctx, 48, pblangParser::RuleExpression);

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
  enterRule(_localctx, 50, pblangParser::RuleAddition);
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
    setState(307);
    multiplication();
    setState(312);
    _errHandler->sync(this);
    _la = _input->LA(1);
    while (_la == pblangParser::T__33

    || _la == pblangParser::T__34) {
      setState(308);
      _la = _input->LA(1);
      if (!(_la == pblangParser::T__33

      || _la == pblangParser::T__34)) {
      _errHandler->recoverInline(this);
      }
      else {
        _errHandler->reportMatch(this);
        consume();
      }
      setState(309);
      multiplication();
      setState(314);
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
  enterRule(_localctx, 52, pblangParser::RuleMultiplication);
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
    setState(315);
    exponentiation();
    setState(320);
    _errHandler->sync(this);
    _la = _input->LA(1);
    while (_la == pblangParser::T__35

    || _la == pblangParser::T__36) {
      setState(316);
      _la = _input->LA(1);
      if (!(_la == pblangParser::T__35

      || _la == pblangParser::T__36)) {
      _errHandler->recoverInline(this);
      }
      else {
        _errHandler->reportMatch(this);
        consume();
      }
      setState(317);
      exponentiation();
      setState(322);
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
  enterRule(_localctx, 54, pblangParser::RuleExponentiation);
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
    setState(323);
    modulo();
    setState(328);
    _errHandler->sync(this);
    _la = _input->LA(1);
    while (_la == pblangParser::T__37) {
      setState(324);
      match(pblangParser::T__37);
      setState(325);
      modulo();
      setState(330);
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
  enterRule(_localctx, 56, pblangParser::RuleModulo);
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
    setState(331);
    primaryExpression();
    setState(336);
    _errHandler->sync(this);
    _la = _input->LA(1);
    while (_la == pblangParser::T__38) {
      setState(332);
      match(pblangParser::T__38);
      setState(333);
      primaryExpression();
      setState(338);
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
  enterRule(_localctx, 58, pblangParser::RulePrimaryExpression);
  size_t _la = 0;

#if __cplusplus > 201703L
  auto onExit = finally([=, this] {
#else
  auto onExit = finally([=] {
#endif
    exitRule();
  });
  try {
    setState(359);
    _errHandler->sync(this);
    switch (getInterpreter<atn::ParserATNSimulator>()->adaptivePredict(_input, 41, _ctx)) {
    case 1: {
      enterOuterAlt(_localctx, 1);
      setState(339);
      match(pblangParser::T__30);
      setState(340);
      expression();
      setState(341);
      match(pblangParser::T__32);
      break;
    }

    case 2: {
      enterOuterAlt(_localctx, 2);
      setState(343);
      match(pblangParser::FLOAT);
      break;
    }

    case 3: {
      enterOuterAlt(_localctx, 3);
      setState(344);
      match(pblangParser::ID);
      setState(356);
      _errHandler->sync(this);

      _la = _input->LA(1);
      if (_la == pblangParser::T__30) {
        setState(345);
        match(pblangParser::T__30);
        setState(346);
        expression();
        setState(351);
        _errHandler->sync(this);
        _la = _input->LA(1);
        while (_la == pblangParser::T__31) {
          setState(347);
          match(pblangParser::T__31);
          setState(348);
          expression();
          setState(353);
          _errHandler->sync(this);
          _la = _input->LA(1);
        }
        setState(354);
        match(pblangParser::T__32);
      }
      break;
    }

    case 4: {
      enterOuterAlt(_localctx, 4);
      setState(358);
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
