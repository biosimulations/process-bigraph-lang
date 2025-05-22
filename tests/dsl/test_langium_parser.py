from pathlib import Path
from typing import cast

from process_bigraph_lang.dsl.ast_model import (
    ASTModel,
    BinaryExpression,
    VariableRef,
)
from process_bigraph_lang.dsl.bind_ast import bind_ast_model
from process_bigraph_lang.dsl.langium_pblang import _langium_generate


def test_simple(simple_parse_data_1: tuple[str, Path, ASTModel]) -> None:
    _dsl_str, dsl_path, expected_model = simple_parse_data_1
    generated_json = _langium_generate(dsl_path)
    model = ASTModel.model_validate_json(generated_json)
    assert model == expected_model
    bind_ast_model(model)
    ref_object = cast(VariableRef, cast(BinaryExpression, model.definitions[0].expr).left).variable.ref_object
    assert ref_object is model.definitions[0].args[0]


def test_square(simple_parse_data_2: tuple[str, Path, ASTModel]) -> None:
    _dsl_str, dsl_path, expected_model = simple_parse_data_2
    generated_json = _langium_generate(dsl_path)
    model = ASTModel.model_validate_json(generated_json)
    assert model == expected_model


def test_types_units_defs(simple_parse_data_3: tuple[str, Path, ASTModel]) -> None:
    _dsl_lang, dsl_path, expected_model = simple_parse_data_3
    generated_json = _langium_generate(dsl_path)
    model = ASTModel.model_validate_json(generated_json)
    assert model.model_dump_json(indent=2) == expected_model.model_dump_json(indent=2)
