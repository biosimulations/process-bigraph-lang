from pathlib import Path

from process_bigraph_lang.antlr_dsl.generate import parse_str
from process_bigraph_lang.dsl.model import (
    Model,
)


def test_simple_parse_bind(simple_parse_data_1: tuple[str, Path, Model]) -> None:
    dsl_str, _dsl_path, expected_model = simple_parse_data_1
    model = parse_str(dsl_str)
    assert model == expected_model


def test_square_parse_bind(simple_parse_data_2: tuple[str, Path, Model]) -> None:
    dsl_str, _dsl_path, expected_model = simple_parse_data_2
    model = parse_str(dsl_str)
    assert model == expected_model


def test_types_units_defs_parse_bind(simple_parse_data_3: tuple[str, Path, Model]) -> None:
    dsl_str, _dsl_path, expected_model = simple_parse_data_3
    model = parse_str(dsl_str)
    assert model.model_dump_json(indent=2) == expected_model.model_dump_json(indent=2)


def test_processes_parse_only(simple_parse_data_4: tuple[str, Path, Model]) -> None:
    dsl_str, _dsl_path, expected_model = simple_parse_data_4
    _model = parse_str(dsl_str)
    assert _model.model_dump_json(indent=2) == expected_model.model_dump_json(indent=2)
