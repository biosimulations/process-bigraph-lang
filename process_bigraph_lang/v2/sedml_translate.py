"""
SED-ML tasks as `.pblang` composites, one per solver (`docs/v2/sedml-plan.md`, steps 1b to 1d).

A task of a SED-ML file becomes a composite of four steps:

- `simulate`, the solver: an open address site sorted by the `TimeCourseSolver` role in the **template**, the
  solver's own class (imported from its environment's manifest) in each **instance**, so the checker verifies the
  class's config and ports exactly as for any composite;
- `observe` (`DataGenerators`): the solver's result columns, constants and the time as the SED-ML data generators
  (linear combinations), with the points before the output start dropped;
- `report` (`Report`): one CSV per SED-ML report, `reports/<sedml>/<report>.csv`;
- `plots` (`Plots`): one Plotly figure per SED-ML plot, `plots/<sedml>/<plot>.plotly.json`.

The adapters are declared in the text itself, at their package's addresses, so each file is self-contained. Model
changes are constants, so they are applied here: the instance's solver reads a changed copy of the SBML, and the
text's `meta` lists each change. Nothing here builds a document: `compile_instance` compiles the text with the checker
(the CLI), as for any `.pblang`.

Findings use the `X4xx` codes (`FINDINGS`); an `error` finding for a solver means no instance for it.
"""

from __future__ import annotations

import io
import json
import math
import re
import xml.etree.ElementTree as ET
import zipfile
from dataclasses import dataclass, field
from functools import cache
from pathlib import Path, PurePosixPath
from typing import Any, Literal

from process_bigraph_lang.v2.api import AddressForm, Compiled, compile_text
from process_bigraph_lang.v2.sbml import ModelHeader, describe_sbml
from process_bigraph_lang.v2.sedml import (
    DataGenerator,
    SedmlFile,
    Task,
    TimeCourse,
    describe_sedml,
    sedml_members,
)

#: Where the SED-ML adapter steps are: biosim-toolkit (compose-api docs/plan-sedml.md, D11).
ADAPTERS_MODULE = "biosim_toolkit.sedml"
ODE_SOLVER = "KISAO:0000694"

Severity = Literal["error", "warning", "info"]

FINDINGS: dict[str, str] = {
    "X400": "a SED-ML element version 1 does not translate (listed by describe)",
    "X401": "a change or data generator names an element the model does not have",
    "X402": "the time course does not start at 0, where the generic solvers start",
    "X403": "the output grid is not a subset of the solver's grid from the initial time",
    "X404": "a data generator needs a variable the solver does not provide; its data sets are left out",
    "X405": "the solver runs a different ODE algorithm than the one asked for",
    "X406": "the solver implements no algorithm of the kind asked for",
}


@dataclass(frozen=True)
class Solver:
    """A filler of the `TimeCourseSolver` role: a class (by address) in an environment, the KiSAO terms it
    implements (its default first) and which kinds of SBML variable its result has columns for."""

    id: str
    address: str
    algorithms: tuple[str, ...]
    provides: frozenset[str] = frozenset({"species"})

    @property
    def module(self) -> str:
        return _module_path(self.address).rsplit(".", 1)[0]

    @property
    def class_name(self) -> str:
        return _module_path(self.address).rsplit(".", 1)[1]


def solvers_from(data: list[dict[str, Any]]) -> list[Solver]:
    """Solvers from plain data (`[{id, address, algorithms, provides?}]`, as compose-api's solvers.yaml lists them)."""
    return [
        Solver(
            id=str(d["id"]),
            address=str(d["address"]),
            algorithms=tuple(str(a) for a in d["algorithms"]),
            provides=frozenset(d.get("provides", ["species"])),
        )
        for d in data
    ]


@dataclass
class Finding:
    severity: Severity
    code: str
    message: str
    path: str  # sedml file / task / element
    solver: str | None = None


