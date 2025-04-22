from pathlib import Path

from process_bigraph_lang.dsl.validate import validate_file


def test_validate_abc(model_path_abc: Path) -> None:
    stdout, stderr = validate_file(model_path_abc)
    assert stderr == ""
    assert stdout == (
        "Parsing and validating file: "
        "/Users/jimschaff/Documents/workspace/process-bigraph-lang/tests/fixtures/models/abc_model.pblang\n"
    )


def test_validate_abc_should_fail(model_path_abc_error: Path) -> None:
    stdout, stderr = validate_file(model_path_abc_error)
    assert stderr == ""
    assert stdout == (
        "Parsing and validating file: "
        "/Users/jimschaff/Documents/workspace/process-bigraph-lang/tests/fixtures/models/abc_model.pblang\n"
    )


def test_validate_spatio_flux(model_path_spatio_flux: Path) -> None:
    stdout, stderr = validate_file(model_path_spatio_flux)
    assert stderr == ""
    assert stdout == (
        "Parsing and validating file: "
        "/Users/jimschaff/Documents/workspace/process-bigraph-lang/tests/fixtures/models/abc_model.pblang\n"
    )
