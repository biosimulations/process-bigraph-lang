"""SED-ML tasks as `.pblang` composites, one per solver (docs/v2/sedml-plan.md, steps 1b to 1d): the template, each
instance checked and compiled against the solvers' environment manifest, the archive a run takes, and each finding."""

import io
import json
import zipfile
from pathlib import Path

import pytest
import yaml

from process_bigraph_lang.v2 import Printed
from process_bigraph_lang.v2.__main__ import main
from process_bigraph_lang.v2.api import CompileError
from process_bigraph_lang.v2.check import check_text
from process_bigraph_lang.v2.langium import langium_cli
from process_bigraph_lang.v2.sedml_translate import (
    Solver,
    compile_instance,
    instance_archive,
    solvers_from,
    translate,
)
from tests.v2.helpers import assert_snapshot

pytestmark = pytest.mark.skipif(langium_cli() is None, reason="no Langium CLI (build dsl/ or install cli-native)")

DATA = Path(__file__).resolve().parent.parent / "fixtures" / "data" / "v2"
SEDML = DATA / "sedml"
MANIFEST = DATA / "interfaces" / "registry_env_pbsim.manifest.json"
SNAPSHOTS = SEDML / "snapshots"  # generated text: checked, but not the printer's fixpoints
SOLVERS = solvers_from(yaml.safe_load((SEDML / "solvers.yaml").read_text())["solvers"])


def omex(folder: Path, tmp_path: Path) -> Path:
    path = tmp_path / f"{folder.name}.omex"
    with zipfile.ZipFile(path, "w") as archive:
        for file in sorted(folder.iterdir()):
            archive.write(file, file.name)
    return path


def test_repressilator_template_and_instances(tmp_path: Path) -> None:
    (task,) = translate(omex(SEDML / "BIOMD0000000012", tmp_path), SOLVERS).tasks
    assert (task.task, task.name, sorted(task.instances)) == ("task1", "task1", ["copasi", "tellurium"])
    assert list(task.models) == ["BIOMD0000000012_url.xml"]  # no changes: the model as it is
    assert_snapshot("BIOMD0000000012.task1", Printed(task.template), SNAPSHOTS)
    assert_snapshot("BIOMD0000000012.task1.copasi", Printed(task.instances["copasi"]), SNAPSHOTS)
    # the template is checked against its own role: only the open site is reported
    assert [d.code for d in check_text(task.template)] == ["I300"]
    # rule-defined parameters and reaction rates are not in the generic solvers' results
    x404 = [f for f in task.findings if f.code == "X404" and f.solver == "copasi"]
    assert [f.message.split(" ", 1)[0] for f in x404] == ["9", "12"]
    assert "auto_dg_for_task1_Reaction1" not in task.instances["copasi"]
    assert "auto_dg_for_task1_PX" in task.instances["copasi"]


def test_ciliberto_changes_are_applied_to_a_copy(tmp_path: Path) -> None:
    (task,) = translate(omex(SEDML / "Ciliberto2003", tmp_path), SOLVERS).tasks
    (name,) = task.models
    assert name == "BIOMD0000000297_url.changed.xml"
    changed = task.models[name].decode()
    assert 'id="kswe_prime"' in changed and 'value="2.001"' in changed
    assert '"parameter:kswe_prime/value" = 2.001' in task.instances["tellurium"]
    assert_snapshot("Ciliberto2003.task_1.tellurium", Printed(task.instances["tellurium"]), SNAPSHOTS)
    # COPASI runs its LSODA hybrid where CVODE was asked for: a warning, not a refusal
    (x405,) = [f for f in task.findings if f.code == "X405"]
    assert x405.solver == "copasi" and "CVODE" in x405.message and "copasi" in task.instances


def test_instances_compile_against_the_environment_with_registered_addresses(tmp_path: Path) -> None:
    (task,) = translate(omex(SEDML / "Ciliberto2003", tmp_path), SOLVERS).tasks
    for solver in ("copasi", "tellurium"):
        compiled = compile_instance(task, solver, [MANIFEST])
        state = compiled.document["state"]
        assert compiled.diagnostics == []
        assert state["simulate"]["address"].startswith("local:pbsim_common.simulators.")
        assert state["observe"]["address"] == "local:pbsim_sedml.DataGenerators"
        config = state["simulate"]["config"]
        assert (config["model_source"], config["time"], config["n_points"]) == (
            "BIOMD0000000297_url.changed.xml",
            140.0,
            201,
        )
        archive = zipfile.ZipFile(io.BytesIO(instance_archive(task, solver, compiled.document)))
        assert sorted(archive.namelist()) == ["BIOMD0000000297_url.changed.xml", "task_1.pbg", "task_1.pblang"]


