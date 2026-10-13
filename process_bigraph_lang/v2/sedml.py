"""
`sedml describe`: what a SED-ML file asks for, as data (`docs/v2/sedml-plan.md`, step 1a).

`describe_sedml` reads a SED-ML file, or every SED-ML file of a COMBINE/OMEX archive, with the standard library's XML
parser (no libsedml) and returns a `SedmlDescription`: models with their attribute changes, uniform time courses with
their KiSAO algorithm, tasks, data generators, reports and plots. XPath targets are resolved to the SBML element they
name (`species PX`, `parameter k1`, `reaction R1`). `to_dict` is the JSON form (`pblang-sedml/0`), which the template
printer turns into one `.pblang` composite per task.

Version 1 covers uniform time course tasks, attribute changes, data generators that are linear combinations of
variables (`x`, `2 * x`, `x + y`), reports and plots. Everything else is listed in `unsupported`, with the element and
why, never dropped silently.
"""

from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
import zipfile
from dataclasses import asdict, dataclass, field
from pathlib import Path, PurePosixPath
from typing import Any

SEDML_DESCRIPTION_VERSION = "pblang-sedml/0"

SEDML_FORMAT = "http://identifiers.org/combine.specifications/sed-ml"
TIME_SYMBOL = "urn:sedml:symbol:time"
_MATHML = "{http://www.w3.org/1998/Math/MathML}"

# /sbml:sbml/sbml:model/sbml:listOfSpecies/sbml:species[@id='PX'] (and /@value, /@initialConcentration, ...)
_TARGET = re.compile(
    r"^/sbml:sbml/sbml:model/sbml:listOf(?P<list>\w+)/sbml:(?P<kind>\w+)"
    r"\[@id=(?P<q>['\"])(?P<id>[^'\"]+)(?P=q)\](?:/@(?P<attribute>\w+))?$"
)
_KINDS = {"species", "parameter", "compartment", "reaction"}


@dataclass
class Target:
    """An SBML element named by an XPath target: its kind (species, parameter, compartment, reaction), its id, and
    the attribute a change sets (`value`, `initialConcentration`, ...)."""

    kind: str
    id: str
    attribute: str | None = None


@dataclass
class Change:
    target: str
    new_value: float
    element: Target


@dataclass
class Model:
    id: str
    source: str
    language: str | None
    changes: list[Change] = field(default_factory=list)


@dataclass
class Algorithm:
    kisao: str
    name: str | None = None
    parameters: dict[str, str] = field(default_factory=dict)  # KiSAO id -> value, as written


@dataclass
class TimeCourse:
    """A uniform time course: from `initial_time`, output from `output_start` to `output_end` in `number_of_steps`
    equal steps (`number_of_steps + 1` points; SED-ML L1V1-3 call it `numberOfPoints`)."""

    id: str
    initial_time: float
    output_start: float
    output_end: float
    number_of_steps: int
    algorithm: Algorithm


@dataclass
class Task:
    id: str
    model: str
    simulation: str


@dataclass
class Variable:
    """A data generator's variable: the time symbol, or an SBML element of a task's model."""

    id: str
    task: str
    symbol: str | None = None
    element: Target | None = None


@dataclass
class Term:
    variable: str
    coefficient: float = 1.0


@dataclass
class DataGenerator:
    """A linear combination of variables: `sum(coefficient * variable)`."""

    id: str
    name: str | None
    variables: list[Variable]
    terms: list[Term]

    @property
    def tasks(self) -> set[str]:
        return {v.task for v in self.variables}


@dataclass
class DataSet:
    id: str
    label: str
    data_generator: str


@dataclass
class Report:
    id: str
    name: str | None
    data_sets: list[DataSet]


@dataclass
class Curve:
    id: str
    name: str | None
    x: str
    y: str
    log_x: bool = False
    log_y: bool = False


@dataclass
class Surface:
    id: str
    name: str | None
    x: str
    y: str
    z: str
    log_x: bool = False
    log_y: bool = False
    log_z: bool = False


@dataclass
class Plot:
    id: str
    name: str | None
    kind: str  # plot2D | plot3D
    curves: list[Curve] = field(default_factory=list)
    surfaces: list[Surface] = field(default_factory=list)


@dataclass
class Unsupported:
    """Something the file asks for that version 1 does not translate: which element, its id, and why."""

    element: str
    id: str | None
    reason: str


