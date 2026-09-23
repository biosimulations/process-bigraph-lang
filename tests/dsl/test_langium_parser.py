from pathlib import Path

from process_bigraph_lang.dsl.ast_model import ASTModel, MemberCall, StructType, VarDef
from process_bigraph_lang.dsl.bind_ast import bind_ast_model
from process_bigraph_lang.dsl.langium_pblang import _langium_generate


def test_simple(simple_parse_data_1: tuple[str, Path, ASTModel]) -> None:
    _dsl_str, dsl_path, expected_model = simple_parse_data_1
    generated_json = _langium_generate(dsl_path)
    model = ASTModel.model_validate_json(generated_json)
    assert model == expected_model
    bind_ast_model(model)
    var_a, var_b = model.elements[1], model.elements[2]
    assert isinstance(var_b, VarDef) and isinstance(var_b.value, MemberCall)
    assert var_b.value.element.ref_object is var_a
    assert var_b.type.type.ref_object is model.elements[0]  # type: ignore[union-attr]


def test_member_access(simple_parse_data_2: tuple[str, Path, ASTModel]) -> None:
    _dsl_str, dsl_path, expected_model = simple_parse_data_2
    generated_json = _langium_generate(dsl_path)
    model = ASTModel.model_validate_json(generated_json)
    assert model == expected_model
    bind_ast_model(model)
    point, var_p, var_px = model.elements[1], model.elements[2], model.elements[3]
    assert isinstance(point, StructType) and isinstance(var_px, VarDef) and isinstance(var_px.value, MemberCall)
    assert var_px.value.element.ref_object is point.fields[0]
    assert var_px.value.previous is not None
    assert var_px.value.previous.element.ref_object is var_p


def test_types_units(simple_parse_data_3: tuple[str, Path, ASTModel]) -> None:
    _dsl_lang, dsl_path, expected_model = simple_parse_data_3
    generated_json = _langium_generate(dsl_path)
    model = ASTModel.model_validate_json(generated_json)
    assert model.model_dump_json(indent=2) == expected_model.model_dump_json(indent=2)