def test_a_solver_that_does_not_fit_the_role_is_refused_by_the_checker(tmp_path: Path) -> None:
    steady = Solver("steady", "local:pbsim_common.simulators.copasi_process.CopasiSteadyStateStep", ("KISAO:0000560",))
    (task,) = translate(omex(SEDML / "Ciliberto2003", tmp_path), [steady]).tasks
    with pytest.raises(CompileError) as raised:
        compile_instance(task, "steady", [MANIFEST])
    found = {(d.code, d.path) for d in raised.value.diagnostics}
    assert ("S021", "simulate/outputs/result") in found  # it returns `results`, not the role's `result`
    assert ("S022", "simulate/config/n_points") in found


def _scenario(tmp_path: Path, **replace: str) -> Path:
    """out_of_scope.sedml with a model next to it, edited by `replace` (old text -> new)."""
    folder = tmp_path / "scenario"
    folder.mkdir()
    text = (SEDML / "out_of_scope.sedml").read_text()
    for old, new in replace.items():
        text = text.replace(old, new)
    (folder / "s.sedml").write_text(text)
    (folder / "model.xml").write_text(
        '<?xml version="1.0"?><sbml xmlns="http://www.sbml.org/sbml/level3/version2/core" level="3" version="2">'
        '<model id="m"><listOfCompartments><compartment id="c" size="1" constant="true"/></listOfCompartments>'
        '<listOfSpecies><species id="A" compartment="c" initialConcentration="1" hasOnlySubstanceUnits="false" '
        'boundaryCondition="false" constant="false"/><species id="B" compartment="c" initialConcentration="0" '
        'hasOnlySubstanceUnits="false" boundaryCondition="false" constant="false"/></listOfSpecies>'
        '<listOfParameters><parameter id="k" value="0.1" constant="true"/></listOfParameters></model></sbml>'
    )
    return folder / "s.sedml"


def test_output_start_drops_the_leading_points(tmp_path: Path) -> None:
    translation = translate(_scenario(tmp_path), SOLVERS)
    assert {f.code for f in translation.findings} == {"X400"}  # describe's unsupported list
    (task,) = translation.tasks
    # output 5..20 in 30 steps: a grid of 40 steps from 0, the first 10 dropped
    text = task.instances["tellurium"]
    assert "n_points = 41" in text and "skip = 10" in text and "time = 20.0" in text
    changed = task.models["model.changed.xml"].decode()
    assert 'initialConcentration="2.5"' in changed


@pytest.mark.parametrize(
    ("replace", "code", "refused"),
    [
        ({'initialTime="0"': 'initialTime="1"'}, "X402", True),
        ({'numberOfSteps="30"': 'numberOfSteps="7"'}, "X403", True),
        ({'kisaoID="KISAO:0000019"': 'kisaoID="KISAO:0000029"'}, "X406", True),  # Gillespie: not an ODE solver
        ({"species[@id='A']/@initialConcentration": "species[@id='Q']/@initialConcentration"}, "X401", True),
    ],
)
def test_findings_that_refuse_a_solver(tmp_path: Path, replace: dict[str, str], code: str, refused: bool) -> None:
    (task,) = translate(_scenario(tmp_path, **replace), SOLVERS).tasks
    assert code in {f.code for f in task.findings}
    assert (task.instances == {}) is refused


def test_the_cli_writes_texts_models_archives_and_findings(tmp_path: Path) -> None:
    out = tmp_path / "out"
    code = main([
        "sedml",
        "translate",
        str(omex(SEDML / "Ciliberto2003", tmp_path)),
        "--solvers",
        str(SEDML / "solvers.yaml"),
        "-i",
        str(MANIFEST),
        "-o",
        str(out),
    ])
    assert code == 0
    assert sorted(p.name for p in out.iterdir()) == [
        "BIOMD0000000297_url.changed.xml",
        "findings.json",
        "task_1.copasi.omex",
        "task_1.copasi.pblang",
        "task_1.pblang",
        "task_1.tellurium.omex",
        "task_1.tellurium.pblang",
    ]
    findings = json.loads((out / "findings.json").read_text())
    assert [(f["code"], f["solver"]) for f in findings] == [("X405", "copasi")]
