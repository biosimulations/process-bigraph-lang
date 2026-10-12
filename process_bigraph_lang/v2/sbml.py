"""
`describe-model` for SBML: a model file's interface as data (see `docs/v2/design.md`, section 5.6).

`describe_sbml` reads an SBML file with the standard library's XML parser (no libsbml, no process code) and
returns a `ModelHeader`: the model's time unit, compartments, species (as concentrations unless the species has
only substance units) and parameters, each with its value and its units composed from the model's unit
definitions in a pint-readable spelling, plus the counts a solver cares about (reactions, events, rules) and the
SBML level, version and packages. `to_dict` is the JSON form (`pblang-model/0`), which the CLI renders as the
`.pbl` model header (`print_model_header`).
"""

from __future__ import annotations

import json
import tempfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

MODEL_HEADER_VERSION = "pblang-model/0"

_KIND_SYMBOLS = {
    "litre": "L",
    "liter": "L",
    "mole": "mol",
    "second": "s",
    "gram": "g",
    "kilogram": "kg",
    "metre": "m",
    "meter": "m",
    "item": "count",
    "dimensionless": "dimensionless",
    "hertz": "Hz",
    "kelvin": "K",
    "joule": "J",
    "newton": "N",
    "pascal": "Pa",
    "watt": "W",
    "volt": "V",
    "ampere": "A",
    "coulomb": "C",
}
_SCALE_PREFIX = {3: "k", 2: "h", 1: "da", -1: "d", -2: "c", -3: "m", -6: "u", -9: "n", -12: "p", -15: "f"}
_TIME_MULTIPLES = {60.0: "min", 3600.0: "h", 86400.0: "day"}
_SBML_DEFAULTS = {"substance": "mol", "volume": "L", "time": "s", "area": "m**2", "length": "m"}


@dataclass
class Quantity:
    value: float | None
    units: str | None = None
    constant: bool = True


@dataclass
class SpeciesDecl:
    initial: float | None
    units: str | None
    kind: str  # concentration | amount
    compartment: str | None
    constant: bool = False


@dataclass
class ModelHeader:
    name: str
    source: str
    sbml_id: str | None = None
    level: int | None = None
    version: int | None = None
    packages: list[str] = field(default_factory=list)
    time_units: str | None = None
    compartments: dict[str, Quantity] = field(default_factory=dict)
    species: dict[str, SpeciesDecl] = field(default_factory=dict)
    parameters: dict[str, Quantity] = field(default_factory=dict)
    counts: dict[str, int] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": MODEL_HEADER_VERSION,
            "name": self.name,
            "source": self.source,
            "sbml": {"id": self.sbml_id, "level": self.level, "version": self.version, "packages": self.packages},
            "time_units": self.time_units,
            "compartments": {k: {"value": q.value, "units": q.units} for k, q in self.compartments.items()},
            "species": {
                k: {
                    "initial": s.initial,
                    "units": s.units,
                    "kind": s.kind,
                    "compartment": s.compartment,
                    "constant": s.constant,
                }
                for k, s in self.species.items()
            },
            "parameters": {
                k: {"value": q.value, "units": q.units, "constant": q.constant} for k, q in self.parameters.items()
            },
            "counts": dict(self.counts),
            "notes": list(self.notes),
        }


