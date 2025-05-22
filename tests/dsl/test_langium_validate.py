from pathlib import Path

from process_bigraph_lang.dsl.langium_pblang import _langium_validate


def test_validate_abc(model_path_abc: Path) -> None:
    stdout, stderr = _langium_validate(model_path_abc)
    assert stderr == ""
    assert stdout.startswith("Parsed and validated ")
    assert stdout.endswith("successfully!")


def test_validate_abc_should_fail(model_path_abc_error: Path) -> None:
    stdout, stderr = _langium_validate(model_path_abc_error)
    assert stderr == (
        "There are validation errors:\n"
        "line 22: Could not resolve reference to SchemaItem named 'calciumaaa'. "
        "[calciumaaa]"
    )
    assert stdout == ""


def test_validate_add_floats(model_add_floats: Path) -> None:
    stdout, stderr = _langium_validate(model_add_floats)
    assert stderr == ""
    assert stdout.startswith("Parsed and validated ")
    assert stdout.endswith("successfully!")


def test_validate_dfba_single(model_dfba_single: Path) -> None:
    stdout, stderr = _langium_validate(model_dfba_single)
    assert stderr == ""
    assert stdout.startswith("Parsed and validated ")
    assert stdout.endswith("successfully!")
