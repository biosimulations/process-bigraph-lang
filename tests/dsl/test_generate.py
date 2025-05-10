from pathlib import Path

from process_bigraph_lang.dsl.generate import generate_model
from process_bigraph_lang.dsl.model import (
    Model,
)


def test_simple(simple_parse_data_1: tuple[str, Path, Model]) -> None:
    _dsl_str, dsl_path, expected_model = simple_parse_data_1
    generated_json = generate_model(dsl_path)
    model = Model.model_validate_json(generated_json)
    assert model == expected_model


def test_square(simple_parse_data_2: tuple[str, Path, Model]) -> None:
    _dsl_str, dsl_path, expected_model = simple_parse_data_2
    generated_json = generate_model(dsl_path)
    model = Model.model_validate_json(generated_json)
    assert model == expected_model


def test_types_units_defs(simple_parse_data_3: tuple[str, Path, Model]) -> None:
    _dsl_lang, dsl_path, expected_model = simple_parse_data_3
    generated_json = generate_model(dsl_path)
    model = Model.model_validate_json(generated_json)
    assert model.model_dump_json(indent=2) == expected_model.model_dump_json(indent=2)


def test_processes(simple_parse_data_4: tuple[str, Path, Model]) -> None:
    _dsl_lang, dsl_path, expected_model = simple_parse_data_4
    generated_json = generate_model(dsl_path)
    model = Model.model_validate_json(generated_json)
    assert model.model_dump_json(indent=2) == expected_model.model_dump_json(indent=2)
