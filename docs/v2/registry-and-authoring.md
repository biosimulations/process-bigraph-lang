# v2 registry, prompt-guided authoring and validation UX

Status: design, 2026-10-11. Companion to the [language design](design.md); background in the
[research notes](research.md); sequencing in the [plan](plan.md).

The framing: the formal DSL is a **verifiable target**, not the single document an end user constructs by hand.
End-user authoring uses (1) a **declared registry of components** (processes, steps, adapters, emitters) whose
interfaces are published as data, so authoring needs no Python import or introspection, and (2) **prompts** (LLM-guided
tooling such as the viva-superpowers Claude Code skills) that guide construction, documentation and validation. The DSL is
where the constructed workflow is type-checked, contract-audited, explained and documented, and from which the runnable
document or `*.composite.yaml` is generated.

## 0. Shape

```text
package repo CI (package's own env)        anywhere pblang is installed              execution env
pblang-describe (stage A: introspect)  ->  pblang registry build (stage B)          pblang preflight
   manifest.raw.json                        + interfaces.override.pblang              (installed vs lock vs
                                            -> pblang/manifest.json                    fingerprint; env hints)
                                            -> pblang/interfaces.pblang
viva-catalog nightly: fetch manifest.json per module -> components.json
LLM skill or human: import -> draft .pblang -> pblang check / doc / compile -> preflight -> run
```

Three principles:

1. **The manifest JSON is canonical**; `interfaces.pblang` is rendered from it deterministically. Tools read JSON,
   humans and `import` read `.pblang`, CI verifies they agree.
2. **Stage A has zero pblang dependencies**, so it runs inside any package environment (a pixi env, the workbench
   `env_worker`, a `git:` per-SHA venv).
3. **One diagnostics JSON format** for the CLI, the language server, the workbench and the skills.

## 1. Component registry

### 1.1 Files shipped by a package

```text
<pkg>/pblang/manifest.json               generated, canonical (stage B output); committed and in the wheel
<pkg>/pblang/interfaces.pblang           rendered from manifest.json; what `import` reads
<pkg>/pblang/interfaces.override.pblang  hand-written; merged by component name; committed
<pkg>/pblang/manifest.raw.json           stage A output; CI artifact only
```

They are located without importing the package, through `importlib.metadata.distribution(name).files`. That is the
difference from `bigraph_schema/package/discover.py` and the workbench's `env_worker.py`, which both import.

### 1.2 Manifest (`pblang-manifest/1`)

JSON Schema to live at `docs/schemas/manifest.schema.json`.

```json
{
  "schema_version": "pblang-manifest/1",
  "package": {
    "name": "viva-pde-particle",
    "module": "viva_pde_particle",
    "version": "0.4.2",
    "python": ">=3.11",
    "source": "https://github.com/vivarium-collective/viva-pde-particle",
    "ref": "v0.4.2",
    "commit": "e5325c1"
  },
  "generated": {
    "tool": "pblang-describe 0.1.0",
    "at": "2026-10-11T00:00:00Z",
    "process_bigraph": "1.8.5",
    "bigraph_schema": "1.7.0",
    "from_override": ["Stepper", "SplittingCoordinator"]
  },
  "environment": {
    "install": ["pip install viva-pde-particle==0.4.2"],
    "native": ["smoldyn (patched fork)", "dolfinx", "gmsh"],
    "image": "ghcr.io/vivarium-collective/viva-pde-particle:0.4.2",
    "platforms": ["linux-x86_64", "macos-arm64"],
    "rest": { "port": 8000, "entry": "viva_pde_particle.server:app" },
    "git_entry": "viva_pde_particle.pblang_entry:make_process"
  },
  "types": [
    { "name": "positive_float", "schema": { "_type": "float" }, "opaque": true }
  ],
  "components": []
}
```

A component entry is a **superset of the workbench's `RegistryProcess`** so the workbench can adopt it unchanged:

