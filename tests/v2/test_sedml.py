"""`sedml describe`: what a SED-ML file asks for, as data (docs/v2/sedml-plan.md, step 1a), from a file or an archive."""

import json
import zipfile
from pathlib import Path

from process_bigraph_lang.v2.__main__ import main
from process_bigraph_lang.v2.sedml import SEDML_DESCRIPTION_VERSION, Target, describe_sedml

SEDML = Path(__file__).resolve().parent.parent / "fixtures" / "data" / "v2" / "sedml"
BIOMD12 = SEDML / "BIOMD0000000012"
CILIBERTO = SEDML / "Ciliberto2003"


def omex(folder: Path, tmp_path: Path) -> Path:
    """The folder as a COMBINE archive (the corpus keeps its files unzipped, so diffs stay readable)."""
    path = tmp_path / f"{folder.name}.omex"
    with zipfile.ZipFile(path, "w") as archive:
        for file in sorted(folder.iterdir()):
            archive.write(file, file.name)
    return path


def test_biomodels_repressilator() -> None:
    (sed,) = describe_sedml(BIOMD12 / "BIOMD0000000012_url.sedml").files
    assert (sed.level, sed.version) == (1, 4) and sed.unsupported == []
    (model,) = sed.models
    assert model.source == "BIOMD0000000012_url.xml" and model.changes == []
    (utc,) = sed.simulations
    # L1V4 numberOfSteps: 1000 steps, 1001 points
    assert (utc.initial_time, utc.output_start, utc.output_end, utc.number_of_steps) == (0.0, 0.0, 10.0, 1000)
    assert utc.algorithm.kisao == "KISAO:0000694"
    assert [(t.id, t.model, t.simulation) for t in sed.tasks] == [("task1", "BIOMD0000000012_url", "auto_ten_seconds")]
    generators = {g.id: g for g in sed.data_generators}
    assert generators["auto_time_for_task1"].variables[0].symbol == "urn:sedml:symbol:time"
    px = generators["auto_dg_for_task1_PX"]
    assert px.variables[0].element == Target(kind="species", id="PX") and px.terms[0].coefficient == 1.0
    kinds = {g.variables[0].element.kind for g in sed.data_generators if g.variables[0].element}
    assert kinds == {"species", "parameter", "compartment", "reaction"}  # a report of every symbol with meaning
    (report,) = sed.reports
    assert len(report.data_sets) == 36 and report.data_sets[1].label == "PX"
    (plot,) = sed.plots
    assert plot.kind == "plot2D" and len(plot.curves) == 6


def test_ciliberto_morphogenesis_checkpoint() -> None:
    (sed,) = describe_sedml(CILIBERTO / "simulation_1.sedml").files
    assert (sed.level, sed.version) == (1, 3) and sed.unsupported == []
    (change,) = sed.models[0].changes
    assert change.element == Target(kind="parameter", id="kswe_prime", attribute="value") and change.new_value == 2.001
    (utc,) = sed.simulations
    assert (utc.output_end, utc.number_of_steps, utc.algorithm.kisao) == (140.0, 200, "KISAO:0000019")  # numberOfPoints
    swe1t = next(g for g in sed.data_generators if g.id == "data_gen_Swe1T")
    assert [t.coefficient for t in swe1t.terms] == [1.0] * 4 and len(swe1t.variables) == 4  # a sum of four species
    assert [(p.id, len(p.curves)) for p in sed.plots] == [
        ("Figure_3a", 4),
        ("Figure_3b", 4),
        ("Figure_3c", 4),
        ("Figure_3d", 1),
    ]


def test_an_archive_is_read_through_its_manifest(tmp_path: Path) -> None:
    from_file = describe_sedml(CILIBERTO / "simulation_1.sedml").files
    archived = describe_sedml(omex(CILIBERTO, tmp_path))
    assert archived.source == "Ciliberto2003.omex" and [f.path for f in archived.files] == ["simulation_1.sedml"]
    assert archived.files == from_file
    # without a manifest, every *.sedml member
    bare = tmp_path / "bare.omex"
    with zipfile.ZipFile(bare, "w") as archive:
        archive.write(BIOMD12 / "BIOMD0000000012_url.sedml", "sim/a.sedml")
        archive.writestr("notes.txt", "")
    assert [f.path for f in describe_sedml(bare).files] == ["sim/a.sedml"]


def test_what_version_one_does_not_translate_is_listed_never_dropped() -> None:
    (sed,) = describe_sedml(SEDML / "out_of_scope.sedml").files
    unsupported = {(u.element, u.id) for u in sed.unsupported}
    assert unsupported == {
        ("computeChange", "m"),
        ("model", "remote"),
        ("model", "cellml"),
        ("steadyState", "ss"),
        ("task", "t_ss"),  # its simulation is not translated
        ("repeatedTask", "scan"),
        ("dataGenerator", "a_squared"),
        ("dataGenerator", "steady_a"),  # a variable of an untranslated task
        ("report", "squared_report"),
        ("figure", "fig"),
    }
    # what remains is translatable
    (model,) = sed.models
    assert model.changes[0].element == Target(kind="species", id="A", attribute="initialConcentration")
    (utc,) = sed.simulations
    assert (utc.output_start, utc.number_of_steps, utc.algorithm.parameters) == (5.0, 30, {"KISAO:0000211": "1e-10"})
    assert [t.id for t in sed.tasks] == ["t"]
    scaled = next(g for g in sed.data_generators if g.id == "a_scaled")
    assert [(t.variable, t.coefficient) for t in scaled.terms] == [("v_a", 0.5), ("v_b", -0.25)]
    assert [r.id for r in sed.reports] == ["ok_report"]
    (plot,) = sed.plots
    assert plot.curves[0].log_y and not plot.curves[0].log_x  # from the L1V4 axis


def test_the_json_form_and_the_cli(tmp_path: Path, capsys: object) -> None:
    description = describe_sedml(CILIBERTO / "simulation_1.sedml")
    data = description.to_dict()
    assert data["schema_version"] == SEDML_DESCRIPTION_VERSION and data["source"] == "simulation_1.sedml"
    assert json.loads(description.to_json()) == data
    out = tmp_path / "d.json"
    assert main(["sedml", "describe", str(omex(CILIBERTO, tmp_path)), "-o", str(out)]) == 0
    written = json.loads(out.read_text())
    assert written["files"] == data["files"] and written["source"] == "Ciliberto2003.omex"


def test_a_file_that_is_not_sedml_is_refused(tmp_path: Path) -> None:
    sbml = tmp_path / "model.sedml"
    sbml.write_bytes((CILIBERTO / "BIOMD0000000297_url.xml").read_bytes())
    try:
        describe_sedml(sbml)
    except ValueError as e:
        assert "not a SED-ML document" in str(e)
    else:
        raise AssertionError("an SBML file was read as SED-ML")