@dataclass
class SedmlFile:
    """One SED-ML file: where it is (its path in the archive), and what it asks for."""

    path: str
    level: int | None
    version: int | None
    models: list[Model] = field(default_factory=list)
    simulations: list[TimeCourse] = field(default_factory=list)
    tasks: list[Task] = field(default_factory=list)
    data_generators: list[DataGenerator] = field(default_factory=list)
    reports: list[Report] = field(default_factory=list)
    plots: list[Plot] = field(default_factory=list)
    unsupported: list[Unsupported] = field(default_factory=list)


@dataclass
class SedmlDescription:
    """Every SED-ML file of a source (one file, or an archive's), with the source's name."""

    source: str
    files: list[SedmlFile]

    def to_dict(self) -> dict[str, Any]:
        return {"schema_version": SEDML_DESCRIPTION_VERSION, **asdict(self)}

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2) + "\n"


def describe_sedml(path: str | Path) -> SedmlDescription:
    """What a `.sedml` file, or each SED-ML file of a COMBINE/OMEX archive, asks for."""
    path = Path(path)
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as archive:
            files = [_describe(name, archive.read(name)) for name in sedml_members(archive)]
        return SedmlDescription(source=path.name, files=files)
    return SedmlDescription(source=path.name, files=[_describe(path.name, path.read_bytes())])


def sedml_members(archive: zipfile.ZipFile) -> list[str]:
    """The SED-ML files of an archive: those its `manifest.xml` declares as SED-ML (master first), else every
    `*.sedml` member."""
    names = set(archive.namelist())
    if "manifest.xml" in names:
        root = ET.fromstring(archive.read("manifest.xml"))
        declared: list[tuple[bool, str]] = []
        for content in root.iter():
            if content.tag.rsplit("}", 1)[-1] != "content" or content.get("format", "").rstrip("/") != SEDML_FORMAT:
                continue
            location = str(PurePosixPath(content.get("location", "").removeprefix("./")))
            if location in names:
                declared.append((content.get("master") != "true", location))
        if declared:
            return [name for _, name in sorted(declared)]
    return sorted(n for n in names if n.lower().endswith(".sedml"))


# --- reading ------------------------------------------------------------------------------------------------------


def _describe(name: str, data: bytes) -> SedmlFile:
    root = ET.fromstring(data)
    if _local(root.tag) != "sedML":
        raise ValueError(f"{name}: not a SED-ML document (root element <{_local(root.tag)}>)")
    sed = SedmlFile(path=name, level=_int(root.get("level")), version=_int(root.get("version")))
    for element in _children(root, "listOfModels"):
        _model(sed, element)
    for element in _children(root, "listOfSimulations"):
        _simulation(sed, element)
    simulations = {s.id for s in sed.simulations}
    for element in _children(root, "listOfTasks"):
        _task(sed, element, simulations)
    tasks = {t.id for t in sed.tasks}
    for element in _children(root, "listOfDataGenerators"):
        _data_generator(sed, element, tasks)
    generators = {g.id: g for g in sed.data_generators}
    for element in _children(root, "listOfOutputs"):
        _output(sed, element, generators)
    return sed


def _model(sed: SedmlFile, element: ET.Element) -> None:
    model_id = element.get("id", "")
    language = element.get("language")
    if language is not None and "sbml" not in language:
        sed.unsupported.append(Unsupported("model", model_id, f"language {language}: only SBML models are translated"))
        return
    source = element.get("source", "")
    if source.startswith(("urn:", "http:", "https:")) or ":" in source.split("/", 1)[0]:
        sed.unsupported.append(Unsupported("model", model_id, f"source {source}: only files in the archive are read"))
        return
    model = Model(id=model_id, source=str(PurePosixPath(source.removeprefix("./"))), language=language)
    for change in _children(element, "listOfChanges"):
        kind = _local(change.tag)
        if kind != "changeAttribute":
            sed.unsupported.append(Unsupported(kind, model_id, "only changeAttribute changes are translated"))
            continue
        target = change.get("target", "")
        resolved = _target(target)
        value = _float(change.get("newValue"))
        if resolved is None or resolved.attribute is None or value is None:
            sed.unsupported.append(
                Unsupported(kind, model_id, f"target {target!r}: not an attribute of an SBML element by id")
            )
            continue
        model.changes.append(Change(target=target, new_value=value, element=resolved))
    sed.models.append(model)