```json
{
  "name": "GridCountsToMeshConcentration",
  "address": "local:!viva_pde_particle.steps.transfer.GridCountsToMeshConcentration",
  "aliases": ["GridCountsToMeshConcentration"],
  "kind": "adapter",
  "base": "step",
  "config_schema": { "grid": "map", "mesh": "map", "species": "list[string]" },
  "config_docs": {
    "grid": "CartesianGrid spec (origin, size, shape)",
    "mesh": "mesh spec"
  },
  "ports": {
    "inputs": { "particle_counts": "map[array[float]]" },
    "outputs": { "particle_conc": "map[overwrite[array[float]]]" }
  },
  "port_semantics": {
    "outputs": { "particle_conc": "overwrite" },
    "inputs": { "particle_counts": "read" }
  },
  "dynamic_ports": { "dynamic": false },
  "contract": {},
  "interval": { "configurable": false },
  "docs": {
    "summary": "Grid particle counts to P1 mesh concentration (P^T).",
    "source": "steps/transfer.py:140"
  },
  "examples": [
    "viva_pde_particle/composites/hybrid.py#build_mesh_hybrid_document"
  ],
  "adapter": {},
  "fingerprint": "sha256:…"
}
```

`kind` is one of `process | step | adapter | emitter | visualization | draft | composite_generator | composite | type`.
`composite_generator` entries carry `parameters`, `emitters`, `builder` and `tags`; `composite` entries copy the
package's `*.composite.yaml` fields. `fingerprint` is the sha256 of the canonical JSON of `{address, config_schema,
ports}` and is what preflight compares.

`dynamic_ports` has three shapes: `{"dynamic": false}`; `{"dynamic": true, "depends_on": ["emit_positions"], "how":
"defaults", "note": "…"}` (ports listed are those obtained with default config; the checker hints when those keys are
set); `{"dynamic": true, "rule": "union_of_children", "children_key": "process"}` (`Stepper`) or `"adapters"` plus
`"pde"`, `"particles"` (`SplittingCoordinator`): ports are computed from the DSL edge literals once the children's
manifests are imported.

A first generated example lives in the repository: `tests/fixtures/data/v2/interfaces/` holds the interface files and
`viva_pde_particle.manifest.json` that `python -m process_bigraph_lang.v2 describe` produced from viva-pde-particle's
classes in that package's own environment. They show the honest output for ports the generator cannot see
(`inputs { ... }` plus a `// TODO: dynamic ports` note on `Stepper`, `SmoldynHybrid` and `SpatialRecorder`), and
`process_bigraph_lang/v2/check.py` uses them to verify the hybrid composite without importing process code.

### 1.3 Stage A: `pblang-describe`

A tiny distribution (`packages/pblang-describe/`; deps: process-bigraph and bigraph-schema only). CLI:
`python -m pblang_describe --package viva_pde_particle [--core viva_pde_particle.core:build_core] [--build-generators]
-o manifest.raw.json`. Per package:

1. Enumerate `Edge` subclasses of the package's own modules (the `find_edges` logic from
   `bigraph_schema/package/discover.py`, filtered by module prefix), never `allocate_core()` over all distributions. Use
   the package's `build_core()` if given, else a plain core plus its `register_types` hook.
2. Copy `config_schema` as authored and also run `core.access` on it, recording `config_schema_errors[]` (this is where
   `int` and `any` are caught at publish time).
3. Ports by a ladder, recording which rung succeeded in `dynamic_ports.how`: `DraftProcess` attributes →
   `cls.inputs(cls)` with the class as `self` → instantiate with `core.default(config_schema)` and call
   `inputs()`/`outputs()` → override file → `null` with the exception text. Rungs that disagree mark `dynamic: true`;
   `depends_on` comes from an AST scan of `inputs`/`outputs` for `self.config[...]` keys (the technique
   `process_bigraph/contract_drift.py` already uses).
4. `port_semantics`: `overwrite` if the type contains `overwrite[`, `set` if the resolved schema replaces, else
   `accumulate`; `read` for inputs. An optional class attribute `port_semantics = {...}` overrides.
5. `contract`: `resolve_contract(...)` serialized, with the `audit_contract`/`completeness` grade.
6. `kind`: emitter (plus `EmitterContract` fields when viva-emitters is present), visualization, adapter (class
   attribute `adapter`), draft, else by MRO.
