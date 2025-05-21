from pathlib import Path

from process_bigraph_lang.dsl.antlr_pblang import parse_pblang_str
from process_bigraph_lang.dsl.ast_model import ASTModel


def test_simple_parse_bind(simple_parse_data_1: tuple[str, Path, ASTModel]) -> None:
    dsl_str, _dsl_path, expected_model = simple_parse_data_1
    model = parse_pblang_str(dsl_str)
    # round trip to JSON to clear ref_objects
    model_json = model.model_dump_json(indent=2)
    model = ASTModel.model_validate_json(model_json)
    assert model == expected_model


def test_square_parse_bind(simple_parse_data_2: tuple[str, Path, ASTModel]) -> None:
    dsl_str, _dsl_path, expected_model = simple_parse_data_2
    model = parse_pblang_str(dsl_str)
    # round trip to JSON to clear ref_objects
    model_json = model.model_dump_json(indent=2)
    model = ASTModel.model_validate_json(model_json)
    assert model == expected_model


def test_types_units_defs_parse_bind(simple_parse_data_3: tuple[str, Path, ASTModel]) -> None:
    dsl_str, _dsl_path, expected_model = simple_parse_data_3
    model = parse_pblang_str(dsl_str)
    assert model.model_dump_json(indent=2) == expected_model.model_dump_json(indent=2)


def test_processes_parse_only(simple_parse_data_4: tuple[str, Path, ASTModel]) -> None:
    dsl_str, _dsl_path, expected_model = simple_parse_data_4
    _model = parse_pblang_str(dsl_str)
    assert _model.model_dump_json(indent=2) == expected_model.model_dump_json(indent=2)
