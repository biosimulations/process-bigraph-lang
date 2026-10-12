"""Model declarations: headers generated from SBML, sorts stating requirements, and admission of one by the other."""

from pathlib import Path

from process_bigraph_lang.v2 import write_document
from process_bigraph_lang.v2.check import check_document
from process_bigraph_lang.v2.langium import langium_cli, read_text
from process_bigraph_lang.v2.printer import print_model
from process_bigraph_lang.v2.sbml import describe_sbml, print_model_header
import pytest
from tests.v2.helpers import SNAPSHOTS

pytestmark = pytest.mark.skipif(langium_cli() is None, reason="no Langium CLI (build dsl/ or install cli-native)")


CARAVAGNA = (
    Path(__file__).resolve().parent.parent / "fixtures" / "data" / "compiler" / "Caravagna2010" / "Caravagna2010.xml"
)
HEADER = print_model_header(describe_sbml(CARAVAGNA))


def _without_comments(text: str) -> str:
    return "\n".join(line for line in text.splitlines() if not line.strip().startswith("//"))


def _codes(text: str) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for d in check_document(read_text(text)):
        out.setdefault(d.code, []).append(d.path)
    return out


def test_generated_header_parses_and_prints_back() -> None:
    doc = read_text((SNAPSHOTS / "Caravagna2010.model.pbl").read_text(encoding="utf-8"))
    (header,) = doc.models
    assert header.name == "Caravagna2010" and header.source == "Caravagna2010.xml" and not header.is_sort
    assert header.time_units == "day" and set(header.species) == {"T", "E", "I"}
    t = header.species["T"]
    assert t.default == 1.0 and t.type is not None and t.type.units == "mmol / mL"  # type: ignore[union-attr]
    assert header.parameters["r2"].default == 0.18 and header.meta["kind"] == "concentration"
    assert _without_comments(print_model(header)) == _without_comments(HEADER)


SORT = """
model ODEModel {
  time @ "?T";
  species { _: float @ "?U"; ... }
  parameters { r2: float; mu2: float; ... }
  meta { events = 0, kind = "concentration" }
}
"""


def test_header_is_admitted_by_a_matching_sort() -> None:
    text = HEADER + SORT + "composite { store model : ODEModel = Caravagna2010; }\n"
    codes = _codes(text)
    assert not {"G300", "G301", "W201"} & set(codes), codes


def test_sort_requirements_are_enforced() -> None:
    missing = SORT.replace("parameters { r2: float; mu2: float; ... }", "parameters { r2: float; zz: float; ... }")
    codes = _codes(HEADER + missing + "composite { store model : ODEModel = Caravagna2010; }\n")
    assert codes.get("G301") == ["model/parameters/zz"]
    events = SORT.replace("events = 0", "events = 2")
    codes = _codes(HEADER + events + "composite { store model : ODEModel = Caravagna2010; }\n")
    assert codes.get("G301") == ["model/meta/events"]
    exact = SORT.replace("parameters { r2: float; mu2: float; ... }", "parameters { r2: float; }")
    codes = _codes(HEADER + exact + "composite { store model : ODEModel = Caravagna2010; }\n")
    assert codes.get("G301") == ["model/parameters"]  # the header has more parameters than an exact sort admits
    codes = _codes(HEADER + SORT + "composite { store model : ODEModel = Nope; }\n")
    assert codes.get("G300") == ["model"]


def test_sort_units_bind_across_the_header() -> None:
    # every species must be in one unit ?U and the time in ?T; a fixed-unit sort can disagree with the header
    fixed = SORT.replace('species { _: float @ "?U"; ... }', 'species { T: float @ "uM"; ... }')
    codes = _codes(HEADER + fixed + "composite { store model : ODEModel = Caravagna2010; }\n")
    assert codes.get("W201") == ["model/species/T"]  # mmol/mL is not uM: convertible, factor reported
    undeclared = SORT.replace("parameters { r2: float; mu2: float; ... }", 'parameters { r2: float @ "1/?T"; ... }')
    codes = _codes(HEADER + undeclared + "composite { store model : ODEModel = Caravagna2010; }\n")
    assert codes.get("I232") == [
        "model/parameters/r2"
    ]  # the model declares no units for r2: unknown, not dimensionless


def test_open_model_site_and_its_document_form() -> None:
    doc = read_text(SORT + "composite { store model : ODEModel = ?; }\n")
    codes = {d.code for d in check_document(doc)}
    assert "I301" in codes
    written = write_document(doc)
    site = written["state"]["model"]
    assert site["_type"] == "site" and site["_sort"]["species"] == {
        "_type": "map",
        "_value": {"_type": "float", "_units": "?U"},
    }
    assert "model" not in written["schema"]


def test_filled_model_site_expands_to_the_model_tree() -> None:
    doc = read_text(HEADER + SORT + "composite { store model : ODEModel = Caravagna2010; }\n")
    written = write_document(doc)
    assert written["state"]["model"]["species"]["T"] == 1.0 and written["state"]["model"]["parameters"]["r2"] == 0.18
    assert written["schema"]["model"]["species"]["T"] == {"_type": "float", "_units": "mmol / mL"}


def test_config_units_are_checked_against_params() -> None:
    text = """
param step: float @ "min" = 0.5;
process Engine { config { dt: float @ "?T"; } inputs { t: float @ "?T"; } outputs { } }
composite {
  store clock: float @ "s" = 0.0;
  process e : Engine at "local:Engine" { config { dt = ${step} } inputs { t -> clock } }
}
"""
    codes = _codes(text)
    assert codes.get("W201") == ["e/config/dt"]  # ?T is seconds (from the clock store) but the param is in minutes


def test_parse_errors_fail_loudly() -> None:
    import pytest

    with pytest.raises(RuntimeError, match="Langium CLI failed"):
        read_text("model Broken from { }")
