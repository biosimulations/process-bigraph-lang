# SED-ML plan: models described in SED-ML, run as checked `.pblang` templates on several solvers

Status: agreed 2026-10-12. This is the language half of compose-api's
[`docs/plan-sedml.md`](https://github.com/biosimulations/compose-api/blob/main/docs/plan-sedml.md), which holds the
decisions, the service side (runs, datasets, comparisons, sources, suites) and the phase table. Each PR here updates
the status below.

| Step | What                                                                                                       | State                       |
| ---- | ---------------------------------------------------------------------------------------------------------- | --------------------------- |
| 1a   | `sedml.py`: SED-ML read with the standard library into `pblang-sedml/0` JSON, with an `unsupported[]` list | in review                   |
| 1b   | The role and adapter declarations (`TimeCourseSolver`, the SED-ML adapters' faces)                         | in review                   |
| 1c   | The template printer: one `.pblang` composite per SED-ML task, the solver an open address site             | in review                   |
| 1d   | One instance per solver, checked and compiled against that solver's environment manifest; refusal findings | in review                   |
| 1e   | SED-ML plots as Plotly figures                                                                             | in review                   |
| 1f   | CLI `sedml describe` and `sedml translate`; corpus and snapshots; release 0.3.0                            | in review (release to come) |

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

## What a task becomes (as built in 1b to 1f)

`process_bigraph_lang/v2/sedml_translate.py`. Each task of each SED-ML file becomes a composite of four steps
(see `tests/fixtures/data/v2/sedml/snapshots/` for the repressilator's template and COPASI instance, and the
Ciliberto project's Tellurium instance):

```text
composite task_1 {
  store result: numeric_result = {};
  store data: map<string, list<float>> = {};

  step simulate : TelluriumUTCStep {                 // the template says `TimeCourseSolver at ?`
    config { model_source = "BIOMD0000000297_url.changed.xml", time = 140.0, n_points = 201,
             output_dir = "/experiment/output" }
    outputs { result -> result }
  }
  step observe : DataGenerators { config { generators = {...}, constants = {...}, skip = 0 } ... }
  step report : Report { config { output_dir = ..., reports = {...} } inputs { data -> data } }
  step plots : Plots { config { output_dir = ..., plots = {...} } inputs { data -> data } }
}
```

Decided while building it (2026-10-13):

- **The role is the generic solvers' common face.** pbsim-common's `CopasiUTCStep` and `TelluriumUTCStep` declare the
  same interface in `registry_env`'s manifest: config `model_source, time, n_points, output_dir`, the species inputs,
  `result: numeric_result`. `TimeCourseSolver` is that face; no wrappers are needed.
- **Filling a solver is printing it, and the checker is the face check.** Process-bigraph 1.0.5 (`registry_env`) has
  no sites, so a run's document must be ground. The template keeps `simulate : TimeCourseSolver at ?` (it checks
  with only `I300`); an instance imports the solver's own class and names it, so the existing checker verifies its
  config and ports against the environment's manifest (`S021`, `S022`, `T121`, `W200`). A solver that does not fit
  is refused by those findings, with no new language machinery.
- **Model changes are applied at translation** (Jim, 2026-10-13): they are constants, and the generic solvers read the
  model from config, which no step can change. The instance reads `<model>.changed.xml`, written with the change
  applied (namespaces kept), and its `meta` lists each change.
- **Adapters live in a new package we own** (Jim, 2026-10-13), `pbsim_sedml` until it is named. Each generated file
  declares them inline at their addresses, so it is self-contained.
- **The output grid.** The generic solvers start at 0 and take points, not steps: `time` is the output end,
  `n_points` covers the initial time to the end on the output's step, and `observe` drops the `skip` points before
  the output start. An initial time other than 0 (`X402`) or an output that is not on that grid (`X403`) refuses
  the task.
- **What a solver returns.** The generic steps return species columns and time. Data generators reading constant
  parameters or compartments take their values (after changes) from the model header; those reading rule-defined
  parameters or reaction rates are left out of that solver's reports and plots (`X404`, one finding per kind).
- **Algorithms.** A solver lists the KiSAO terms it implements (default first). The generic `KISAO:0000694`, a
  listed term, or an ancestor of the solver's default is accepted; another ODE algorithm is a substitution (`X405`,
  a warning: COPASI runs LSODA/LSODAR where CVODE is asked for); anything else refuses (`X406`). The ODE terms and
  their ancestors are `kisao_ode.json`, from the KiSAO ontology.
- **Plots are built at run time.** The `Plots` adapter takes each SED-ML plot's curves (data generator ids, names, log
  axes) in its config and writes the Plotly figure with the data; no template files and no `fill_plot`. The
  comparison page overlays the figures of several runs.
- **The data store is `overwrite<map<string, list<float>>>`**: bigraph-schema 1.0's `map` apply keeps only keys the
  store already has, so a `map` store would stay empty (found running the chain under `registry_env`'s versions).
- **One archive per task and solver**: pbest runs the first top-level `.pbg`, so `instance_archive` holds one compiled
  document (`<task>.pbg`), its text and the model files.
- **No browser translation.** The web app previews a translation through compose-api, which calls this package.

## Findings

| Code | Severity | Meaning                                                                                           |
| ---- | -------- | ------------------------------------------------------------------------------------------------- |
| X400 | warning  | a SED-ML element version 1 does not translate (from `describe`'s `unsupported`)                   |
| X401 | error    | a change or data generator names an element the model does not have, or the model file is missing |
| X402 | error    | the time course does not start at 0, where the generic solvers start                              |
| X403 | error    | the output is not on a grid from the initial time                                                 |
| X404 | warning  | data generators read values the solver does not return; they are left out of its outputs          |
| X405 | warning  | the solver runs a different ODE algorithm than the one asked for                                  |
| X406 | error    | the solver implements no algorithm of the kind asked for                                          |

## Interfaces

- Python: `describe_sedml(path) -> SedmlDescription` (`pblang-sedml/0`);
  `translate(path, solvers, output_dir) -> Translation` (per task: the template, one instance per accepted solver,
  the model files, the findings); `compile_instance(task, solver, manifests, addresses="registered")`;
  `instance_archive(task, solver, document) -> bytes`; `solvers_from(data)` for compose-api's `solvers.yaml`.
- CLI: `python -m process_bigraph_lang.v2 sedml describe x.omex [-o d.json]`;
  `sedml translate x.omex --solvers solvers.yaml -i env.json -o dir/` (texts, models, one archive per task and
  solver, `findings.json`). `compile --addresses registered` writes `local:module.Class` (the CLI now has the option
  the TypeScript API had).

## Corpus

`tests/fixtures/data/v2/sedml/`: BIOMD0000000012 (EBI), the Ciliberto 2003 project (biosimulations.org),
`out_of_scope.sedml` (and edited copies of it for each refusing finding), `solvers.yaml` (the generic COPASI and
Tellurium steps), and `snapshots/` (generated text: checked by `dsl/test/v2/sedml.test.ts`, not the printer's
fixpoints). `interfaces/registry_env_pbsim.manifest.json` is the pbsim-common part of compose-api's generated
`registry_env` manifest.
