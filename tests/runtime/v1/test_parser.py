import os
from pathlib import Path

from process_bigraph_lang.antlr_dsl.generate import bind_model
from process_bigraph_lang.dsl import generate
from process_bigraph_lang.dsl.model import (
    Model as ASTModel,
)


def _generateModelAst(pblang_file: os.PathLike[str]) -> ASTModel:
    model_json: str = generate.generate_model(pblang_file)
    model: ASTModel = ASTModel.model_validate_json(model_json)
    bind_model(model)
    # result: str = model.model_dump_json(indent=4)
    # rich.print(result)
    return model


def test_parse_add_floats_with_process(model_paths_add_floats_processes: tuple[Path, Path]) -> None:
    pblang_path = model_paths_add_floats_processes[0]
    ast_json_path = model_paths_add_floats_processes[1]

    # create the AST Model by parsing the pblang DSL
    parsed_ast_model: ASTModel = _generateModelAst(pblang_path)

    # read JSON from DSL in second argument of tuple
    with open(ast_json_path, "r") as file:
        ast_model_json = file.read()

    loaded_ast_model: ASTModel = ASTModel.model_validate_json(ast_model_json)
    bind_model(loaded_ast_model)

    assert loaded_ast_model == parsed_ast_model


def test_parse_add_with_steps(model_paths_add_floats_steps: tuple[Path, Path]) -> None:
    pblang_path = model_paths_add_floats_steps[0]
    ast_json_path = model_paths_add_floats_steps[1]

    # create the AST Model by parsing the pblang DSL
    parsed_ast_model: ASTModel = _generateModelAst(pblang_path)

    # read JSON from DSL in second argument of tuple
    with open(ast_json_path, "r") as file:
        ast_model_json = file.read()

    loaded_ast_model: ASTModel = ASTModel.model_validate_json(ast_model_json)
    bind_model(loaded_ast_model)

    assert loaded_ast_model == parsed_ast_model