@dataclass
class TaskTranslation:
    """One SED-ML task: the template text, one instance text per accepted solver, the model files the instances
    read (by archive path), and every finding."""

    sedml: str
    task: str
    name: str
    template: str
    instances: dict[str, str] = field(default_factory=dict)
    models: dict[str, bytes] = field(default_factory=dict)
    findings: list[Finding] = field(default_factory=list)
    reports: list[str] = field(default_factory=list)
    plots: list[str] = field(default_factory=list)

    def refused(self, solver: str) -> list[Finding]:
        return [f for f in self.findings if f.severity == "error" and f.solver in (None, solver)]


@dataclass
class Translation:
    source: str
    tasks: list[TaskTranslation]
    findings: list[Finding] = field(default_factory=list)  # file-level: what describe could not translate


def translate(source: str | Path, solvers: list[Solver], output_dir: str = "/experiment/output") -> Translation:
    """Every task of a `.sedml` file, or of an archive's SED-ML files, as a template and one instance per solver.
    `output_dir` is where the job writes its files (the instances' adapters and solver write there)."""
    source = Path(source)
    files = _read_files(source)
    description = describe_sedml(source)
    translation = Translation(source=source.name, tasks=[])
    for sed in description.files:
        for u in sed.unsupported:
            translation.findings.append(
                Finding("warning", "X400", f"{u.element} {u.id or ''}: {u.reason}".replace("  ", " "), sed.path)
            )
        for task in sed.tasks:
            translation.tasks.append(_task(sed, task, files, solvers, output_dir))
    return translation


def compile_instance(
    task: TaskTranslation,
    solver: str,
    manifests: list[Path],
    addresses: AddressForm = "registered",
) -> Compiled:
    """The instance for `solver` compiled by the checker against `manifests` (the solver's environment)."""
    return compile_text(task.instances[solver], manifests=manifests, addresses=addresses)


def instance_archive(task: TaskTranslation, solver: str, document: dict[str, Any]) -> bytes:
    """The archive a run of `task` on `solver` takes: the compiled document (`<name>.pbg`), its text
    (`<name>.pblang`) and the model files it reads, at the top level where the runner finds them."""
    from process_bigraph_lang.v2.api import dumps

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(f"{task.name}.pbg", dumps(document))
        archive.writestr(f"{task.name}.pblang", task.instances[solver])
        for path, content in sorted(task.models.items()):
            archive.writestr(path, content)
    return buffer.getvalue()


# --- one task -----------------------------------------------------------------------------------------------------