7. Composite generators and `*.composite.yaml`, restricted to the package.
8. Never abort on one class: per-component `errors[]`, overall `status: ok|partial`.

### 1.4 Stage B: `pblang registry build` and `verify`

`pblang registry build <pkg-dir>` reads `manifest.raw.json`, parses `interfaces.override.pblang` with the normal grammar,
merges by name (override wins per field: ports, docs, adapter, dynamic_ports, contract rows), fills git ref and commit,
computes fingerprints, writes `manifest.json` and renders `interfaces.pblang` with a header naming the manifest hash.
`pblang registry verify` rebuilds in a temporary directory and diffs; it is the CI gate.

### 1.5 CI and the catalog

- Per repo: a reusable `publish-interfaces.yml` published from viva-catalog and scaffolded by pbg-template. On push to
  main and on tag: install the package in its own env, run stage A, `pipx run process-bigraph-lang registry build`,
  verify; bot-commit `pblang/*` on main if stale; attach the manifest and interface file as release assets. The wheel
  includes `pblang/*` as package data.
- viva-catalog nightly: for each `modules.json` entry fetch `<source>/<ref>/<package>/pblang/manifest.json`; aggregate
  into `ecosystem-interfaces.json` and a flat `components.json` for search. Packages without a manifest keep their
  AST-scanned entry marked `"interface": "unpublished"`. This replaces the closed PR's idea of AST-extracted ports.

### 1.6 Versioning and staleness

- `import pkg;` with an optional `@range`. Resolution order: explicit paths from `pblang.toml` → the installed
  distribution's manifest (via `importlib.metadata`, no import) → the catalog cache (`pblang registry fetch`).
- Lock file `<workflow>.pblang.lock.json` (`pblang-lock/1`): package version, ref, commit, manifest sha, and component
  fingerprints. `pblang lock` writes it; `pblang check` warns on drift.
- `pblang preflight` in the execution env compares the installed version to the lock, then runs stage A for only the
  referenced classes and compares fingerprints, reporting a port-level diff when an interface is stale.

### 1.7 What ships today: `pblang-manifest/0`, one manifest per environment

Decided 2026-10-12 (see the [stage two plan](authoring-plan.md)). Sections 1.1 to 1.6 remain the target; what exists
is smaller, and one decision changes the unit: **a manifest describes an environment, not a package.** `describe` must
import the classes inside the environment that will run the document, and environments differ (compose-api's shared
image carries process-bigraph 1.0.5, viva-pde-particle's image 1.8.x and its own core).

- **Producer.** `process_bigraph_lang/v2/describe_env.py` is stage A in its smallest form: one file, standard library
  only, importing nothing from this package, so it runs as a plain script in any image or env:
  `python describe_env.py viva_pde_particle --env-name viva-pde-particle --image <ref> > manifest.json`. It imports
  every module under the given roots (a failed import is recorded, never fatal), keeps the step and process classes each
  module defines, and shares its per-class code with `describe_module`. compose-api runs it in CI inside each
  environment it offers and serves the result at `GET /registry/environments/{name}/manifest`.
- **Consumers.** `Pblang.addManifest` / `setManifests` (main thread) and the language server's `pblang/setManifests`
  notification (`SET_MANIFESTS_NOTIFICATION`; a host editor sends it when the environment is known or changes, and every
  open document is re-checked). A component with a known address replaces the earlier one; another `schema_version` is
  rejected.

The format carries no DSL syntax: types stay in bigraph-schema's own string or dict forms, addresses in
process-bigraph's `local:!module.Class` form, so any tool that can read a bigraph-schema type (a core's `access`, the
workbench, a prompt-driven skill, another checker) can use it as it is.

