# v2 background: research notes (2026-10-11)

This page records what was learned while taking a second look at the language, a year after its first design.
It is the evidence behind the [v2 language design](design.md), the
[registry and authoring design](registry-and-authoring.md) and the [implementation plan](plan.md).

Sources were the local clones of `process-bigraph` (1.8.5, commit e5325c1), `bigraph-schema` (1.6.0, commit 8268aa1;
origin is at 1.7.0), the `viva-*` and `pbg-*` packages, `vivarium-workbench`, `viva-catalog` (read through the GitHub
API), and this repository. The Python environment of this repository has process-bigraph 1.8.4 and bigraph-schema 1.6.0.

## 1. What motivated the second look

- process-bigraph grew **templates and sites** (open holes in a document, filled later), **contracts** and
  **contract audits**, and a declarative **CompositeSpec** (`*.composite.yaml`).
- The ecosystem grew to about fifty `viva-*` packages, a browser workbench, a nascent registry and prompt-driven
  authoring tools.
- `viva-pde-particle`, a co-simulation of a PDE solver and a Brownian-dynamics particle solver, shows what real
  composites need and what today's language cannot say.
- The current DSL is one-directional, lossy, and was designed as the document a person writes by hand. The new framing
  is different: the DSL is a **verifiable target layer**. End users author with prompt-guided tools against a
  **declared registry of components**; the DSL is where the result is type-checked, audited, documented and
  explained, and from which the runnable document is generated.

## 2. process-bigraph 1.8 and bigraph-schema 1.6–1.7

### 2.1 Composite document

A document is `{"schema": …, "state": …}` plus optional top-level options. `Composite.config_schema` declares
`schema`, `state`, `interface{inputs,outputs}`, `bridge{inputs,outputs}` (and an undeclared `bridge.conduits`),
`global_time_precision`, `run_steps_on_init`, `parallel_steps`, `parallel_processes`, `parallel_workers`,
`skip_process_state` and (clone only) `contract_strict`. `initialize` injects `global_time` at the root.

An edge node in `state` may carry:

| Key                     | Notes                                                                                                  |
| ----------------------- | ------------------------------------------------------------------------------------------------------ |
| `_type`                 | `process`, `step` or `link`; may be omitted in `state` when `schema` declares it                       |
| `address`               | `"protocol:data"` string or `{"protocol","data"}` dict; no protocol means `local`                      |
| `config`                | realized against the class `config_schema`                                                             |
| `inputs` / `outputs`    | wires: list paths **relative to the edge's parent**; a string is a one-element path; nested dicts wire |
|                         | sub-ports; `..` goes up; `*` is a star jump                                                            |
| `_inputs` / `_outputs`  | port-schema overrides merged with `interface()`                                                        |
| `interval`              | process only, must be > 0, default 1.0                                                                 |
| `priority`, `_triggers` | step only                                                                                              |
| any other non-`_` key   | realized as extra data                                                                                 |

Address protocols: `local:Name` (registry lookup; discovery registers both `module.Class` and a short alias, first one
wins), `local:!module.Class` (import by dotted path, portable), `parallel:`, `ray:`, `rest:` and `git:` (allow-listed
repo at a SHA, per-SHA venv, subprocess RPC, face-conformance check). `registry_dependent_addresses` and
`assert_portable_addresses` in `bigraph_schema/protocols.py` lint for the non-portable form.

Nested composites are a process at `local:Composite` whose `config` holds `state`, `schema`, `bridge` and
`interface`; the outer ports derive from `bridge`. **Saving such a document is lossy**: the inner state comes back
empty (observed on 1.8.4 and the clone). Shared processes use `shared_process` plus `shared_process_ref`.

Emitters are steps whose config has `emit: <schema>`; viva-emitters provides RAM, sqlite, parquet and xarray. CompositeSpec
has `emitters: [{address, paths}]` sugar, materialized by `process_bigraph.emitter.emitter_node_from_declaration`.

### 2.2 Serialized documents differ from authored ones

`Composite.save()` writes `{"state": serialize_state(), "schema": serialize_schema()}`. Compared with the authoring
document:

- `_type` appears only in the schema half; the state half has dict addresses `{"protocol","data"}`.
- `config` is fully defaulted; `_inputs`/`_outputs` are always present, often in compact string form
  (`"level:float"`); a `_contract` block is added.
- `global_time` and process-contributed stores (an emitter's `results`) are added.
- The schema half is rendered **without** defaults, so a dict schema collapses to a string (`"pt": "x:float|y:float"`)
  and store defaults are lost (`float{3.5}` becomes `float`).
- Rendering quirks: `map[string,float]` becomes `map[float]`; `array[float]` becomes `array[1,float]`.
- Reloading `{"state": saved_state}` alone silently loses every process; both halves are needed.

### 2.3 Templates and sites

The vocabulary is **site, sort, admits, face, fill, compose, ground, template**. "Slot" was an earlier draft name
and was dropped deliberately. There is one `Site` type (`bigraph_schema/schema.py`, `class Site(Empty)` with `_sort`
and the inherited `_default`); its kind is decided by its sort and position:

| Kind         | Written as                                                           | Admits                                                            |
| ------------ | -------------------------------------------------------------------- | ----------------------------------------------------------------- |
| value site   | `{"_type":"site","_sort":"float"}`                                   | `core.check(sort, filler)`                                        |
| face site    | `_sort` is `link[in,out]` or `{"_type":"link","_inputs","_outputs"}` | `face_conforms`: every required port, resolvable types; extras ok |
| address site | `"address": {"_type":"site","_sort": FACE}` inside an edge node      | filler is an address; face from the registered class              |
| config site  | a site anywhere under an edge's `config`                             | as a value site                                                   |
| named sort   | `_sort: "results"` via `core.register_sort` or a contract name       | custom admits function                                            |
| unsorted     | `"site"`                                                             | anything                                                          |

`{"_control":"replicate","_count":N}` expands a region N times (`assembly.build` only). The algebra is in
`bigraph_schema/assembly.py` (`interfaces`, `is_ground`, `admits_why`, `face_conforms`, `fill_sites`, `replicate`,
`build`); the process-bigraph layer is `process_bigraph/templates.py` (`open_sites`, `required_open_sites`,
`is_ground_document`, `fill_template`, `template_document`, `load_template`, `save_template`). bigraph-schema 1.7 adds
`bigraph_schema.matching.find_candidates(core, site)`.

Fill semantics: bindings are keyed by bare site key (when unique) or by `/`-joined path; an unbound site with a
`_default` is filled from it; a value filler becomes the sort with `_default=value`; `template_document` renders with
`defaults=True` (without it, values are lost). `Composite.initialize` checks groundness before realization (clone) and
raises `composite document is not ground — required site(s) left unfilled: '…'`. Two upstream traps remain: a
`schema` entry used to swallow a `state` site (process-bigraph#213), and address sites can only be filled with names
registered through `core.register_link` (bigraph-schema#188).

### 2.4 Type system

String grammar (`bigraph_schema/parse.py`): `name[params]{default}`, struct `a:T|b:U`, union `A~B`, parentheses.
Builtins: node, atom, empty, union, tuple, boolean, integer, float, float64, nonnegative, complex, range, string, enum,
maybe, overwrite, const, quote, list, set, map, tree, array, dataframe, path, wires, protocol, schema, link, object,
function, quantity, site, inner_name, outer_name, face; process-bigraph adds step, process, composite, interface,
bridge, shared_process, interval. Dict forms use `_element`, `_key`, `_value`, `_values`, `_options`, `_shape`,
`_data`, `_units`, `_bits`, `_min`, `_max`, `_sort`, `_inputs`, `_outputs`, `_class`, `_default`, `_inherit`.

Two traps: **`any` is not a type** and an unknown string name passes through `core.access` silently, so typos are
not caught; and a plain `map[array[float]]` output is **additive** unless wrapped in `overwrite[...]`, which silently
changes update semantics. Custom types are registered via a `register_types(core)` hook and get behaviour from plum
dispatch methods, not from `_apply` keys (those no longer exist).

### 2.5 Interfaces and discovery

`Edge` (`bigraph_schema/edge.py`) has class attributes `config_schema`, `description`, `contract` and instance
methods `inputs()`, `outputs()`, `interface()`, `describe()`. `ProcessContract` (`bigraph_schema/contract.py`) is a
structured face with `_units`, `_min`, `_max`, description, assumptions and references; `audit_contract` and
`completeness` (1.7) grade it. `DraftProcess` declares ports and a contract with no dynamics.

Discovery is import-based everywhere: `allocate_core()` scans every installed distribution that depends on
bigraph-schema and imports it (with a lazy on-disk name→module index); import errors in submodules are swallowed.
There is no static interface manifest and no entry-point mechanism. The REST server exposes `/list-processes` and
`/process/{p}/config-schema`.

## 3. The viva ecosystem

### 3.1 viva-pde-particle

Pipeline: model input (Python `HybridModel` dataclasses or SBML Spatial via libvcell) → `partition()` into PDE and
particle halves → Smoldyn config text → geometry (vcell-fenics `GeometryDescription` realized by Netgen or libvcell;
derived mesh, membrane triangles, volume samples, fold maps) → engines (FV, FEniCSx Q1/P1, `SmoldynHybrid`) → coupling
(adapter steps both ways; timing by Jacobi scheduling, `Stepper` with `every`/`phase`, or `SplittingCoordinator`) →
output (`HybridTrajectory` from a Python run loop, or `SpatialRecorder` writing a zarr bundle; `SpatialExport` after the
run because there is no end-of-run hook) → visualization (`viz3d`).

Declarations: config schemas are mostly untyped `"map"` blobs (`grid`, `pde` partition, mesh spec, `domain` arrays,
generated `config_text`); ports are always `map[array[float]]` in and `map[overwrite[array[float]]]` out; no custom
types, shapes or units (these live in prose in `docs/DESIGN.md` §13). Ports depend on config (`SmoldynHybrid` adds
`particle_positions` only if `emit_positions`; `SpatialRecorder.inputs()` depends on `layout.kind`) or on children
(`Stepper.inputs()` returns its child's; `SplittingCoordinator` unions its children's ports). Adapters are steps in
`steps/transfer.py` with `config {grid: map, mesh: map, species: list[string]}`.

Composites are built only by Python functions in `composites/hybrid.py`, wrapped by `@composite_generator` in
`composites/examples.py`; there are no `*.composite.yaml` files. Builder logic that is not declarative today: engine
choice by name, adapter choice, conditional wiring, option-combination validation, pre-computing initial arrays by
instantiating steps (steps don't run at init), a probe process to learn the DOF count, seeded particle placement,
generating the Smoldyn text, and keeping grid/mesh/species consistent across components. Addresses are bare
`local:Name` registered by a hand-written `build_core()` because editable installs are not discovered. The package
runs in a single pixi environment (dolfinx, gmsh, a patched Smoldyn submodule, pyvcell) on linux-64 and osx-arm64,
with a compose-api Docker image.

### 3.2 Other packages

| Package                           | Declarations and authoring                                                                                                                                                                                       |
| --------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| viva-smoldyn, viva-vcell-fvsolver | declarative `*.composite.yaml` (CompositeSpec: `requires`, `parameters` with `${}` substitution, `emitters`)                                                                                                     |
| viva-fenics                       | `@composite_generator` dict literals that compute initial mesh arrays in Python; one custom type `fem_field`                                                                                                     |
| viva-emitters                     | emitters as steps with `emit: schema`; the only self-describing contract (`EmitterContract(output_kind, output_uri_config_key)`)                                                                                 |
| viva-uq                           | injects parameters at `"a/b/c"` paths; builds an emitter class at runtime to dodge type checking                                                                                                                 |
| spatio-flux (older)               | richest custom types (`positive_float` with custom apply, `enum`, `maybe`, `map[reaction]`); one `DynamicFBA` per grid cell with array-indexed wires `["..","fields",mol,i,j]`; port shapes computed from config |
| pbg-ptools                        | workbench viewer plugin, no processes                                                                                                                                                                            |

Nothing publishes process interfaces as data. The only entry-point group is `process_bigraph.spec_generators` for
composite generators. The `catalog/modules.json` in viva-superpowers lists repo pointers, not interfaces. pbg-template
scaffolds a workspace (JSON Schemas for `workspace.yaml`, study and investigation; a `core.py` stub).

### 3.3 vivarium-workbench and loom

The workbench is a local FastAPI server that turns a workspace directory (`workspace.yaml`, `composites/*.composite.yaml`,
studies, investigations; every mutation committed to git) into an interactive notebook. It never imports workspace
code in the HTTP process; a stdlib-only `env_worker.py` runs in the workspace interpreter, imports
`<package>.core.build_core()`, walks `core.link_registry`, reads `config_schema` and calls `inputs()`/`outputs()` with
the class standing in for `self` (ports are `None` when that fails). The record sent to the frontend is
`RegistryProcess {name, address, kind, schema_preview, aliases, source, description, config_schema, inputs, outputs}`
plus, on GitHub, `contract_audit`. Composites are authored as yaml with parameter forms (`ParameterDecl {type, default,
description, choices}`), dotted-path "perturb" overrides, per-process "try it", and the viva-superpowers skills.
Validation: JSON Schema at save time, `{error}` envelopes, build errors as a warning chip with the stringified
exception, a preflight that aggregates silent failures, and (on GitHub) a composite-level contract audit with codes
`wire-type-mismatch`, `wire-unit-mismatch`, `unknown_port`. Runs are local (SQLite results) or remote via viva-api.

`bigraph-loom` is archived and vendored at `vivarium_workbench/loom/`: a read-only React Flow viewer and inspector with
many layout engines, drill-down into composite processes, a contract panel and a raw JSON panel. It has no text
pretty-printer, no diffs, no templates and no validation. Its process node model is `{processType, address, config,
configSchema, interval, inputPorts, outputPorts, inputSchema, outputSchema, contract, isCompositeProcess}` with wires
resolved to absolute store paths in `convert.ts`.

### 3.4 viva-catalog

"Ledger for the vivarium ecosystem": `modules.json` lists repos tagged with the GitHub topic `viva-marketplace`
(`{name, source, ref, package, homepage, description, tags}`); a nightly workflow shallow-clones each one and AST-scans
class names into `ecosystem-index.json` (`processes: [{name, description}]`, steps, composites, studies,
investigations). There are no ports, config schemas or addresses in the index. A PR proposing AST-extracted ports, JSON
Schemas and a `marketplace_info.get_info()` hook was closed unmerged on 2026-07-30. Published at
`vivarium-collective.github.io/viva-catalog/*.json` and consumed by the workbench marketplace tab.

### 3.5 Pain points collected

1. A missing address fails late and cryptically: `no link found at address: {'protocol': 'local', 'data': 'X'}`.
2. Unknown type names (`int`, `any`) are accepted silently.
3. Additive vs `overwrite[...]` update semantics are silently wrong; an empty-array initial store is replaced rather
   than added to.
4. Remote failures succeed silently: dropped process swaps, typo'd emit paths that materialize empty dicts, empty
   variant grids.
5. `${param}` substitution leaves malformed references as-is; values may arrive as strings.
6. Discovery swallows `ImportError`s; a registry cache can be stale and show none of the workspace's own processes.
7. Float-sum interval drift defers updates.
8. Validation lives in `initialize()`/`update()` as `ValueError`s, not in schemas.
9. Schemas for emitters, studies and investigations are hand-mirrored across repos and unversioned.
10. Missing observables are returned as `0.0`.
11. Saved nested composites lose their inner state.

## 4. This repository before v2

- One direction only: DSL → document. No printer, formatter, decompiler, hover or completion provider.
  `dsl/src/language/sbml.ts` is a narrow precedent for generating DSL from external data.
- Lossy compile: aliases erased, struct-typed stores split per field, references inlined, remote type names dropped,
  units and comments dropped, `interval` never set.
- Missing constructs compared with the 1.x document: emitters, `interval`, nested composites and `bridge`, maps of
  edges, custom types with apply behaviour, enum/union/maybe/optional, array dtype and shape, imports across files, doc
  comments, protocol-aware addresses, units on types, nested or per-key wiring, `..` paths, remote-typed config values,
  expressions.
- The old ANTLR grammar (`antlr/pblang.g4`) had different ideas worth remembering: parameters with units, update
  expressions, `maybe[T]`, store hierarchies, `composite_def`, an `sbml` block.