def _task(
    sed: SedmlFile, task: Task, files: dict[str, bytes], solvers: list[Solver], output_dir: str
) -> TaskTranslation:
    where = f"{sed.path}/{task.id}"
    name = _identifier(task.id)
    out = TaskTranslation(sedml=sed.path, task=task.id, name=name, template="")
    model = next(m for m in sed.models if m.id == task.model)
    simulation = next(s for s in sed.simulations if s.id == task.simulation)
    sed_dir = PurePosixPath(sed.path).parent
    model_path = str(sed_dir / model.source) if str(sed_dir) != "." else model.source
    sbml = files.get(model_path)
    if sbml is None:
        out.findings.append(Finding("error", "X401", f"model file {model_path!r} is not in the archive", where))
        out.template = "// the model file is missing; nothing to translate\n"
        return out
    header = _header(model_path, sbml)

    # model changes, applied to a copy
    changed: dict[tuple[str, str], tuple[str, float]] = {}
    for change in model.changes:
        element = change.element
        if not _has(header, element.kind, element.id):
            out.findings.append(
                Finding("error", "X401", f"change of {element.kind} {element.id!r}: not in the model", where)
            )
            continue
        changed[(element.kind, element.id)] = (element.attribute or "value", change.new_value)
    model_file = PurePosixPath(model_path).name
    if changed:
        model_file = f"{PurePosixPath(model_path).stem}.changed{PurePosixPath(model_path).suffix or '.xml'}"
        out.models[model_file] = _apply_changes(sbml, changed)
    else:
        out.models[model_file] = sbml

    # the time course on the solvers' grid: from 0, every step, the output from its start
    grid = _grid(simulation, where, out.findings)

    # data generators of this task, and what each needs
    generators = [g for g in sed.data_generators if g.tasks == {task.id}]
    constants = _constants(header, changed)
    needs: dict[str, set[str]] = {}  # generator -> kinds of SBML variable it reads
    terms: dict[str, list[tuple[str, float]]] = {}
    for g in generators:
        resolved = _terms(g, header, constants, where, out.findings)
        if resolved is None:
            continue
        terms[g.id], needs[g.id] = resolved
    reports = [r for r in sed.reports if all(d.data_generator in terms for d in r.data_sets)]
    plots = [
        p
        for p in sed.plots
        if all(ref in terms for c in p.curves for ref in (c.x, c.y))
        and all(ref in terms for s in p.surfaces for ref in (s.x, s.y, s.z))
    ]
    out.reports, out.plots = [r.id for r in reports], [p.id for p in plots]
    sed_stem = _identifier(PurePosixPath(sed.path).stem)

    def text(solver: Solver | None) -> str:
        available = {g: t for g, t in terms.items() if solver is None or needs[g] <= solver.provides}
        return _print(
            sed=sed,
            task=task,
            simulation=simulation,
            name=name,
            model_file=model_file,
            changes=changed,
            grid=grid,
            generators=available,
            constants=constants,
            reports=reports,
            plots=plots,
            sed_stem=sed_stem,
            solver=solver,
            output_dir=output_dir,
        )

    out.template = text(None)
    for solver in solvers:
        before = len(out.findings)
        _algorithm(simulation, solver, where, out.findings)
        lacking: dict[str, list[str]] = {}
        for gen_id, kinds in needs.items():
            for kind in sorted(kinds - solver.provides):
                lacking.setdefault(kind, []).append(gen_id)
        for kind, gens in lacking.items():
            out.findings.append(
                Finding(
                    "warning",
                    "X404",
                    f"{len(gens)} data generator(s) read {kind} values that vary in time, which {solver.id} does not "
                    f"return; left out of its reports and plots: {', '.join(gens)}",
                    where,
                    solver.id,
                )
            )
        refused = any(f.severity == "error" and f.solver in (None, solver.id) for f in out.findings[before:]) or any(
            f.severity == "error" and f.solver is None for f in out.findings
        )
        if not refused:
            out.instances[solver.id] = text(solver)
    return out


@dataclass(frozen=True)
class _Grid:
    time: float  # the solver runs from 0 to here
    n_points: int  # on this many points
    skip: int  # of which the first `skip` precede the output start


def _grid(simulation: TimeCourse, where: str, findings: list[Finding]) -> _Grid:
    if simulation.initial_time != 0.0:
        findings.append(
            Finding(
                "error",
                "X402",
                f"simulation {simulation.id!r} starts at {simulation.initial_time}; the generic solvers start at 0",
                where,
            )
        )
    span = simulation.output_end - simulation.output_start
    total = simulation.output_end - simulation.initial_time
    steps = simulation.number_of_steps * total / span if span > 0 else math.nan
    if not math.isfinite(steps) or abs(steps - round(steps)) > 1e-6 * max(1.0, steps):
        findings.append(
            Finding(
                "error",
                "X403",
                f"simulation {simulation.id!r}: output from {simulation.output_start} to {simulation.output_end} in "
                f"{simulation.number_of_steps} steps is not on a grid from {simulation.initial_time}",
                where,
            )
        )
        steps = float(simulation.number_of_steps)
    n = round(steps)
    return _Grid(time=float(simulation.output_end), n_points=n + 1, skip=n - simulation.number_of_steps)


def _terms(
    g: DataGenerator,
    header: ModelHeader,
    constants: dict[str, float],
    where: str,
    findings: list[Finding],
) -> tuple[list[tuple[str, float]], set[str]] | None:
    """A data generator's terms as (variable, coefficient), the variable a result column, `time` or a constant;
    and the kinds of SBML variable the solver must return for it."""
    by_id = {v.id: v for v in g.variables}
    terms: list[tuple[str, float]] = []
    kinds: set[str] = set()
    for t in g.terms:
        v = by_id[t.variable]
        if v.symbol is not None:
            terms.append(("time", t.coefficient))
            continue
        assert v.element is not None
        kind, element_id = v.element.kind, v.element.id
        if kind != "reaction" and not _has(header, kind, element_id):
            findings.append(Finding("error", "X401", f"data generator {g.id!r}: no {kind} {element_id!r}", where))
            return None
        if kind in ("parameter", "compartment") and element_id in constants:
            terms.append((element_id, t.coefficient))
            continue
        terms.append((element_id, t.coefficient))
        kinds.add({"compartment": "parameter"}.get(kind, kind))
    return terms, kinds


