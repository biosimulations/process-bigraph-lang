import tempfile
from os import PathLike
from pathlib import Path

from antlr4 import FileStream, CommonTokenStream, ParseTreeWalker, Token
from antlr4.error.ErrorListener import ErrorListener

from process_bigraph_lang.antlr.pblangLexer import pblangLexer
from process_bigraph_lang.antlr.pblangParser import pblangParser
from process_bigraph_lang.antlr_dsl.antlr_ast_builder import ASTBuilderListener
from process_bigraph_lang.antlr_dsl.bind_ast import bind_model
from process_bigraph_lang.dsl.ast_model import ASTModel


class CustomErrorListener(ErrorListener):
    def syntaxError(
        self,
        recognizer: pblangParser | pblangLexer,
        offendingSymbol: Token | None,
        line: int,
        column: int,
        msg: str,
        e: Exception,
    ) -> None:
        raise ValueError(f"Syntax error at line {str(line)}, column {str(column)}: {msg}")


def parse_pblang_file(filename: PathLike[str]) -> ASTModel:
    file_path = Path(filename)
    if not file_path.exists():
        raise FileNotFoundError(filename)
    if not file_path.is_file():
        raise NotADirectoryError(filename)
    if not file_path.name.endswith(".pblang"):
        raise ValueError(f"File {filename} is not a .pblang file")
    if not file_path.is_absolute():
        raise ValueError(f"File {filename} is not an absolute path")

    input_stream = FileStream(fileName=str(file_path))
    lexer = pblangLexer(input_stream)
    lexer.removeErrorListeners()  # remove default ConsoleErrorListener
    lexer.addErrorListener(CustomErrorListener())  # add custom error listener
    stream = CommonTokenStream(lexer)
    parser = pblangParser(stream)
    parser.removeErrorListeners()  # remove default ConsoleErrorListener
    parser.addErrorListener(CustomErrorListener())  # add custom error listener
    tree = parser.model()
    listener = ASTBuilderListener()
    walker = ParseTreeWalker()
    walker.walk(listener, tree)
    model = listener.model
    bind_model(model)
    return model


def parse_pblang_str(pblang_str: str) -> ASTModel:
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir) / "test.pblang"
        with open(tmp_path, "w") as f:
            f.write(pblang_str)
            f.flush()
            return parse_pblang_file(tmp_path)