def _simulation(sed: SedmlFile, element: ET.Element) -> None:
    kind = _local(element.tag)
    sim_id = element.get("id", "")
    if kind != "uniformTimeCourse":
        sed.unsupported.append(Unsupported(kind, sim_id, "only uniform time courses are translated"))
        return
    steps = _int(element.get("numberOfSteps") or element.get("numberOfPoints"))
    algorithm = element.find("{*}algorithm")
    numbers = [_float(element.get(a)) for a in ("initialTime", "outputStartTime", "outputEndTime")]
    if steps is None or algorithm is None or any(n is None for n in numbers):
        sed.unsupported.append(Unsupported(kind, sim_id, "incomplete: times, number of steps and algorithm needed"))
        return
    initial, start, end = (float(n) for n in numbers if n is not None)
    parameters = {p.get("kisaoID", ""): p.get("value", "") for p in _children(algorithm, "listOfAlgorithmParameters")}
    sed.simulations.append(
        TimeCourse(
            id=sim_id,
            initial_time=initial,
            output_start=start,
            output_end=end,
            number_of_steps=steps,
            algorithm=Algorithm(kisao=algorithm.get("kisaoID", ""), name=algorithm.get("name"), parameters=parameters),
        )
    )


def _task(sed: SedmlFile, element: ET.Element, simulations: set[str]) -> None:
    kind = _local(element.tag)
    task_id = element.get("id", "")
    if kind != "task":
        sed.unsupported.append(Unsupported(kind, task_id, "only plain tasks are translated (no repeated tasks)"))
        return
    model, simulation = element.get("modelReference", ""), element.get("simulationReference", "")
    if simulation not in simulations:
        sed.unsupported.append(Unsupported("task", task_id, f"its simulation {simulation!r} is not translated"))
        return
    if model not in {m.id for m in sed.models}:
        sed.unsupported.append(Unsupported("task", task_id, f"its model {model!r} is not translated"))
        return
    sed.tasks.append(Task(id=task_id, model=model, simulation=simulation))


def _data_generator(sed: SedmlFile, element: ET.Element, tasks: set[str]) -> None:
    gen_id = element.get("id", "")
    variables: list[Variable] = []
    for v in _children(element, "listOfVariables"):
        task = v.get("taskReference", "")
        symbol, target = v.get("symbol"), v.get("target")
        if task not in tasks:
            sed.unsupported.append(Unsupported("dataGenerator", gen_id, f"variable of task {task!r}, not translated"))
            return
        if symbol is not None:
            if symbol != TIME_SYMBOL:
                sed.unsupported.append(Unsupported("dataGenerator", gen_id, f"symbol {symbol}: only time is read"))
                return
            variables.append(Variable(id=v.get("id", ""), task=task, symbol=symbol))
            continue
        resolved = _target(target or "")
        if resolved is None or resolved.attribute is not None or resolved.kind not in _KINDS:
            sed.unsupported.append(Unsupported("dataGenerator", gen_id, f"target {target!r}: not an SBML element"))
            return
        variables.append(Variable(id=v.get("id", ""), task=task, element=resolved))
    constants = {
        p.get("id", ""): value
        for p in _children(element, "listOfParameters")
        if (value := _float(p.get("value"))) is not None
    }
    math = element.find(f"{_MATHML}math")
    terms = _linear(math[0] if math is not None and len(math) else None, {v.id for v in variables}, constants)
    if terms is None or not variables:
        sed.unsupported.append(
            Unsupported("dataGenerator", gen_id, "only linear combinations of variables (x, 2*x, x+y) are translated")
        )
        return
    sed.data_generators.append(DataGenerator(id=gen_id, name=element.get("name"), variables=variables, terms=terms))


