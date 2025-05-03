#include "antlr4-runtime.h"
#include "MyGrammarLexer.h"
#include "MyGrammarParser.h"

int main() {
    std::ifstream stream("input.dsl");
    antlr4::ANTLRInputStream input(stream);
    MyGrammarLexer lexer(&input);
    antlr4::CommonTokenStream tokens(&lexer);
    MyGrammarParser parser(&tokens);
    parser.startRule();  // adjust to your top-level rule
}