| Key                                     | Content                                                                                                                                                                             |
| --------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `schema_version`                        | `"pblang-manifest/0"`                                                                                                                                                               |
| `environment`                           | `{name, image, python, process_bigraph, bigraph_schema, packages {dist: version}, roots, generated_by}` (from `describe_env.py`)                                                    |
| `components[]`                          | one per step or process class, sorted by address                                                                                                                                    |
| `.name`, `.kind`, `.address`, `.module` | class name; `process` or `step` (by MRO); `local:!module.Class`; the defining module                                                                                                |
| `.config`                               | `{key: {type, default?}}` from `config_schema`: the type as authored (string or dict, else `null`), the default when the type carries one (`{"_type": T, "_default": v}` or `T{v}`) |
| `.inputs`, `.outputs`                   | `{port: type}` from `inputs()` / `outputs()` called with the class as `self`; `null` when they need an instance                                                                     |
| `.dynamic_ports`                        | `true` when the ports need an instance (config-dependent or children's)                                                                                                             |
| `.doc`                                  | the first paragraph of the class docstring, when there is one                                                                                                                       |
| `errors[]`                              | `{module, error}` per module or class that failed (from `describe_env.py`)                                                                                                          |

Not yet in `/0`, compared with section 1.2: units and contracts, port semantics, adapter metadata, fingerprints, a
published JSON Schema.

## 2. Adapters as first-class entries

An adapter is a step whose purpose is to map one face to another (grid particle counts → mesh concentration field).
Metadata, declared as a class attribute `adapter = {…}` or in the override file:

```json
{
  "from": {
    "port": "particle_counts",
    "layout": "grid",
    "quantity": "count",
    "units": "molecule"
  },
  "to": {
    "port": "particle_conc",
    "layout": "mesh_p1",
    "quantity": "concentration",
    "units": "uM"
  },
  "shared_config": ["grid", "mesh", "species"],
  "method": "transpose interpolation P^T",
  "exact": false,
  "conserves": ["mass"],
  "cost": "O(n_grid)"
}
```

Non-adapter ports carry `_layout` and `_quantity` rows in the contract's documentary port dicts (free-form per
`ProcessContract`, ignored by existing code). A controlled vocabulary lives in `docs/vocab/faces.json` (layouts
`scalar, grid, mesh_p1, mesh_dg0, positions, per_species_map`; quantities `count, concentration, amount, rate, flux,
field, positions, time`; `x-` extensions). viva-pde-particle's DESIGN.md §13 component contract maps directly onto it.

`pblang suggest-adapter` scores adapters by layout and quantity match (required), unit convertibility (pint), and
`core.resolve` on both sides, and returns ranked candidates with the shared config to fill and an insertable DSL snippet.
A check (`W230`) fires when an adapter's shared config literal differs from the producer's.

## 3. Prompt-guided authoring loop

### 3.1 Tool surface

Every command takes `--json`; exit 0 clean, 1 diagnostics with errors, 2 usage or internal error.

| Command                                                                                                    | Output                                                                                                |
| ---------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| `pblang registry search <q> [--kind] [--tag] [--input-type] [--output-type] [--face face.json]`            | ranked components; face mode is `find_candidates` semantics over manifests, no import                 |
| `pblang registry show <ref>`                                                                               | full entry, rendered declaration, a minimal instantiation snippet, `dynamic_ports` explanation        |
| `pblang registry fetch / build / verify / sources`                                                         | lock-style records, verify diff                                                                       |
| `pblang check <file> [--level parse\|scope\|types\|wiring\|ground\|env]`                                   | diagnostics document (§4.5)                                                                           |
| `pblang explain <CODE>`                                                                                    | `{code, title, why, fix, example_before, example_after, links}`; the same text the LSP shows on hover |
| `pblang suggest-adapter <file> --from a.port --to b.port`                                                  | candidates with `why`, `shared_config`, snippet and LSP edits                                         |
| `pblang fmt <file>`                                                                                        | canonical text                                                                                        |
| `pblang compile <file> --to yaml\|document\|template [--params k=v] [--exec-plan local\|rest\|git] -o out` | the artifact plus a source map `out.pblang.map.json` (document path → DSL range)                      |
| `pblang decompile <x.composite.yaml\|doc.json> -o file.pblang`                                             | best-effort text plus a list of what could not be expressed                                           |
| `pblang doc <file> --format md\|json\|html`                                                                | Markdown narrative plus graph JSON (§3.3)                                                             |
| `pblang preflight <file> [--python <exe>] [--suggest-env]`                                                 | §5                                                                                                    |
| `pblang lock <file>`                                                                                       | lock file                                                                                             |