def _output(sed: SedmlFile, element: ET.Element, generators: dict[str, DataGenerator]) -> None:
    kind = _local(element.tag)
    out_id = element.get("id", "")
    if kind == "report":
        data_sets = [
            DataSet(
                id=d.get("id", ""),
                label=d.get("label") or d.get("id") or "",
                data_generator=d.get("dataReference", ""),
            )
            for d in _children(element, "listOfDataSets")
        ]
        missing = sorted({d.data_generator for d in data_sets} - set(generators))
        if missing:
            sed.unsupported.append(Unsupported("report", out_id, f"its data generators {missing} are not translated"))
            return
        sed.reports.append(Report(id=out_id, name=element.get("name"), data_sets=data_sets))
    elif kind in ("plot2D", "plot3D"):
        plot = Plot(id=out_id, name=element.get("name"), kind=kind)
        axis_log = {a: _axis_log(element, a) for a in ("xAxis", "yAxis", "zAxis")}
        for c in _children(element, "listOfCurves"):
            if _local(c.tag) != "curve":
                sed.unsupported.append(Unsupported(_local(c.tag), c.get("id"), "only curves are translated"))
                continue
            plot.curves.append(
                Curve(
                    id=c.get("id", ""),
                    name=c.get("name"),
                    x=c.get("xDataReference", ""),
                    y=c.get("yDataReference", ""),
                    log_x=_bool(c.get("logX")) or axis_log["xAxis"],
                    log_y=_bool(c.get("logY")) or axis_log["yAxis"],
                )
            )
        for s in _children(element, "listOfSurfaces"):
            plot.surfaces.append(
                Surface(
                    id=s.get("id", ""),
                    name=s.get("name"),
                    x=s.get("xDataReference", ""),
                    y=s.get("yDataReference", ""),
                    z=s.get("zDataReference", ""),
                    log_x=_bool(s.get("logX")) or axis_log["xAxis"],
                    log_y=_bool(s.get("logY")) or axis_log["yAxis"],
                    log_z=_bool(s.get("logZ")) or axis_log["zAxis"],
                )
            )
        used = {r for c in plot.curves for r in (c.x, c.y)} | {r for s in plot.surfaces for r in (s.x, s.y, s.z)}
        missing = sorted(used - set(generators))
        if missing:
            sed.unsupported.append(Unsupported(kind, out_id, f"its data generators {missing} are not translated"))
            return
        sed.plots.append(plot)
    else:
        sed.unsupported.append(Unsupported(kind, out_id, "only reports and plots are translated"))


def _linear(node: ET.Element | None, variables: set[str], constants: dict[str, float]) -> list[Term] | None:
    """MathML that is a linear combination of variables, as terms; None for anything else."""
    if node is None:
        return None
    tag = _local(node.tag)
    if tag == "ci":
        name = (node.text or "").strip()
        return [Term(variable=name)] if name in variables else None
    if tag != "apply" or not len(node):
        return None
    op, args = _local(node[0].tag), list(node)[1:]
    if op == "plus":
        terms: list[Term] = []
        for arg in args:
            part = _linear(arg, variables, constants)
            if part is None:
                return None
            terms.extend(part)
        return terms
    if op == "minus" and len(args) in (1, 2):
        parts = [_linear(arg, variables, constants) for arg in args]
        if any(p is None for p in parts):
            return None
        first, *rest = [p for p in parts if p is not None]
        negated = [Term(t.variable, -t.coefficient) for t in (first if not rest else rest[0])]
        return negated if not rest else first + negated
    if op in ("times", "divide") and len(args) == 2:
        if op == "divide":
            divisor = _constant(args[1], constants)
            inner = _linear(args[0], variables, constants)
            if divisor is None or divisor == 0.0 or inner is None:
                return None
            return [Term(t.variable, t.coefficient / divisor) for t in inner]
        for scale_node, other in ((args[0], args[1]), (args[1], args[0])):
            scale = _constant(scale_node, constants)
            inner = _linear(other, variables, constants)
            if scale is not None and inner is not None:
                return [Term(t.variable, t.coefficient * scale) for t in inner]
    return None


def _constant(node: ET.Element, constants: dict[str, float]) -> float | None:
    tag = _local(node.tag)
    if tag == "cn":
        return _float((node.text or "").strip())
    if tag == "ci":
        return constants.get((node.text or "").strip())
    return None


def _target(target: str) -> Target | None:
    match = _TARGET.match(target.strip())
    if match is None:
        return None
    kind = match.group("kind")
    if kind not in _KINDS:
        return None
    return Target(kind=kind, id=match.group("id"), attribute=match.group("attribute"))


def _axis_log(plot: ET.Element, axis: str) -> bool:
    element = plot.find(f"{{*}}{axis}")
    return element is not None and element.get("type") == "log10"


# --- helpers -----------------------------------------------------------------------------------------------------


def _children(element: ET.Element, list_name: str) -> list[ET.Element]:
    found = element.find(f"{{*}}{list_name}")
    return list(found) if found is not None else []


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _int(value: str | None) -> int | None:
    try:
        return int(value) if value is not None else None
    except ValueError:
        return None


def _float(value: str | None) -> float | None:
    try:
        return float(value) if value is not None else None
    except ValueError:
        return None


def _bool(value: str | None) -> bool:
    return value is not None and value.lower() == "true"
