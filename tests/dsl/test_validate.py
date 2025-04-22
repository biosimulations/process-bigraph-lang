from pathlib import Path

from process_bigraph_lang.dsl.validate import validate_file


def test_validate_abc(model_path_abc: Path) -> None:
    stdout, stderr = validate_file(model_path_abc)
    assert stderr == ""
    assert stdout.startswith("Parsed and validated ")
    assert stdout.endswith("successfully!")


def test_validate_abc_should_fail(model_path_abc_error: Path) -> None:
    stdout, stderr = validate_file(model_path_abc_error)
    assert stderr == (
        "There are validation errors:\n"
        "line 25: Could not resolve reference to SchemaItem named 'calciumaaa'. "
        "[calciumaaa]"
    )
    assert stdout == ""


def test_validate_spatio_flux(model_path_spatio_flux: Path) -> None:
    stdout, stderr = validate_file(model_path_spatio_flux)
    assert stderr == ""
    assert stdout.startswith("Parsed and validated ")
    assert stdout.endswith("successfully!")