### 3.2 Skill flow (`/viva-compose`, in viva-superpowers)

```text
1. Orient: `pblang registry sources`, `pblang registry search --json <intent keywords>`; with --from, `pblang decompile`.
2. Select: for each role (engine, adapter, emitter) `registry show`; prefer kind=adapter for face gaps; never invent ports.
3. Draft: write <slug>.pblang (file-level `///` intent, `param` for anything a study would vary, `emit` for observables).
4. Fix loop (bounded): `pblang check --json`; apply `fix.edits` when present, else `pblang explain CODE`;
   wiring warnings -> `pblang suggest-adapter`; groundness -> ask the user or `?(default)`; stop at zero errors.
5. Document: `pblang doc -o <slug>.md`; present the DSL and the doc to the user; wait for approval.
6. Materialize: `pblang lock`; `pblang compile --to yaml -o composites/<slug>.composite.yaml`.
7. Preflight: `pblang preflight --json`; report missing packages with the manifest's install hints; hand off to the run skill.
Hard gates: never hand-edit the generated .composite.yaml; never silence a diagnostic by widening a type.
```

Sibling skills: `/viva-publish-interfaces` (runs stage A and B in a package repo and opens the override file for anything
with `ports: null` or `dynamic: true`) and `/viva-adapt` (a thin wrapper on `suggest-adapter`).

### 3.3 Documentation generation

`pblang doc` merges three sources: `///` doc comments, registry docs and contracts per component, and the wiring graph
from the compiled model. Markdown sections: Overview; Parameters (name, type, default, units, doc); Components (name,
kind, package@version, interval, summary); Stores (type, units, writers → readers with `overwrite`/`accumulate` badges);
Wiring narrative per store; Open sites; Diagnostics summary; Provenance (lock entries, pblang version, manifest hashes).
Graph JSON `{nodes, stores, edges, groups}` feeds a small adaptor for loom and `bigraph_viz`. The user reviews the
`.pblang` and the Markdown; the `.composite.yaml` is a build artifact with a header naming its source and a CI check
that regenerates and diffs it.

## 4. Validation and error UX

### 4.1 Layers and code families

Codes carry a family prefix and a stable slug (`W200 wire-type-mismatch`).

| Layer               | Where                                                               | Family | Examples (message → fix hint)                                                                                                                                                                                                                                                                                                                                                                                                      |
| ------------------- | ------------------------------------------------------------------- | ------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Parse               | Langium and CLI                                                     | `P0xx` | `P001 expected '}'`                                                                                                                                                                                                                                                                                                                                                                                                                |
| Scope and imports   | Langium and Python resolver                                         | `S0xx` | `S010 package 'viva_smoldyn' not found in any registry source` → fetch hint; `S011 lock pins 0.3.1, resolved 0.4.0`; `S020 unknown component` → did-you-mean; `S021 unknown port`, noting `dynamic_ports.depends_on`; `S022 unknown config key`                                                                                                                                                                                    |
| Types               | Python core seeded with manifest `types`                            | `T1xx` | `T100 unknown type 'int'` → "bigraph-schema has 'integer'"; `T110 value 3 is not a float`; `T120 config 'species' expects list[string]`; `T140 opaque type checked loosely` (info)                                                                                                                                                                                                                                                 |
| Wiring and contract | Python                                                              | `W2xx` | `W200 wire type mismatch` via `core.resolve_schemas`; `W201 unit mismatch`; `W210 port bound twice`; `W211 required input unbound`; `W220 two accumulating writers on store`; `W221 overwrite writer plus another writer`; `W223 step publishes a whole array with accumulate semantics` → "did you mean overwrite[...]"; `W230 adapter shared config differs`; `W240 emit path matches no store`; `W241 observable never written` |
| Groundness          | Python (`open_sites`, `admits_why`, `registry_dependent_addresses`) | `G3xx` | `G300 required site unfilled`; `G301 filler rejected` (text from `admits_why`); `G302 non-portable address` → `local:!…` from the manifest                                                                                                                                                                                                                                                                                         |
| Env preflight       | Python, execution env                                               | `E4xx` | `E400 not installed` + install lines; `E401 version differs from lock`; `E402 interface stale` with a port diff; `E403 address unresolvable in core`; `E404 native dependency import failed`                                                                                                                                                                                                                                       |
| Runtime             | wrapper around `Composite`                                          | `R5xx` | process-bigraph exceptions mapped through the source map to a DSL range                                                                                                                                                                                                                                                                                                                                                            |