def describe_sbml(path: str | Path) -> ModelHeader:
    """The model header of an SBML file."""
    path = Path(path)
    root = ET.parse(path).getroot()
    model = root.find("{*}model")
    if model is None:
        raise ValueError(f"{path}: no <model> element")
    header = ModelHeader(name=_identifier(path.stem), source=path.name, sbml_id=model.get("id"))
    header.level, header.version = _int(root.get("level")), _int(root.get("version"))
    header.packages = sorted({_package(k) for k in root.attrib if k.endswith(":required")} - {""})
    unit_defs = {d.get("id", ""): _unit_text(d) for d in model.findall("{*}listOfUnitDefinitions/{*}unitDefinition")}

    def units(reference: str | None, default_key: str) -> str | None:
        if reference:
            return unit_defs.get(reference) or _KIND_SYMBOLS.get(reference, reference)
        return unit_defs.get(model.get(f"{default_key}Units") or default_key) or _SBML_DEFAULTS.get(default_key)

    header.time_units = units(None, "time")
    for c in model.findall("{*}listOfCompartments/{*}compartment"):
        dims = _int(c.get("spatialDimensions")) if c.get("spatialDimensions") else 3
        default = {3: "volume", 2: "area", 1: "length"}.get(dims or 3, "volume")
        header.compartments[c.get("id", "")] = Quantity(_float_or_none(c.get("size")), units(c.get("units"), default))
    for sp in model.findall("{*}listOfSpecies/{*}species"):
        name = sp.get("id", "")
        compartment = sp.get("compartment")
        substance = units(sp.get("substanceUnits"), "substance")
        comp_units = (
            header.compartments[compartment].units if compartment in header.compartments else units(None, "volume")
        )
        only_substance = sp.get("hasOnlySubstanceUnits") == "true"
        if only_substance:
            initial, kind, unit_text = _float_or_none(sp.get("initialAmount")), "amount", substance
        elif sp.get("initialConcentration") is not None:
            initial, kind, unit_text = (
                _float_or_none(sp.get("initialConcentration")),
                "concentration",
                _ratio(substance, comp_units),
            )
        else:
            amount = _float_or_none(sp.get("initialAmount"))
            size = header.compartments[compartment].value if compartment in header.compartments else None
            initial = amount / size if amount is not None and size else amount
            kind, unit_text = "concentration", _ratio(substance, comp_units)
            if amount is not None and size:
                header.notes.append(
                    f"species {name}: initial amount {amount:g} converted to concentration by compartment size {size:g}"
                )
        header.species[name] = SpeciesDecl(initial, unit_text, kind, compartment, constant=sp.get("constant") == "true")
    for pr in model.findall("{*}listOfParameters/{*}parameter"):
        header.parameters[pr.get("id", "")] = Quantity(
            _float_or_none(pr.get("value")),
            units(pr.get("units"), "") if pr.get("units") else None,
            pr.get("constant") != "false",
        )
    header.counts = {
        "reactions": len(model.findall("{*}listOfReactions/{*}reaction")),
        "events": len(model.findall("{*}listOfEvents/{*}event")),
        "rules": len(model.findall("{*}listOfRules/*")),
        "function_definitions": len(model.findall("{*}listOfFunctionDefinitions/{*}functionDefinition")),
    }
    return header


def print_model_header(header: ModelHeader) -> str:
    """The `.pbl` model header: a generated declaration to `import`, not a composite (rendered by the CLI)."""
    from process_bigraph_lang.v2.langium import run_cli

    with tempfile.TemporaryDirectory() as tmp:
        source = Path(tmp) / "model.json"
        source.write_text(json.dumps(header.to_dict()), encoding="utf-8")
        return run_cli("model-header", str(source)).stdout


# --- helpers -----------------------------------------------------------------------------------------------------


def _unit_text(definition: ET.Element) -> str:
    parts = []
    for unit in definition.findall("{*}listOfUnits/{*}unit"):
        kind = unit.get("kind", "dimensionless")
        symbol = _KIND_SYMBOLS.get(kind, kind)
        scale = _int(unit.get("scale")) or 0
        multiplier = _float_or_none(unit.get("multiplier")) or 1.0
        exponent = _float_or_none(unit.get("exponent")) or 1.0
        if symbol == "dimensionless" and multiplier == 1.0 and scale == 0:
            continue
        if symbol == "s" and scale == 0 and multiplier in _TIME_MULTIPLES:
            text = _TIME_MULTIPLES[multiplier]
        elif multiplier == 1.0 and scale in _SCALE_PREFIX and symbol != "dimensionless":
            text = f"{_SCALE_PREFIX[scale]}{symbol}"
        elif multiplier == 1.0 and scale == 0:
            text = symbol
        else:
            text = f"({multiplier:g}e{scale} * {symbol})"
        if exponent != 1.0:
            text += f"**{exponent:g}"
        parts.append(text)
    return " * ".join(parts) if parts else "dimensionless"


def _ratio(numerator: str | None, denominator: str | None) -> str | None:
    if not numerator:
        return None
    if not denominator or denominator == "dimensionless":
        return numerator
    return f"{numerator} / {denominator}" if " " not in denominator else f"{numerator} / ({denominator})"


def _package(attribute: str) -> str:
    return attribute.split("}")[0].lstrip("{").rsplit("/", 2)[-2] if "}" in attribute else ""


def _identifier(text: str) -> str:
    cleaned = "".join(c if c.isalnum() or c == "_" else "_" for c in text)
    return cleaned if cleaned and not cleaned[0].isdigit() else f"m_{cleaned}"


def _int(text: str | None) -> int | None:
    try:
        return int(text) if text is not None else None
    except ValueError:
        return None


def _float_or_none(text: str | None) -> float | None:
    try:
        return float(text) if text is not None else None
    except ValueError:
        return None
