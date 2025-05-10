
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
      "model", "typeDef", "namedType", "defaultValue", "schemaItem", "storeDef",
      "storeDefStateDef", "unit", "sbmlModel", "sbmlParameter", "sbmlVariable",
      "processDef", "pythonPath", "processParameter", "processVariable",
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
  	4,1,46,358,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,6,2,
  	7,7,7,2,8,7,8,2,9,7,9,2,10,7,10,2,11,7,11,2,12,7,12,2,13,7,13,2,14,7,
  	14,2,15,7,15,2,16,7,16,2,17,7,17,2,18,7,18,2,19,7,19,2,20,7,20,2,21,7,
  	21,2,22,7,22,2,23,7,23,2,24,7,24,2,25,7,25,2,26,7,26,2,27,7,27,2,28,7,
  	28,1,0,1,0,1,0,1,0,1,0,1,0,1,0,5,0,66,8,0,10,0,12,0,69,9,0,1,0,1,0,1,
  	1,1,1,1,1,3,1,76,8,1,1,1,1,1,3,1,80,8,1,1,1,1,1,3,1,84,8,1,1,1,1,1,3,
  	1,88,8,1,1,1,5,1,91,8,1,10,1,12,1,94,9,1,1,2,1,2,1,2,1,2,1,2,1,2,3,2,
  	102,8,2,1,2,1,2,1,2,3,2,107,8,2,1,2,1,2,1,2,3,2,112,8,2,1,3,1,3,1,4,1,
  	4,1,4,1,4,1,4,3,4,121,8,4,1,4,1,4,1,4,3,4,126,8,4,1,5,1,5,1,5,1,5,3,5,
  	132,8,5,1,5,1,5,5,5,136,8,5,10,5,12,5,139,9,5,1,6,1,6,1,7,1,7,1,7,1,7,
  	1,7,1,7,1,7,3,7,150,8,7,1,8,1,8,1,8,1,8,1,8,5,8,157,8,8,10,8,12,8,160,
  	9,8,1,8,5,8,163,8,8,10,8,12,8,166,9,8,1,9,1,9,1,9,1,10,1,10,1,10,1,11,
  	1,11,1,11,3,11,177,8,11,1,11,5,11,180,8,11,10,11,12,11,183,9,11,1,11,
  	5,11,186,8,11,10,11,12,11,189,9,11,1,11,1,11,5,11,193,8,11,10,11,12,11,
  	196,9,11,3,11,198,8,11,1,11,1,11,5,11,202,8,11,10,11,12,11,205,9,11,3,
  	11,207,8,11,1,11,1,11,5,11,211,8,11,10,11,12,11,214,9,11,3,11,216,8,11,
  	1,12,1,12,1,12,1,12,5,12,222,8,12,10,12,12,12,225,9,12,1,13,1,13,1,13,
  	1,14,1,14,1,14,1,15,1,15,1,16,1,16,1,17,1,17,1,17,1,17,1,17,1,17,5,17,
  	243,8,17,10,17,12,17,246,9,17,3,17,248,8,17,1,18,1,18,1,18,1,18,5,18,
  	254,8,18,10,18,12,18,257,9,18,1,19,1,19,1,19,5,19,262,8,19,10,19,12,19,
  	265,9,19,1,19,5,19,268,8,19,10,19,12,19,271,9,19,1,20,1,20,1,20,1,20,
  	1,20,1,21,1,21,1,21,1,21,1,21,1,21,5,21,284,8,21,10,21,12,21,287,9,21,
  	1,21,1,21,3,21,291,8,21,1,21,1,21,1,21,1,21,1,21,3,21,298,8,21,1,22,1,
  	22,1,23,1,23,1,24,1,24,1,24,5,24,307,8,24,10,24,12,24,310,9,24,1,25,1,
  	25,1,25,5,25,315,8,25,10,25,12,25,318,9,25,1,26,1,26,1,26,5,26,323,8,
  	26,10,26,12,26,326,9,26,1,27,1,27,1,27,5,27,331,8,27,10,27,12,27,334,
  	9,27,1,28,1,28,1,28,1,28,1,28,1,28,1,28,1,28,1,28,1,28,5,28,346,8,28,
  	10,28,12,28,349,9,28,1,28,1,28,3,28,353,8,28,1,28,3,28,356,8,28,1,28,
  	0,0,29,0,2,4,6,8,10,12,14,16,18,20,22,24,26,28,30,32,34,36,38,40,42,44,
  	46,48,50,52,54,56,0,3,1,0,41,42,1,0,34,35,1,0,36,37,377,0,67,1,0,0,0,
  	2,72,1,0,0,0,4,95,1,0,0,0,6,113,1,0,0,0,8,115,1,0,0,0,10,127,1,0,0,0,
  	12,140,1,0,0,0,14,142,1,0,0,0,16,151,1,0,0,0,18,167,1,0,0,0,20,170,1,
  	0,0,0,22,173,1,0,0,0,24,217,1,0,0,0,26,226,1,0,0,0,28,229,1,0,0,0,30,
  	232,1,0,0,0,32,234,1,0,0,0,34,236,1,0,0,0,36,249,1,0,0,0,38,258,1,0,0,
  	0,40,272,1,0,0,0,42,277,1,0,0,0,44,299,1,0,0,0,46,301,1,0,0,0,48,303,
  	1,0,0,0,50,311,1,0,0,0,52,319,1,0,0,0,54,327,1,0,0,0,56,355,1,0,0,0,58,
  	66,3,2,1,0,59,66,3,42,21,0,60,66,3,14,7,0,61,66,3,22,11,0,62,66,3,10,
  	5,0,63,66,3,38,19,0,64,66,3,16,8,0,65,58,1,0,0,0,65,59,1,0,0,0,65,60,
  	1,0,0,0,65,61,1,0,0,0,65,62,1,0,0,0,65,63,1,0,0,0,65,64,1,0,0,0,66,69,
  	1,0,0,0,67,65,1,0,0,0,67,68,1,0,0,0,68,70,1,0,0,0,69,67,1,0,0,0,70,71,
  	5,0,0,1,71,1,1,0,0,0,72,73,5,1,0,0,73,75,5,40,0,0,74,76,5,2,0,0,75,74,
  	1,0,0,0,75,76,1,0,0,0,76,79,1,0,0,0,77,78,5,3,0,0,78,80,5,40,0,0,79,77,
  	1,0,0,0,79,80,1,0,0,0,80,83,1,0,0,0,81,82,5,4,0,0,82,84,3,6,3,0,83,81,
  	1,0,0,0,83,84,1,0,0,0,84,87,1,0,0,0,85,86,5,5,0,0,86,88,5,40,0,0,87,85,
  	1,0,0,0,87,88,1,0,0,0,88,92,1,0,0,0,89,91,3,4,2,0,90,89,1,0,0,0,91,94,
  	1,0,0,0,92,90,1,0,0,0,92,93,1,0,0,0,93,3,1,0,0,0,94,92,1,0,0,0,95,96,
  	5,40,0,0,96,101,5,6,0,0,97,98,5,7,0,0,98,99,5,8,0,0,99,100,5,40,0,0,100,
  	102,5,9,0,0,101,97,1,0,0,0,101,102,1,0,0,0,102,103,1,0,0,0,103,106,5,
  	40,0,0,104,105,5,4,0,0,105,107,3,6,3,0,106,104,1,0,0,0,106,107,1,0,0,
  	0,107,111,1,0,0,0,108,109,5,8,0,0,109,110,5,40,0,0,110,112,5,9,0,0,111,
  	108,1,0,0,0,111,112,1,0,0,0,112,5,1,0,0,0,113,114,7,0,0,0,114,7,1,0,0,
  	0,115,116,5,40,0,0,116,117,5,6,0,0,117,120,5,40,0,0,118,119,5,4,0,0,119,
  	121,3,6,3,0,120,118,1,0,0,0,120,121,1,0,0,0,121,125,1,0,0,0,122,123,5,
  	8,0,0,123,124,5,40,0,0,124,126,5,9,0,0,125,122,1,0,0,0,125,126,1,0,0,
  	0,126,9,1,0,0,0,127,128,5,10,0,0,128,131,5,40,0,0,129,130,5,11,0,0,130,
  	132,5,40,0,0,131,129,1,0,0,0,131,132,1,0,0,0,132,137,1,0,0,0,133,134,
  	5,12,0,0,134,136,3,12,6,0,135,133,1,0,0,0,136,139,1,0,0,0,137,135,1,0,
  	0,0,137,138,1,0,0,0,138,11,1,0,0,0,139,137,1,0,0,0,140,141,3,8,4,0,141,
  	13,1,0,0,0,142,143,5,13,0,0,143,144,5,40,0,0,144,149,5,6,0,0,145,146,
  	5,8,0,0,146,147,5,43,0,0,147,150,5,9,0,0,148,150,5,40,0,0,149,145,1,0,
  	0,0,149,148,1,0,0,0,150,15,1,0,0,0,151,152,5,14,0,0,152,153,5,40,0,0,
  	153,154,5,15,0,0,154,158,5,43,0,0,155,157,3,18,9,0,156,155,1,0,0,0,157,
  	160,1,0,0,0,158,156,1,0,0,0,158,159,1,0,0,0,159,164,1,0,0,0,160,158,1,
  	0,0,0,161,163,3,20,10,0,162,161,1,0,0,0,163,166,1,0,0,0,164,162,1,0,0,
  	0,164,165,1,0,0,0,165,17,1,0,0,0,166,164,1,0,0,0,167,168,5,16,0,0,168,
  	169,3,8,4,0,169,19,1,0,0,0,170,171,5,17,0,0,171,172,3,8,4,0,172,21,1,
  	0,0,0,173,174,5,18,0,0,174,176,5,40,0,0,175,177,3,24,12,0,176,175,1,0,
  	0,0,176,177,1,0,0,0,177,181,1,0,0,0,178,180,3,26,13,0,179,178,1,0,0,0,
  	180,183,1,0,0,0,181,179,1,0,0,0,181,182,1,0,0,0,182,187,1,0,0,0,183,181,
  	1,0,0,0,184,186,3,28,14,0,185,184,1,0,0,0,186,189,1,0,0,0,187,185,1,0,
  	0,0,187,188,1,0,0,0,188,197,1,0,0,0,189,187,1,0,0,0,190,194,5,19,0,0,
  	191,193,3,30,15,0,192,191,1,0,0,0,193,196,1,0,0,0,194,192,1,0,0,0,194,
  	195,1,0,0,0,195,198,1,0,0,0,196,194,1,0,0,0,197,190,1,0,0,0,197,198,1,
  	0,0,0,198,206,1,0,0,0,199,203,5,20,0,0,200,202,3,32,16,0,201,200,1,0,
  	0,0,202,205,1,0,0,0,203,201,1,0,0,0,203,204,1,0,0,0,204,207,1,0,0,0,205,
  	203,1,0,0,0,206,199,1,0,0,0,206,207,1,0,0,0,207,215,1,0,0,0,208,212,5,
  	21,0,0,209,211,3,40,20,0,210,209,1,0,0,0,211,214,1,0,0,0,212,210,1,0,
  	0,0,212,213,1,0,0,0,213,216,1,0,0,0,214,212,1,0,0,0,215,208,1,0,0,0,215,
  	216,1,0,0,0,216,23,1,0,0,0,217,218,5,22,0,0,218,223,5,40,0,0,219,220,
  	5,23,0,0,220,222,5,40,0,0,221,219,1,0,0,0,222,225,1,0,0,0,223,221,1,0,
  	0,0,223,224,1,0,0,0,224,25,1,0,0,0,225,223,1,0,0,0,226,227,5,16,0,0,227,
  	228,3,8,4,0,228,27,1,0,0,0,229,230,5,17,0,0,230,231,3,8,4,0,231,29,1,
  	0,0,0,232,233,5,40,0,0,233,31,1,0,0,0,234,235,5,40,0,0,235,33,1,0,0,0,
  	236,237,5,24,0,0,237,238,5,40,0,0,238,239,5,6,0,0,239,247,5,40,0,0,240,
  	244,5,25,0,0,241,243,5,40,0,0,242,241,1,0,0,0,243,246,1,0,0,0,244,242,
  	1,0,0,0,244,245,1,0,0,0,245,248,1,0,0,0,246,244,1,0,0,0,247,240,1,0,0,
  	0,247,248,1,0,0,0,248,35,1,0,0,0,249,250,5,26,0,0,250,251,5,40,0,0,251,
  	255,5,6,0,0,252,254,5,40,0,0,253,252,1,0,0,0,254,257,1,0,0,0,255,253,
  	1,0,0,0,255,256,1,0,0,0,256,37,1,0,0,0,257,255,1,0,0,0,258,259,5,27,0,
  	0,259,263,5,40,0,0,260,262,3,36,18,0,261,260,1,0,0,0,262,265,1,0,0,0,
  	263,261,1,0,0,0,263,264,1,0,0,0,264,269,1,0,0,0,265,263,1,0,0,0,266,268,
  	3,34,17,0,267,266,1,0,0,0,268,271,1,0,0,0,269,267,1,0,0,0,269,270,1,0,
  	0,0,270,39,1,0,0,0,271,269,1,0,0,0,272,273,5,40,0,0,273,274,5,28,0,0,
  	274,275,3,46,23,0,275,276,5,29,0,0,276,41,1,0,0,0,277,278,5,30,0,0,278,
  	290,5,40,0,0,279,280,5,31,0,0,280,285,3,44,22,0,281,282,5,32,0,0,282,
  	284,3,44,22,0,283,281,1,0,0,0,284,287,1,0,0,0,285,283,1,0,0,0,285,286,
  	1,0,0,0,286,288,1,0,0,0,287,285,1,0,0,0,288,289,5,33,0,0,289,291,1,0,
  	0,0,290,279,1,0,0,0,290,291,1,0,0,0,291,292,1,0,0,0,292,297,5,6,0,0,293,
  	298,5,2,0,0,294,295,3,46,23,0,295,296,5,29,0,0,296,298,1,0,0,0,297,293,
  	1,0,0,0,297,294,1,0,0,0,298,43,1,0,0,0,299,300,5,40,0,0,300,45,1,0,0,
  	0,301,302,3,48,24,0,302,47,1,0,0,0,303,308,3,50,25,0,304,305,7,1,0,0,
  	305,307,3,50,25,0,306,304,1,0,0,0,307,310,1,0,0,0,308,306,1,0,0,0,308,
  	309,1,0,0,0,309,49,1,0,0,0,310,308,1,0,0,0,311,316,3,52,26,0,312,313,
  	7,2,0,0,313,315,3,52,26,0,314,312,1,0,0,0,315,318,1,0,0,0,316,314,1,0,
  	0,0,316,317,1,0,0,0,317,51,1,0,0,0,318,316,1,0,0,0,319,324,3,54,27,0,
  	320,321,5,38,0,0,321,323,3,54,27,0,322,320,1,0,0,0,323,326,1,0,0,0,324,
  	322,1,0,0,0,324,325,1,0,0,0,325,53,1,0,0,0,326,324,1,0,0,0,327,332,3,
  	56,28,0,328,329,5,39,0,0,329,331,3,56,28,0,330,328,1,0,0,0,331,334,1,
  	0,0,0,332,330,1,0,0,0,332,333,1,0,0,0,333,55,1,0,0,0,334,332,1,0,0,0,
  	335,336,5,31,0,0,336,337,3,46,23,0,337,338,5,33,0,0,338,356,1,0,0,0,339,
  	356,5,41,0,0,340,352,5,40,0,0,341,342,5,31,0,0,342,347,3,46,23,0,343,
  	344,5,32,0,0,344,346,3,46,23,0,345,343,1,0,0,0,346,349,1,0,0,0,347,345,
  	1,0,0,0,347,348,1,0,0,0,348,350,1,0,0,0,349,347,1,0,0,0,350,351,5,33,
  	0,0,351,353,1,0,0,0,352,341,1,0,0,0,352,353,1,0,0,0,353,356,1,0,0,0,354,
  	356,5,40,0,0,355,335,1,0,0,0,355,339,1,0,0,0,355,340,1,0,0,0,355,354,
  	1,0,0,0,356,57,1,0,0,0,42,65,67,75,79,83,87,92,101,106,111,120,125,131,
  	137,149,158,164,176,181,187,194,197,203,206,212,215,223,244,247,255,263,
  	269,285,290,297,308,316,324,332,347,352,355
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
    setState(67);
    _errHandler->sync(this);
    _la = _input->LA(1);
    while ((((_la & ~ 0x3fULL) == 0) &&
      ((1ULL << _la) & 1208247298) != 0)) {
      setState(65);
      _errHandler->sync(this);
      switch (_input->LA(1)) {
        case pblangParser::T__0: {
          setState(58);
          typeDef();
          break;
        }

        case pblangParser::T__29: {
          setState(59);
          definition();
          break;
        }

        case pblangParser::T__12: {
          setState(60);
          unit();
          break;
        }

        case pblangParser::T__17: {
          setState(61);
          processDef();
          break;
        }

        case pblangParser::T__9: {
          setState(62);
          storeDef();
          break;
        }

        case pblangParser::T__26: {
          setState(63);
          compositeDef();
          break;
        }

        case pblangParser::T__13: {
          setState(64);
          sbmlModel();
          break;
        }

      default:
        throw NoViableAltException(this);
      }
      setState(69);
      _errHandler->sync(this);
      _la = _input->LA(1);
    }
    setState(70);
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
    setState(72);
    match(pblangParser::T__0);
    setState(73);
    antlrcpp::downCast<TypeDefContext *>(_localctx)->name = match(pblangParser::ID);
    setState(75);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__1) {
      setState(74);
      antlrcpp::downCast<TypeDefContext *>(_localctx)->builtin = match(pblangParser::T__1);
    }
    setState(79);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__2) {
      setState(77);
      match(pblangParser::T__2);
      setState(78);
      match(pblangParser::ID);
    }
    setState(83);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__3) {
      setState(81);
      match(pblangParser::T__3);
      setState(82);
      defaultValue();
    }
    setState(87);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__4) {
      setState(85);
      match(pblangParser::T__4);
      setState(86);
      match(pblangParser::ID);
    }
    setState(92);
    _errHandler->sync(this);
    _la = _input->LA(1);
    while (_la == pblangParser::ID) {
      setState(89);
      namedType();
      setState(94);
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
    setState(95);
    antlrcpp::downCast<NamedTypeContext *>(_localctx)->name = match(pblangParser::ID);
    setState(96);
    match(pblangParser::T__5);
    setState(101);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__6) {
      setState(97);
      match(pblangParser::T__6);
      setState(98);
      match(pblangParser::T__7);
      setState(99);
      antlrcpp::downCast<NamedTypeContext *>(_localctx)->optional_type_ref = match(pblangParser::ID);
      setState(100);
      match(pblangParser::T__8);
    }
    setState(103);
    antlrcpp::downCast<NamedTypeContext *>(_localctx)->type_ref = match(pblangParser::ID);
    setState(106);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__3) {
      setState(104);
      match(pblangParser::T__3);
      setState(105);
      defaultValue();
    }
    setState(111);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__7) {
      setState(108);
      match(pblangParser::T__7);
      setState(109);
      antlrcpp::downCast<NamedTypeContext *>(_localctx)->unit_ref = match(pblangParser::ID);
      setState(110);
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
    setState(113);
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
    setState(115);
    antlrcpp::downCast<SchemaItemContext *>(_localctx)->name = match(pblangParser::ID);
    setState(116);
    match(pblangParser::T__5);
    setState(117);
    antlrcpp::downCast<SchemaItemContext *>(_localctx)->type_ref = match(pblangParser::ID);
    setState(120);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__3) {
      setState(118);
      match(pblangParser::T__3);
      setState(119);
      defaultValue();
    }
    setState(125);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__7) {
      setState(122);
      match(pblangParser::T__7);
      setState(123);
      antlrcpp::downCast<SchemaItemContext *>(_localctx)->unit_ref = match(pblangParser::ID);
      setState(124);
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

//----------------- StoreDefContext ------------------------------------------------------------------

pblangParser::StoreDefContext::StoreDefContext(ParserRuleContext *parent, size_t invokingState)
  : ParserRuleContext(parent, invokingState) {
}

std::vector<tree::TerminalNode *> pblangParser::StoreDefContext::ID() {
  return getTokens(pblangParser::ID);
}

tree::TerminalNode* pblangParser::StoreDefContext::ID(size_t i) {
  return getToken(pblangParser::ID, i);
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
  enterRule(_localctx, 10, pblangParser::RuleStoreDef);
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
    setState(127);
    match(pblangParser::T__9);
    setState(128);
    antlrcpp::downCast<StoreDefContext *>(_localctx)->name = match(pblangParser::ID);
    setState(131);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__10) {
      setState(129);
      match(pblangParser::T__10);
      setState(130);
      antlrcpp::downCast<StoreDefContext *>(_localctx)->store_def_ref = match(pblangParser::ID);
    }
    setState(137);
    _errHandler->sync(this);
    _la = _input->LA(1);
    while (_la == pblangParser::T__11) {
      setState(133);
      match(pblangParser::T__11);
      setState(134);
      storeDefStateDef();
      setState(139);
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
  enterRule(_localctx, 12, pblangParser::RuleStoreDefStateDef);

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
    setState(142);
    match(pblangParser::T__12);
    setState(143);
    antlrcpp::downCast<UnitContext *>(_localctx)->name = match(pblangParser::ID);
    setState(144);
    match(pblangParser::T__5);
    setState(149);
    _errHandler->sync(this);
    switch (_input->LA(1)) {
      case pblangParser::T__7: {
        setState(145);
        match(pblangParser::T__7);
        setState(146);
        match(pblangParser::STRING);
        setState(147);
        match(pblangParser::T__8);
        break;
      }

      case pblangParser::ID: {
        setState(148);
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
    setState(151);
    match(pblangParser::T__13);
    setState(152);
    antlrcpp::downCast<SbmlModelContext *>(_localctx)->name = match(pblangParser::ID);
    setState(153);
    match(pblangParser::T__14);
    setState(154);
    match(pblangParser::STRING);
    setState(158);
    _errHandler->sync(this);
    _la = _input->LA(1);
    while (_la == pblangParser::T__15) {
      setState(155);
      sbmlParameter();
      setState(160);
      _errHandler->sync(this);
      _la = _input->LA(1);
    }
    setState(164);
    _errHandler->sync(this);
    _la = _input->LA(1);
    while (_la == pblangParser::T__16) {
      setState(161);
      sbmlVariable();
      setState(166);
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
    setState(167);
    match(pblangParser::T__15);
    setState(168);
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
    setState(170);
    match(pblangParser::T__16);
    setState(171);
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
    setState(173);
    match(pblangParser::T__17);
    setState(174);
    match(pblangParser::ID);
    setState(176);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__21) {
      setState(175);
      pythonPath();
    }
    setState(181);
    _errHandler->sync(this);
    _la = _input->LA(1);
    while (_la == pblangParser::T__15) {
      setState(178);
      processParameter();
      setState(183);
      _errHandler->sync(this);
      _la = _input->LA(1);
    }
    setState(187);
    _errHandler->sync(this);
    _la = _input->LA(1);
    while (_la == pblangParser::T__16) {
      setState(184);
      processVariable();
      setState(189);
      _errHandler->sync(this);
      _la = _input->LA(1);
    }
    setState(197);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__18) {
      setState(190);
      match(pblangParser::T__18);
      setState(194);
      _errHandler->sync(this);
      _la = _input->LA(1);
      while (_la == pblangParser::ID) {
        setState(191);
        processInput();
        setState(196);
        _errHandler->sync(this);
        _la = _input->LA(1);
      }
    }
    setState(206);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__19) {
      setState(199);
      match(pblangParser::T__19);
      setState(203);
      _errHandler->sync(this);
      _la = _input->LA(1);
      while (_la == pblangParser::ID) {
        setState(200);
        processOutput();
        setState(205);
        _errHandler->sync(this);
        _la = _input->LA(1);
      }
    }
    setState(215);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__20) {
      setState(208);
      match(pblangParser::T__20);
      setState(212);
      _errHandler->sync(this);
      _la = _input->LA(1);
      while (_la == pblangParser::ID) {
        setState(209);
        update();
        setState(214);
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
  enterRule(_localctx, 24, pblangParser::RulePythonPath);
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
    setState(217);
    match(pblangParser::T__21);
    setState(218);
    match(pblangParser::ID);
    setState(223);
    _errHandler->sync(this);
    _la = _input->LA(1);
    while (_la == pblangParser::T__22) {
      setState(219);
      match(pblangParser::T__22);
      setState(220);
      match(pblangParser::ID);
      setState(225);
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
    setState(226);
    match(pblangParser::T__15);
    setState(227);
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
    setState(229);
    match(pblangParser::T__16);
    setState(230);
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
    setState(234);
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
    setState(236);
    match(pblangParser::T__23);
    setState(237);
    antlrcpp::downCast<ProcessContext *>(_localctx)->name = match(pblangParser::ID);
    setState(238);
    match(pblangParser::T__5);
    setState(239);
    antlrcpp::downCast<ProcessContext *>(_localctx)->process_def_ref = match(pblangParser::ID);
    setState(247);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__24) {
      setState(240);
      match(pblangParser::T__24);
      setState(244);
      _errHandler->sync(this);
      _la = _input->LA(1);
      while (_la == pblangParser::ID) {
        setState(241);
        antlrcpp::downCast<ProcessContext *>(_localctx)->idToken = match(pblangParser::ID);
        antlrcpp::downCast<ProcessContext *>(_localctx)->store_def_refs.push_back(antlrcpp::downCast<ProcessContext *>(_localctx)->idToken);
        setState(246);
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
  enterRule(_localctx, 36, pblangParser::RuleStore);
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
    setState(249);
    match(pblangParser::T__25);
    setState(250);
    antlrcpp::downCast<StoreContext *>(_localctx)->name = match(pblangParser::ID);
    setState(251);
    match(pblangParser::T__5);
    setState(255);
    _errHandler->sync(this);
    _la = _input->LA(1);
    while (_la == pblangParser::ID) {
      setState(252);
      antlrcpp::downCast<StoreContext *>(_localctx)->store_def = match(pblangParser::ID);
      setState(257);
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
  enterRule(_localctx, 38, pblangParser::RuleCompositeDef);
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
    setState(258);
    match(pblangParser::T__26);
    setState(259);
    antlrcpp::downCast<CompositeDefContext *>(_localctx)->name = match(pblangParser::ID);
    setState(263);
    _errHandler->sync(this);
    _la = _input->LA(1);
    while (_la == pblangParser::T__25) {
      setState(260);
      store();
      setState(265);
      _errHandler->sync(this);
      _la = _input->LA(1);
    }
    setState(269);
    _errHandler->sync(this);
    _la = _input->LA(1);
    while (_la == pblangParser::T__23) {
      setState(266);
      process();
      setState(271);
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
  enterRule(_localctx, 40, pblangParser::RuleUpdate);

#if __cplusplus > 201703L
  auto onExit = finally([=, this] {
#else
  auto onExit = finally([=] {
#endif
    exitRule();
  });
  try {
    enterOuterAlt(_localctx, 1);
    setState(272);
    antlrcpp::downCast<UpdateContext *>(_localctx)->lhs = match(pblangParser::ID);
    setState(273);
    match(pblangParser::T__27);
    setState(274);
    expression();
    setState(275);
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
  enterRule(_localctx, 42, pblangParser::RuleDefinition);
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
    match(pblangParser::T__29);
    setState(278);
    match(pblangParser::ID);
    setState(290);
    _errHandler->sync(this);

    _la = _input->LA(1);
    if (_la == pblangParser::T__30) {
      setState(279);
      match(pblangParser::T__30);
      setState(280);
      declaredParameter();
      setState(285);
      _errHandler->sync(this);
      _la = _input->LA(1);
      while (_la == pblangParser::T__31) {
        setState(281);
        match(pblangParser::T__31);
        setState(282);
        declaredParameter();
        setState(287);
        _errHandler->sync(this);
        _la = _input->LA(1);
      }
      setState(288);
      match(pblangParser::T__32);
    }
    setState(292);
    match(pblangParser::T__5);
    setState(297);
    _errHandler->sync(this);
    switch (_input->LA(1)) {
      case pblangParser::T__1: {
        setState(293);
        antlrcpp::downCast<DefinitionContext *>(_localctx)->builtin = match(pblangParser::T__1);
        break;
      }

      case pblangParser::T__30:
      case pblangParser::ID:
      case pblangParser::FLOAT: {
        setState(294);
        expression();
        setState(295);
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
  enterRule(_localctx, 44, pblangParser::RuleDeclaredParameter);

#if __cplusplus > 201703L
  auto onExit = finally([=, this] {
#else
  auto onExit = finally([=] {
#endif
    exitRule();
  });
  try {
    enterOuterAlt(_localctx, 1);
    setState(299);
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
  enterRule(_localctx, 46, pblangParser::RuleExpression);

#if __cplusplus > 201703L
  auto onExit = finally([=, this] {
#else
  auto onExit = finally([=] {
#endif
    exitRule();
  });
  try {
    enterOuterAlt(_localctx, 1);
    setState(301);
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
  enterRule(_localctx, 48, pblangParser::RuleAddition);
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
    multiplication();
    setState(308);
    _errHandler->sync(this);
    _la = _input->LA(1);
    while (_la == pblangParser::T__33

    || _la == pblangParser::T__34) {
      setState(304);
      _la = _input->LA(1);
      if (!(_la == pblangParser::T__33

      || _la == pblangParser::T__34)) {
      _errHandler->recoverInline(this);
      }
      else {
        _errHandler->reportMatch(this);
        consume();
      }
      setState(305);
      multiplication();
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
  enterRule(_localctx, 50, pblangParser::RuleMultiplication);
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
    exponentiation();
    setState(316);
    _errHandler->sync(this);
    _la = _input->LA(1);
    while (_la == pblangParser::T__35

    || _la == pblangParser::T__36) {
      setState(312);
      _la = _input->LA(1);
      if (!(_la == pblangParser::T__35

      || _la == pblangParser::T__36)) {
      _errHandler->recoverInline(this);
      }
      else {
        _errHandler->reportMatch(this);
        consume();
      }
      setState(313);
      exponentiation();
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
  enterRule(_localctx, 52, pblangParser::RuleExponentiation);
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
    modulo();
    setState(324);
    _errHandler->sync(this);
    _la = _input->LA(1);
    while (_la == pblangParser::T__37) {
      setState(320);
      match(pblangParser::T__37);
      setState(321);
      modulo();
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
  enterRule(_localctx, 54, pblangParser::RuleModulo);
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
    setState(327);
    primaryExpression();
    setState(332);
    _errHandler->sync(this);
    _la = _input->LA(1);
    while (_la == pblangParser::T__38) {
      setState(328);
      match(pblangParser::T__38);
      setState(329);
      primaryExpression();
      setState(334);
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
  enterRule(_localctx, 56, pblangParser::RulePrimaryExpression);
  size_t _la = 0;

#if __cplusplus > 201703L
  auto onExit = finally([=, this] {
#else
  auto onExit = finally([=] {
#endif
    exitRule();
  });
  try {
    setState(355);
    _errHandler->sync(this);
    switch (getInterpreter<atn::ParserATNSimulator>()->adaptivePredict(_input, 41, _ctx)) {
    case 1: {
      enterOuterAlt(_localctx, 1);
      setState(335);
      match(pblangParser::T__30);
      setState(336);
      expression();
      setState(337);
      match(pblangParser::T__32);
      break;
    }

    case 2: {
      enterOuterAlt(_localctx, 2);
      setState(339);
      match(pblangParser::FLOAT);
      break;
    }

    case 3: {
      enterOuterAlt(_localctx, 3);
      setState(340);
      match(pblangParser::ID);
      setState(352);
      _errHandler->sync(this);

      _la = _input->LA(1);
      if (_la == pblangParser::T__30) {
        setState(341);
        match(pblangParser::T__30);
        setState(342);
        expression();
        setState(347);
        _errHandler->sync(this);
        _la = _input->LA(1);
        while (_la == pblangParser::T__31) {
          setState(343);
          match(pblangParser::T__31);
          setState(344);
          expression();
          setState(349);
          _errHandler->sync(this);
          _la = _input->LA(1);
        }
        setState(350);
        match(pblangParser::T__32);
      }
      break;
    }

    case 4: {
      enterOuterAlt(_localctx, 4);
      setState(354);
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