### 4.2 Additive vs overwrite

The registry records `port_semantics` per port; rendered interfaces show it. The checker builds the store graph
statically (like `process_bigraph/composite_audit.py`) and emits `W220`, `W221` and `W223`; `pblang explain W223`
carries the one-paragraph explanation of bigraph-schema's apply semantics with before and after snippets.

### 4.3 Reuse of bigraph-schema and process-bigraph

Type names through `core.access` on a validation core (rejecting on exception instead of passing strings through);
wire types through `core.resolve_schemas`; units and ranges through `units_compatible` and `range_subsumes`; sites
through `admits_why` and `required_open_sites`; addresses through `registry_dependent_addresses` and
`unresolvable_addresses`; contract grades copied into manifests at publish time.

### 4.4 TypeScript and Python

Decided 2026-10-12: the checker is TypeScript, inside the Langium services, because its inputs are data (the
document and header manifests) and a browser must validate without a round trip. Python does what needs an
environment: `describe`, saved documents with numpy, equivalence through a core, groundness, preflight, running.
A browser-based authoring tool therefore needs a Python-backed API only for those environment-bound operations.
The earlier plan (Langium for syntax only, Python for the type algebra, the language server shelling out to
`pblang check` on save) is superseded by that decision. Manifests reach the checker as data: through `--interfaces` in
the CLI, `addManifest`/`setManifests` in the API, and `pblang/setManifests` in a language server (section 1.7).

### 4.5 Diagnostics JSON (`pblang-diagnostics/1`)

```json
{
  "version": "pblang-diagnostics/1",
  "file": "/abs/hybrid.pblang",
  "ok": false,
  "summary": { "error": 1, "warning": 1, "info": 0, "hint": 1 },
  "diagnostics": [
    {
      "code": "W200",
      "slug": "wire-type-mismatch",
      "severity": "error",
      "layer": "wiring",
      "message": "wire type mismatch: conv.particle_conc is map[overwrite[array[float]]] but store 'conc' is map[float]",
      "range": {
        "start": { "line": 41, "character": 6 },
        "end": { "line": 41, "character": 32 }
      },
      "path": "cell/conv/outputs/particle_conc",
      "related": [
        { "file": "…", "range": {}, "message": "store 'conc' declared here" }
      ],
      "fix": {
        "hint": "change the store type, or insert an adapter",
        "edits": [{ "range": {}, "newText": "map[array[float]]" }],
        "command": "pblang suggest-adapter hybrid.pblang --from conv.particle_conc --to pde.external_conc"
      },
      "explain": "pblang explain W200"
    }
  ]
}
```

Ranges are LSP zero-based; edits are LSP `TextEdit`s so the skill and the editor apply the same fix. JSON Schema at
`docs/schemas/diagnostics.schema.json`.

## 5. Execution without one giant environment

Interfaces being data removes the package from the authoring loop. For running, the manifest `environment` field maps
to options:

| Option                              | Manifest fields                 | Use                                                                                                                                         |
| ----------------------------------- | ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| Local env with everything installed | `install`                       | `preflight` reports `E4xx` with install lines; `--suggest-env` writes a merged requirements or pixi fragment                                |
| `rest:` process servers             | `rest.port`, `image`            | `compile --exec-plan rest --endpoint pkg=URL` rewrites addresses; one container per package image via compose-api; face conformance at bind |
| `git:` per-SHA venv                 | `git_entry`, `source`, `commit` | needs a `make_process(name, config)` entry convention; defer                                                                                |
| Whole-composite image               | each package's `image`          | not realistic; prefer `rest:`                                                                                                               |