def _algorithm(simulation: TimeCourse, solver: Solver, where: str, findings: list[Finding]) -> None:
    asked = simulation.algorithm.kisao
    runs = solver.algorithms[0]
    terms = _kisao()
    if asked in solver.algorithms or asked == ODE_SOLVER or asked in terms.get(runs, {}).get("ancestors", []):
        return
    if asked in terms:
        findings.append(
            Finding(
                "warning",
                "X405",
                f"{asked} ({terms[asked]['name']}) asked for; {solver.id} runs {runs} ({terms.get(runs, {}).get('name', '?')})",
                where,
                solver.id,
            )
        )
        return
    findings.append(
        Finding(
            "error", "X406", f"{asked} is not an ODE algorithm; {solver.id} runs ODE solvers only", where, solver.id
        )
    )


# --- printing -----------------------------------------------------------------------------------------------------

_ADAPTERS = f"""// The SED-ML adapters (docs/v2/sedml-plan.md): solver-agnostic steps around the solver.
step DataGenerators at "local:{ADAPTERS_MODULE}.DataGenerators" {{
  config {{
    generators: map<string, list<{{ variable: string; coefficient: float; }}>>;
    constants: map<string, float>;
    skip: int;
  }}
  inputs {{ result: numeric_result; }}
  outputs {{ data: overwrite<map<string, list<float>>>; }}
}}

step Report at "local:{ADAPTERS_MODULE}.Report" {{
  config {{
    output_dir: string;
    reports: map<string, {{ file: string; name: string; data_sets: list<{{ label: string; data_generator: string; }}>; }}>;
  }}
  inputs {{ data: overwrite<map<string, list<float>>>; }}
}}

step Plots at "local:{ADAPTERS_MODULE}.Plots" {{
  config {{
    output_dir: string;
    plots: map<string, {{
      file: string;
      name: string;
      kind: string;
      curves: list<{{ name: string; x: string; y: string; }}>;
      surfaces: list<{{ name: string; x: string; y: string; z: string; }}>;
      log_x: bool;
      log_y: bool;
      log_z: bool;
    }}>;
  }}
  inputs {{ data: overwrite<map<string, list<float>>>; }}
}}
"""

_ROLE = """// The role a solver fills: any step with this face. The generic COPASI and Tellurium steps have it.
step TimeCourseSolver {
  config { model_source: string; time: float; n_points: int; output_dir: string; }
  inputs { species_concentrations: map<string, float>; species_counts: map<string, float>; }
  outputs { result: numeric_result; }
}
"""


