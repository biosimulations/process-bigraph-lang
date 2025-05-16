import os
from pathlib import Path

from process_bigraph_lang.antlr_dsl.generate import bind_model
from process_bigraph_lang.dsl import generate
from process_bigraph_lang.dsl.model import (
    Model,
)


def generateModelAst(pblang_file: os.PathLike[str]) -> Model:
    model_json: str = generate.generate_model(pblang_file)
    model: Model = Model.model_validate_json(model_json)
    bind_model(model)
    # result: str = model.model_dump_json(indent=4)
    # rich.print(result)
    return model


def test_parse_abc_with_process(model_paths_abc_processes: tuple[Path, Path]) -> None:
    pblang_path = model_paths_abc_processes[0]
    json_path = model_paths_abc_processes[1]

    # create the AST Model by parsing the pblang DSL
    parsed_ast_model: Model = generateModelAst(pblang_path)

    # read JSON from DSL in second argument of tuple
    with open(json_path, "r") as file:
        model_json = file.read()

    loaded_ast_model: Model = Model.model_validate_json(model_json)
    bind_model(loaded_ast_model)

    assert loaded_ast_model == parsed_ast_model


def test_parse_add_with_steps(model_paths_abc_steps: tuple[Path, Path]) -> None:
    pblang_path = model_paths_abc_steps[0]
    json_path = model_paths_abc_steps[1]

    # create the AST Model by parsing the pblang DSL
    parsed_ast_model: Model = generateModelAst(pblang_path)

    # read JSON from DSL in second argument of tuple
    with open(json_path, "r") as file:
        model_json = file.read()

    loaded_ast_model: Model = Model.model_validate_json(model_json)
    bind_model(loaded_ast_model)

    assert loaded_ast_model == parsed_ast_model