First step: the `environment` field plus `pblang preflight`. Then `rest:`, which already exists and matches the
workbench and compose-api direction.

## 6. Integration points

- **vivarium-workbench**: consume `manifest.json` for installed packages (fall back to stage A inside `env_worker` for
  unpublished workspace packages, so there is one registry model); `RegistryProcess` gains `manifest_ref`,
  `dynamic_ports`, `port_semantics`, `adapter`, `fingerprint`; published/introspected/stale badges; a workflow view hosting
  the existing Monaco and Langium worker plus a diagnostics panel; parameter forms from `compile --to yaml`.
- **viva-catalog**: `modules.json` gains `manifest_path`; nightly `ecosystem-interfaces.json` and `components.json`;
  hosts the reusable workflow.
- **viva-superpowers**: `/viva-compose`, `/viva-publish-interfaces`, `/viva-adapt`; `docs/conventions/interfaces.md`;
  `composites.md` documents `requires.packages` and the generated-file header.
- **pbg-template**: scaffold `pblang/`, the override stub, the workflow and schema references.
- **Upstream asks** (process-bigraph, bigraph-schema): `python -m process_bigraph.describe` (adopt stage A),
  `Edge.port_semantics()`, an `Edge.adapter` marker, `Edge.ports_depend_on`, JSON-safe `ProcessContract.to_dict()`,
  `find_candidates` over manifests, CompositeSpec `requires.packages`, `core.access(strict=True)`, bigraph-schema#188,
  process-bigraph#213.
- **This repo**: `process_bigraph_lang/registry/` (manifest models, resolver, search, render, stage B),
  `process_bigraph_lang/check/` (diagnostics model, checks, preflight), `process_bigraph_lang/cli.py` (`pblang`),
  `packages/pblang-describe/`, `docs/schemas/*.json`, `docs/vocab/faces.json`.

## 7. Roadmap

| Phase | Scope                                                                                                                                                                                                                                          | Validation                                                                                                                                         |
| ----- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1     | design docs and the round-trip prototype in this repo (see the [plan](plan.md))                                                                                                                                                                | corpus round-trips; snapshots reviewed                                                                                                             |
| 2     | DSL v2 grammar (Langium), `compile`/`decompile`/`doc`/`check` CLI, lock, LSP forwarding of Python diagnostics                                                                                                                                  | round-trip viva-smoldyn and viva-vcell-fvsolver yamls; compiled documents run under `Composite`                                                    |
| 3     | publish real interfaces: viva-pde-particle (overrides for Stepper, SplittingCoordinator, SmoldynHybrid; adapter metadata on the transfer steps), viva-smoldyn, viva-emitters; catalog aggregation and reusable workflow; pbg-template scaffold | the catalog serves ports; `registry search --face` finds the grid-counts → mesh adapter; `verify` green in CI                                      |
| 4     | authoring loop and workbench integration                                                                                                                                                                                                       | the pde-particle hybrid rebuilt from DSL via the skill with no hand-edited yaml runs in the workbench; error-UX review against the pain-point list |
| 5     | execution without one env: `environment`, `preflight --suggest-env`, `--exec-plan rest` with compose-api                                                                                                                                       | the hybrid runs with Smoldyn in a separate container; preflight catches a deliberately stale interface                                             |
| 6     | upstreaming and hardening                                                                                                                                                                                                                      | describe, markers and strict access land upstream; heuristics leave stage A                                                                        |

Risks: bigraph-schema version skew (the toolchain floor must be ≥ 1.7 for `matching` and `audit_contract`;
feature-detect); dynamic ports are a long tail (override files are the escape hatch; `check` degrades to hints, never
silence); custom `Node` types with Python apply behaviour cannot be data (validate loosely and say so); TypeScript and
Python validators drifting (a shared fixture corpus run by both suites); generated-file drift (verify gates on both
sides).