def _print(
    *,
    sed: SedmlFile,
    task: Task,
    simulation: TimeCourse,
    name: str,
    model_file: str,
    changes: dict[tuple[str, str], tuple[str, float]],
    grid: _Grid,
    generators: dict[str, list[tuple[str, float]]],
    constants: dict[str, float],
    reports: list[Any],
    plots: list[Any],
    sed_stem: str,
    solver: Solver | None,
    output_dir: str,
) -> str:
    lines: list[str] = []
    form = f"for {solver.id}" if solver else "template: the solver is an open site"
    lines.append(f"// pblang v2 - generated from {sed.path}, task {task.id!r} ({form})")
    lines.append("")
    if solver is not None:
        lines.append(f"import {solver.module}.{{{solver.class_name}}};")
        lines.append("")
    else:
        lines.append(_ROLE)
        lines.append("param output_dir: string = ?;")
        lines.append("")
    lines.append(_ADAPTERS)
    meta: dict[str, Any] = {
        "sedml": sed.path,
        "task": task.id,
        "model": task.model,
        "simulation": simulation.id,
        "algorithm": simulation.algorithm.kisao,
        "output_start": simulation.output_start,
        "output_end": simulation.output_end,
        "number_of_steps": simulation.number_of_steps,
    }
    if solver is not None:
        meta["solver"] = solver.id
    if changes:
        meta["changes"] = {f"{kind}:{eid}/{attr}": value for (kind, eid), (attr, value) in changes.items()}
    lines.append(f"meta {_value(meta, 0, 5)}")
    lines.append("")
    out_dir = _value(output_dir) if solver is not None else "${output_dir}"
    solver_type = solver.class_name if solver is not None else "TimeCourseSolver at ?"
    lines.append(f"composite {name} {{")
    lines.append("  store result: numeric_result = {};")
    # overwrite: bigraph-schema 1.0's map apply keeps only keys the store already has
    lines.append("  store data: overwrite<map<string, list<float>>> = {};")
    lines.append("")
    lines.append(f"  step simulate : {solver_type} {{")
    lines.append("    config {")
    lines.append(f"      model_source = {_value(model_file)},")
    lines.append(f"      time = {_value(grid.time)},")
    lines.append(f"      n_points = {grid.n_points},")
    lines.append(f"      output_dir = {out_dir}")
    lines.append("    }")
    lines.append("    outputs { result -> result }")
    lines.append("  }")
    lines.append("  step observe : DataGenerators {")
    lines.append("    config {")
    generator_config = {g: [{"variable": v, "coefficient": c} for v, c in t] for g, t in generators.items()}
    lines.append(f"      generators = {_value(generator_config, 6, 19)},")
    used = {v for t in generators.values() for v, _ in t}
    lines.append(f"      constants = {_value({k: v for k, v in constants.items() if k in used}, 6, 18)},")
    lines.append(f"      skip = {grid.skip}")
    lines.append("    }")
    lines.append("    inputs { result -> result }")
    lines.append("    outputs { data -> data }")
    lines.append("  }")
    report_config = {
        r.id: {
            "file": f"reports/{sed_stem}/{_identifier(r.id)}.csv",
            "name": r.name or r.id,
            "data_sets": [
                {"label": d.label, "data_generator": d.data_generator}
                for d in r.data_sets
                if d.data_generator in generators
            ],
        }
        for r in reports
    }
    lines.append("  step report : Report {")
    lines.append("    config {")
    lines.append(f"      output_dir = {out_dir},")
    lines.append(f"      reports = {_value(report_config, 6, 16)}")
    lines.append("    }")
    lines.append("    inputs { data -> data }")
    lines.append("  }")
    plot_config = {
        p.id: {
            "file": f"plots/{sed_stem}/{_identifier(p.id)}.plotly.json",
            "name": p.name or p.id,
            "kind": p.kind,
            "curves": [
                {"name": c.name or c.id, "x": c.x, "y": c.y}
                for c in p.curves
                if c.x in generators and c.y in generators
            ],
            "surfaces": [
                {"name": s.name or s.id, "x": s.x, "y": s.y, "z": s.z}
                for s in p.surfaces
                if {s.x, s.y, s.z} <= set(generators)
            ],
            "log_x": any(c.log_x for c in p.curves) or any(s.log_x for s in p.surfaces),
            "log_y": any(c.log_y for c in p.curves) or any(s.log_y for s in p.surfaces),
            "log_z": any(s.log_z for s in p.surfaces),
        }
        for p in plots
    }
    lines.append("  step plots : Plots {")
    lines.append("    config {")
    lines.append(f"      output_dir = {out_dir},")
    lines.append(f"      plots = {_value(plot_config, 6, 14)}")
    lines.append("    }")
    lines.append("    inputs { data -> data }")
    lines.append("  }")
    lines.append("}")
    return "\n".join(lines) + "\n"


_IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _value(value: Any, base: int = 0, start: int | None = None, width: int = 116) -> str:
    """A value in `.pblang` syntax (map literals with quoted keys for dicts, lists, strings, numbers, booleans): on
    one line when it fits in `width` columns from `start` (its column), else one entry per line indented from `base`
    (the column its line starts at)."""
    flat = _flat(value)
    column = base if start is None else start
    if len(flat) + column <= width or not isinstance(value, (dict, list)) or not value:
        return flat
    pad, inner = " " * base, " " * (base + 2)
    if isinstance(value, dict):
        body = []
        for k, v in value.items():
            key = f"{json.dumps(str(k))} = "
            body.append(f"{inner}{key}{_value(v, base + 2, base + 2 + len(key), width)}")
        return "{\n" + ",\n".join(body) + "\n" + pad + "}"
    body = [inner + _value(v, base + 2, base + 2, width) for v in value]
    return "[\n" + ",\n".join(body) + "\n" + pad + "]"


def _flat(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return repr(value) if math.isfinite(value) else json.dumps(str(value))
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    if value is None:
        return "null"
    if isinstance(value, list):
        return "[" + ", ".join(_flat(v) for v in value) + "]"
    if isinstance(value, dict):
        if not value:
            return "{}"
        return "{ " + ", ".join(f"{json.dumps(str(k))} = {_flat(v)}" for k, v in value.items()) + " }"
    raise TypeError(f"cannot print {type(value).__name__}")


# --- models -------------------------------------------------------------------------------------------------------


def _header(path: str, sbml: bytes) -> ModelHeader:
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / PurePosixPath(path).name
        target.write_bytes(sbml)
        return describe_sbml(target)


def _has(header: ModelHeader, kind: str, element_id: str) -> bool:
    if kind == "species":
        return element_id in header.species
    if kind == "parameter":
        return element_id in header.parameters
    if kind == "compartment":
        return element_id in header.compartments
    return True  # reactions are not in the header; the solver reports them or the X404 finding does


def _constants(header: ModelHeader, changed: dict[tuple[str, str], tuple[str, float]]) -> dict[str, float]:
    """Values of constant parameters and compartments (after changes): data generators read them directly."""
    values: dict[str, float] = {}
    for kind, block in (("parameter", header.parameters), ("compartment", header.compartments)):
        for name, q in block.items():
            if not q.constant:
                continue
            attr_value = changed.get((kind, name))
            value = attr_value[1] if attr_value is not None and attr_value[0] in ("value", "size") else q.value
            if value is not None:
                values[name] = float(value)
    return values


def _apply_changes(sbml: bytes, changed: dict[tuple[str, str], tuple[str, float]]) -> bytes:
    """The SBML with each change's attribute set, its namespaces and prefixes kept."""
    for _, namespace in ET.iterparse(io.BytesIO(sbml), events=["start-ns"]):
        prefix, uri = namespace
        ET.register_namespace(prefix, uri)
    root = ET.fromstring(sbml)
    for (kind, element_id), (attribute, value) in changed.items():
        for element in root.iter():
            if element.tag.rsplit("}", 1)[-1] == kind and element.get("id") == element_id:
                element.set(attribute, repr(value))
                break
    written: bytes = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    return written


def _read_files(source: Path) -> dict[str, bytes]:
    if zipfile.is_zipfile(source):
        with zipfile.ZipFile(source) as archive:
            return {
                str(PurePosixPath(n.removeprefix("./"))): archive.read(n)
                for n in archive.namelist()
                if not n.endswith("/")
            }
    return {p.name: p.read_bytes() for p in source.parent.iterdir() if p.is_file()}


@cache
def _kisao() -> dict[str, dict[str, Any]]:
    data = json.loads((Path(__file__).with_name("kisao_ode.json")).read_text(encoding="utf-8"))
    terms: dict[str, dict[str, Any]] = data["terms"]
    return terms


def _identifier(text: str) -> str:
    name = re.sub(r"\W", "_", text)
    return name if _IDENT.match(name) else f"_{name}"


def _module_path(address: str) -> str:
    return address.split(":", 1)[-1].removeprefix("!")


__all__ = [
    "ADAPTERS_MODULE",
    "FINDINGS",
    "Finding",
    "Solver",
    "TaskTranslation",
    "Translation",
    "compile_instance",
    "instance_archive",
    "sedml_members",
    "solvers_from",
    "translate",
]
