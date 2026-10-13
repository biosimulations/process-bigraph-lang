# SED-ML plan: models described in SED-ML, run as checked `.pblang` templates on several solvers

Status: agreed 2026-10-12. This is the language half of compose-api's
[`docs/plan-sedml.md`](https://github.com/biosimulations/compose-api/blob/main/docs/plan-sedml.md), which holds the
decisions, the service side (runs, datasets, comparisons, sources, suites) and the phase table. Each PR here updates
the status below.

| Step | What                                                                                                                            | State    |
| ---- | ------------------------------------------------------------------------------------------------------------------------------- | -------- | ----------------------------------------------------------------------------------- | ------- |
| 1a   | `sedml.py`: SED-ML read with the standard library into `pblang-sedml/0` JSON, with an `unsupported[]` list                      | planned  |
| 1b   | `sedml.pblang`: the role header (`TimeCourseSolver`, the SED-ML adapters' faces)                                                | planned  |
| 1c   | The template printer: one `.pblang` composite per SED-ML task, the SBML model header beside it, the solver an open address site | planned  |
| 1d   | Compile with a solver filled, checked against that solver's environment manifest; refusal findings                              | planned  |
| 1e   | Plot templates (Plotly JSON) from SED-ML plots, and `fill_plot` from a report CSV (Python and TypeScript)                       | planned  |
| 1f   | CLI `sedml describe                                                                                                             | template | compile`, `Pblang.sedml` in the embeddable API; corpus and snapshots; release 0.3.0 | planned |

## Why here

compose-api will run SED-ML models (curated BioModels entries, biosimulations.org projects, uploads) as
process-bigraph documents, one run per solver, and compare the results. The translation lives in this package, not
in the service, for the reason CLAUDE.md gives: there is no Python model of a composite, and nothing runnable skips
the checker. A SED-ML task becomes `.pblang` text; the solver is an open site; filling it with a solver is checked
against that solver's interface in the environment that runs it. The same template, filled with each solver in turn,
is the "same workflow on several implementations" that the comparison needs, and the text is what the composite
viewer shows and "Edit a copy" opens.

It also exercises two parts of the language that no real workload uses yet: model headers (`describe-model`,
`model X from "file"`, design section 5.6) and templates with address sites (design section 4.5).

## Scope, version 1

Read: uniform time course simulations (initial time, output start and end, number of points, the KiSAO algorithm
and its parameters); tasks; models with **attribute changes** (`changeAttribute` on an SBML target by XPath, resolved
to the SBML id); **simple data generators** (one variable, a time symbol or an SBML id by XPath, with `math` that is
the variable itself or the variable times a constant); **reports** (data set id, label, data generator); **plots**
(2D curves: x and y data generators, names, log scales; 3D surfaces).

Reported, never dropped silently (an `unsupported[]` entry with the element's id and why): steady state and one-step
simulations, repeated and nested tasks, other change kinds (`computeChange`, `addXML`, `removeXML`, `changeXML`),
data generators with other math, models that are not SBML, references to remote models.

### Settled in 1a

- **Simple data generators are linear combinations**: `x`, `c * x`, `x / c`, `x + y`, `x - y`, with constants from
  `<cn>` or the data generator's own parameters. The Ciliberto project needs the sum (`Swe1T` is four species added).
  Each is `terms: [{variable, coefficient}]`.
- **Steps, not points.** L1V1-3's `numberOfPoints` and L1V4's `numberOfSteps` both count intervals; the description
  says `number_of_steps`, and a time course has `number_of_steps + 1` points.
- **An archive's SED-ML** is what its `manifest.xml` declares with the SED-ML format (the master first), else every
  `*.sedml` member.
- **Targets** resolve to `{kind, id, attribute}` for species, parameters, compartments and reactions (a reaction's
  variable is its rate). A data generator may name any of them: BIOMD0000000012's report asks for all four kinds,
  so a solver that returns only species leaves the rest unfilled. Phase 2 (the adapters) must say which kinds each
  solver provides, and the compile step reports the gap per solver.
- **Algorithms are KiSAO terms, sometimes generic**: BIOMD0000000012 asks for `KISAO:0000694` ("ODE solver"), not a
  specific integrator. Matching a solver to an algorithm (1d) uses the KiSAO hierarchy, not equality.

## What a task becomes

For `BIOMD0000000012` (the repressilator; its archive holds `BIOMD0000000012_url.xml` and
`BIOMD0000000012_url.sedml`), the shape is (names indicative; settled in 1b and phase 2):

```text
// pblang v2 - generated from BIOMD0000000012_url.sedml, task "task1"
import sedml.{TimeCourseSolver, SedmlModelChanges, SedmlDataGenerators, SedmlReport, SedmlPlots};
import BIOMD0000000012_url.{Elowitz2000};          // the model header, from describe-model

composite task1 {
  store model_file = "BIOMD0000000012_url.xml";
  step changes : SedmlModelChanges {               // attribute changes, applied to a copy of the SBML
    config  { changes = { "parameter:k1" = 2.0 } }
    inputs  { source -> model_file }
    outputs { model -> model }
  }
  step simulate : TimeCourseSolver at ? {          // the solver: an open site, filled per solver
    config  { start = 0.0, end = 1000.0, n_points = 1000, algorithm = "KISAO:0000019" }
    inputs  { model -> model }
    outputs { result -> raw }
  }
  step observe : SedmlDataGenerators {             // variables and scales -> data set labels; output start
    config  { generators = { ... }, output_start = 0.0 }
    inputs  { result -> raw }
    outputs { data -> data }
  }
  step report : SedmlReport { config { reports = { ... } } inputs { data -> data } }
  step plots : SedmlPlots { config { templates = [ file("plots/plot1.plotly.json") ] } inputs { data -> data } }
}
```

- The model's species and parameters named by changes and data generators are checked against the model header (a
  change to a parameter the model lacks is a finding, `G301`-style).
- `TimeCourseSolver` is a **role**: an interface with no `at`, declared in `sedml.pblang`. Filling `simulate`'s
  address with a class is admitted when that class's interface (from the environment's manifest) fits the role's
  face: the existing face check. Generic COPASI and Tellurium steps that do not share one face are fitted by thin
  wrappers in the adapters package (compose-api phase 2), never by special cases here.
- A requested algorithm the solver does not implement is a finding: a solver lists its KiSAO terms (compose-api's
  `solvers.yaml`, passed in as data), and the check compares.
- Steps run in dependency order; the composite sets what process-bigraph needs for steps to run (the
  `run_steps_on_init` trap in CLAUDE.md).

## Plots

Each SED-ML plot becomes `plots/<sedml>/<plot>.plotly.json`: a Plotly figure whose traces name data set labels in
place of data (`{"x": {"$label": "time"}, "y": {"$label": "PX"}, "name": ...}`), with axis titles and scales.
`fill_plot(template, csv_text)` replaces each `$label` with the column (Python for the job's `SedmlPlots` step and the
service; TypeScript for the browser, which overlays several runs' traces on the comparison page).

## Interfaces

- Python: `describe_sedml(path_or_omex) -> SedmlDescription` (`to_dict()` is `pblang-sedml/0`);
  `sedml_templates(description, model_headers) -> {task: (text, assets)}`;
  `compile_sedml(text, solver_address, manifests, solver_algorithms) -> document | findings`.
- CLI: `python -m process_bigraph_lang.v2 sedml describe x.omex`, `sedml template x.omex -o dir/`,
  `sedml compile dir/task1.pblang --solver local:… -i manifest.json`.
- TypeScript: `Pblang.sedml(description)` for the browser preview (tasks, reports, plots, findings), and
  `fillPlot`.

## Corpus

`tests/fixtures/data/v2/sedml/`: BIOMD0000000012 (EBI's COMBINE archive), the Ciliberto 2003 morphogenesis project
from biosimulations.org (with its `reports.h5`), and two more chosen for coverage (attribute changes; a log-scale
plot). Each: describe snapshot, template snapshot per task, compiled document per solver, an out-of-scope case.
