"""`describe-model`: an SBML file's interface as a generated model header, with no libsbml and no process code."""

import json
from pathlib import Path

from process_bigraph_lang.v2.printer import Printed
from process_bigraph_lang.v2.sbml import describe_sbml, print_model_header
from tests.v2.helpers import assert_snapshot

CARAVAGNA = (
    Path(__file__).resolve().parent.parent / "fixtures" / "data" / "compiler" / "Caravagna2010" / "Caravagna2010.xml"
)


def test_caravagna_header() -> None:
    header = describe_sbml(CARAVAGNA)
    assert header.name == "Caravagna2010" and header.sbml_id and header.sbml_id.startswith("Caravagna2010")
    assert (header.level, header.version) == (2, 4) and header.packages == []
    assert header.time_units and set(header.species) == {"T", "E", "I"}
    t = header.species["T"]
    assert t.initial == 1.0 and t.kind == "concentration" and t.compartment == "compartment"
    assert (
        t.units is not None and "mol" in t.units and "L" in t.units
    )  # substance per volume, from the unit definitions
    assert header.parameters["r2"].value == 0.18 and header.parameters["b"].value == 1e-9
    assert header.counts["reactions"] > 0 and header.counts["events"] == 0
    json.dumps(header.to_dict())  # plain data


def test_caravagna_header_snapshot() -> None:
    text = print_model_header(describe_sbml(CARAVAGNA))
    assert_snapshot("Caravagna2010.model", Printed(text))
    assert 'model Caravagna2010 from "Caravagna2010.xml" {' in text
    assert "species {" in text and "T: float @" in text and "parameters {" in text


def test_units_are_pint_readable() -> None:
    import pint

    header = describe_sbml(CARAVAGNA)
    registry = pint.UnitRegistry()
    units = [sp.units for sp in header.species.values()] + [c.units for c in header.compartments.values()]
    for text in units:
        if text:
            registry.parse_expression(text)
    assert (
        registry.parse_expression(header.time_units or "s").dimensionality
        == registry.parse_expression("s").dimensionality
    )


def test_amounts_and_substance_only_species(tmp_path: Path) -> None:
    sbml = """<?xml version="1.0" encoding="UTF-8"?>
<sbml xmlns="http://www.sbml.org/sbml/level3/version2/core" level="3" version="2">
  <model id="m" timeUnits="second" substanceUnits="mole" volumeUnits="litre">
    <listOfCompartments><compartment id="c" size="2" spatialDimensions="3" units="litre"/></listOfCompartments>
    <listOfSpecies>
      <species id="A" compartment="c" initialAmount="4" hasOnlySubstanceUnits="false"/>
      <species id="N" compartment="c" initialAmount="7" hasOnlySubstanceUnits="true" substanceUnits="item"/>
    </listOfSpecies>
    <listOfParameters><parameter id="k" value="0.5" units="second"/></listOfParameters>
  </model>
</sbml>"""
    path = tmp_path / "m.xml"
    path.write_text(sbml, encoding="utf-8")
    header = describe_sbml(path)
    assert (
        header.species["A"].initial == 2.0
        and header.species["A"].kind == "concentration"
        and header.species["A"].units == "mol / L"
    )
    assert (
        header.species["N"].initial == 7.0
        and header.species["N"].kind == "amount"
        and header.species["N"].units == "count"
    )
    assert header.parameters["k"].units == "s" and header.time_units == "s"
    assert any("converted to concentration" in n for n in header.notes)
    text = print_model_header(header)
    assert "// amount" in text or "amount" in text  # mixed kinds are annotated per species
