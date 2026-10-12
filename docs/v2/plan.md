# v2 implementation plan

Status: approved scope for the first round, 2026-10-11. See the [research notes](research.md), the
[language design](design.md) and the [registry and authoring design](registry-and-authoring.md).

## Decisions

1. This round delivers the **design documents** (done: this directory) and a **round-trip prototype** that reads real
   documents and `*.composite.yaml` files into a v2 model, prints canonical `.pblang` v2 text for review, writes an
   equivalent document back, and proves equivalence. The Langium v2 grammar and the `pblang` CLI come in later rounds.
2. The v2 syntax is tree-shaped and mirrors the document.
3. Interfaces come from generated `.pblang` interface files (manifest JSON canonical).
4. The DSL interoperates both ways with CompositeSpec yaml.
5. The DSL is a verifiable target layer; end users author with registry- and prompt-driven tools.
6. The language core stays one-to-one with the document. The higher-level semantics it adds are static and compile
   away: named and imported interfaces, faces as sorts, `param`, `let`, edge literals, adapters, units, and
   referential-integrity checks. There is no pattern or macro layer this round; coupling schemes and engine selection
   stay in Python builders or composite generators, and the DSL records their result.

Reconciled details:

- **Type spelling** in the DSL: `int`, `bool`, `float`, `string`, `map<string, V>`, `list<T>`, `maybe<T>`,
  `overwrite<T>`, `enum<a, b>`, `array<float>[3,3] @ "uM"`, `{ a: T; b: U }`, `A | B`, raw `"…"`. The compiler maps
  `int` → `integer`, `bool` → `boolean`, `map<string, V>` → `map[V]`; unknown names are errors.
- **Error codes**: family-prefixed numeric codes with a stable slug (`W200 wire-type-mismatch`); the mnemonic names in
  the language design are the slugs.
- **`emit`**: `emit parquet { … } with { … };` or `emit "local:ParquetEmitter" { … };`.
- **Interfaces in decompiled text**: resolved addresses print `import pkg.{Name}`; unresolved ones print an inline
  declaration from `_inputs`/`_outputs` and `at "…"`.
- **Parsing this round**: the model is the pivot; text is printed and snapshotted. A Lark parser is a stretch step; the
  Langium grammar remains the long-term source of truth and binds to the same model.
- **Dependencies**: no version bump of process-bigraph or bigraph-schema (nothing needed is 1.7-only). `bigraph-schema`
  moves to the main dependencies; `process-bigraph` stays dev-only (the package returns plain dicts); `pyyaml` and
  `types-PyYAML` join the dev group.

## Layout

`process_bigraph_lang/v2/` (shipped; mypy strict and ruff apply; it outlives the prototype as the target of the later
Langium v2 AST binder):

| Module         | Responsibility                                                                                                                                                                        |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `model.py`     | dataclasses `Document, Composite, Store, Node, Edge, Site, Face, Param, Emitter, Import, InterfaceDecl, Address, ParamRef, ExternalRef, Path`; `MISSING` sentinel; no bigraph imports |
| `types.py`     | `TypeExpr` tree (`Named, Struct, Union, Group, Raw`); `parse_type(str \| dict)` via `bigraph_schema.parse.parse_expression`; `to_bigraph()`; `to_surface()`                           |
| `values.py`    | predicates, tuple and ndarray handling, externalization thresholds                                                                                                                    |
| `paths.py`     | `Path.from_wire` / `to_wire`; reuses `compiler.generator.compute_relative_path`                                                                                                       |
| `reader.py`    | `read_document({schema, state})` for authoring and saved forms; `read_composite_spec(dict)`                                                                                           |
| `writer.py`    | `write_document(Document, assets=…)` → `{schema, state, **options}`; `write_composite_spec(Document)`                                                                                 |
| `printer.py`   | `print_document(Document)` → `(text, assets)`                                                                                                                                         |
| `normalize.py` | `normalize_document`, `equivalent`, `diff_documents`                                                                                                                                  |
| `__main__.py`  | `python -m process_bigraph_lang.v2 print \| diff …`                                                                                                                                   |

Reused from v1 without copying: `compiler/converter.py` (`edge_address`, `site`, `set_value_at_path`,
`get_value_at_path`) and `compiler/generator.py` (`compute_relative_path`; `type_schema` as the reference for string vs
dict type emission). v1 stays untouched and green.

## Reader rules

Walk `state` and `schema` in parallel, state key order first. Classify each key in order:

1. **Site**: `_type == "site"` → `Store(site=Site(sort, default))`.
2. **Edge**: `_type` in process/step, or `address` present, or the schema entry says edge. Kind from state `_type` →
   schema `_type` → `interval` present → process → `priority`/`_triggers` → step → else `ValueError` naming the path.
   `address` from `"proto:data"`, dict, `${x}` or site. Consume `config, inputs, outputs, interval, priority,
_triggers, _inputs/_outputs (→ ports)`; drop `instance` and `_contract`; everything else → `extras` verbatim.
   Short name `Composite` → `inner` from `config.state`/`config.schema`, `bridge`, `interface`. A Stepper-style child
   `{address, config}` inside config stays a plain struct value (lossless).
3. **Node**: a dict with an edge or site descendant, or a struct schema, or a `map` schema of edges (`Node(type=…)`).
4. **Store**: everything else; typed from the schema when present; schema-only → `value=MISSING`.

Saved form is auto-detected (root `global_time`, dict addresses, `_contract`): also drop root `global_time`, take edge
`_type` from the schema entry, ignore the schema's `inputs: "wires"` entries, parse string `_inputs`/`_outputs`, keep
fully defaulted config verbatim. Params come only from CompositeSpec `parameters`; `^\$\{(\w+)\}$` strings become
`ParamRef`, embedded ones `ParamRef(template=…)`, undeclared ones are errors. Imports come from `local:!a.b.C` addresses
(collisions print fully qualified); `local:Name` prints as `Name` with no import. Interface declarations are emitted
only for edges that carry ports. CompositeSpec metadata (`name, description, tags, requires, emitters,
global_time_precision`) is read; other keys go to `extras`.

## Printer rules

Order: a header comment naming the source; sorted imports; params; interface declarations in first-use order;
`composite name "description" { requires {…} options {…} stores and sites, then nodes, then edges, each in source order
}`; `emit …`. Two-space indent; a block prints inline when it fits in 100 columns and no nested block broke. Values:
ints as ints, floats via `repr`, `true`/`false`/`null`, JSON-escaped double-quoted strings, lists `[…]`, tuples `(…)`
(preserved so v1 parity holds), struct literals when all keys are identifiers else map literals, `${dt}`, `?` and
`?(default)`. Arrays and nested lists with more than 100 elements and strings longer than 1000 characters are
externalized to `<snapshot>.assets/<path-slug>.json|txt` (JSON `{dtype, shape, data}` for diffability; `ExternalRef`
keeps a `$bundle_ref`-compatible key) and printed as `array(file("…"), dtype = "float64", shape = [11, 11, 3])` or
`file("…")`; small arrays print inline with an `array(…)` wrapper. Port overrides print as `ports { … }`; unknown keys
print as `extra { … }` or `schema { … }` as explicit "not understood" markers. A saved nested composite with empty inner
state prints a `// WARNING: inner state lost by Composite.save` comment.

## Writer rules

Schema half: `Store.type` → `to_bigraph` with the default folded as `{"_type": T, "_default": d}` (v1's exact shape);
untyped stores → no entry; **sites → no schema entry** (process-bigraph#213); `Node` → nested dict or
`{"_type":"map","_value":…}`; edges → no schema entry; `schema_extras` merged back. State half: values; sites via
`converter.site`; edges `{"_type", "_inputs"/"_outputs", "address", "config" (omit empty), "inputs"/"outputs" (omit
empty), "interval"/"priority"/"_triggers", **extras}`; a nested composite → `config = {state, schema?, bridge,
interface, …}`. `ParamRef` → `"${name}"`; `ExternalRef` → loaded through the `assets` callback.
`write_composite_spec` → `{name, description, tags, requires, parameters {type (normalized by
`composite_spec.normalize_type`), default, description, choices}, emitters [{address, paths ["a/b"], config?}],
schema?, state, global_time_precision?, **extras}`; tests dump it with `yaml.safe_dump(sort_keys=False)` and feed
`CompositeSpec.from_dict(...).to_document(emit=False)`.

Parity target: `write_document(read_document(doc)) == doc` **exactly** for every v1 expected template in
`tests/compiler/generator/` (toy add-floats, `test_collections` flat/list/map, spatio-flux I/II/III,
`test_open_values_compile_to_template_sites`).

## Normalizer (behaviour verified against the installed versions)

`normalize_document(doc, core)`: in the schema half drop `global_time`, move edge entries to a side table
(`{path: {_type, _inputs, _outputs}}`), and render other entries with `core.render(core.access(entry), defaults=True)`,
falling back to a canonical sorted dict when `access` raises on an unknown dict-form type (string names pass through); a
rendered string containing a top-level `|` or `:` is re-accessed to dict form so `"x:float|y:float"` and
`{"x":"float","y":"float"}` collide. In the state half drop root `global_time`; render sites with `_sort`
canonicalized; edges become `{_type (state or side table), address as "proto:data", _inputs/_outputs canonical (omitted
if absent on both), config canonical (omit {}), inputs/outputs canonical wires (str → [str]; omit empty),
interval/priority as float, _triggers}`; drop `instance` and `_contract`; recurse into nested `local:Composite`
config. Values: tuple → list, ndarray → `tolist()`, numpy scalars → Python, floats compared with
`math.isclose(rel_tol=1e-9)`. `diff_documents` flattens to `state/smoldyn/config/dt`-style paths and prints `-`, `+`,
`~` lines (capped at 200), falling back to a unified JSON diff.

Ignored: key order, tuple vs list, dtype, runtime keys, string vs structured forms of addresses, wires and types,
absent vs `{}` config, default-in-schema vs `float{…}`, schema edge entries. Not ignored: config values. A stronger
`realized_equivalent(a, b, core)` (tests only) builds `Composite` from both and compares `serialize_state()` and
`serialize_schema()` through the same normalizer.

## Corpus and tests

```text
tests/v2/
  conftest.py, helpers.py            core and spatio_core fixtures, corpus loader, assets loader, realized_equivalent,
                                     assert_snapshot (PBLANG_UPDATE_SNAPSHOTS=1 regenerates)
  test_types.py                      table-driven parse / to_bigraph / to_surface including the render quirks
  test_reader.py                     classification rules, saved form, extras, params, imports, nested composite
  test_writer_v1_parity.py           exact equality for every v1 expected template
  test_printer.py                    inline/multiline, quoting, float repr, tuples, externalization, ordering, naming
  test_normalize.py                  quirk pairs collide; saved toy ≡ authoring toy; diff shape
  test_roundtrip_corpus.py           parametrized over the corpus: equivalent(original, write(read(original))) with a
                                     diff on failure; printed snapshot == committed .pblang (+ assets);
                                     realized_equivalent where runnable
tests/fixtures/data/v2/
  corpus/README.md                   provenance and regeneration commands
  corpus/reversible-dimerization.composite.yaml   verbatim copy from viva-smoldyn (prettier reformats it; noted)
  corpus/hybrid_two_way_exchange.json             generated once in viva-pde-particle's pixi env by
                                     corpus/make_hybrid_fixture.py (examples.two_way_exchange(core=None) on the
                                     11×11×3 slab; SpatialRecorder attached with viz3d.record.attach_recorder;
                                     dumped with bigraph_schema.json_codec); not collected by pytest
  corpus/template_sites.json         the expected dict from test_open_values_compile_to_template_sites
  snapshots/<name>.pblang (+ <name>.assets/*)     printed text, committed, reviewed by hand
```

| #   | Corpus entry                                         | Source                                                                                                     | Checks                                                                                                                                                |
| --- | ---------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | viva-smoldyn reversible dimerization                 | yaml copy                                                                                                  | spec-level equivalence; `CompositeSpec.from_dict(written).to_document(emit=False)` ≡ `from_file(...)`; snapshot. No run (Smoldyn not installed here). |
| 2   | viva-pde-particle hybrid two-way exchange + recorder | generated JSON                                                                                             | Stepper child and recorder config preserved; large config text and arrays externalized; snapshot. No run.                                             |
| 3   | growth-division nested composite                     | built at test time from `process_bigraph.processes.growth_division.grow_divide_agent(path=["agent"])`      | equivalence and realized equivalence; a negative test documenting the save-loss trap and the printer warning                                          |
| 4   | spatio-flux I/II/III                                 | imported from the existing test modules                                                                    | indexed wires, ndarray state, dict-form `positive_array`; `spatio_core`; realized equivalence                                                         |
| 5   | template sites                                       | JSON copy                                                                                                  | equivalence; `template_document` fill with the bindings from `test_filled_template_runs_in_process_bigraph` runs                                      |
| 6   | saved toy add-floats                                 | built in the test from `Composite(...).serialize_state()/serialize_schema()` without the file-writing step | saved ≡ write(read(saved)); ≡ the authoring document after normalization                                                                              |

## Order of work

| Step         | Work                                                                                                                                                                  | Checkpoint                                                                           |
| ------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| 0            | design docs under `docs/v2/` and the mkdocs nav (done); `pyproject.toml` dependency moves; `poetry lock --no-update`; empty `v2/` and `tests/v2/`; `git add`          | `make check` green                                                                   |
| 1            | `types.py` + `test_types.py`                                                                                                                                          | every table row round-trips; render quirks covered                                   |
| 2            | `model.py`, `values.py`, `paths.py`                                                                                                                                   | mypy strict clean; path tests incl. ints, `..`, `*`                                  |
| 3            | `normalize.py` + `test_normalize.py`                                                                                                                                  | quirk pairs collide; saved vs authoring toy collide; diff readable                   |
| 4            | `reader.py` + `writer.py` (authoring form) + reader tests + v1 parity test                                                                                            | exact parity for all v1 templates                                                    |
| 5            | `printer.py` + snapshot harness + printer tests; snapshots for corpus 4 and 5                                                                                         | first `.pblang` snapshots committed; **read them for readability before continuing** |
| 6            | CompositeSpec read/write, params, emitters, metadata; corpus 1                                                                                                        | spec round-trip; snapshot                                                            |
| 7            | saved form + nested composite/bridge; corpora 3 and 6; `realized_equivalent`                                                                                          | equivalence and realized equivalence; save-loss negative test                        |
| 8            | externalization + `make_hybrid_fixture.py`; generate corpus 2 in the pixi env; snapshot                                                                               | the hybrid round-trips with Stepper and SpatialRecorder intact; assets diffable      |
| 9            | `__main__.py` (`print`, `diff`); update the design pages with the real snapshots; `docs/architecture.md` v2 section; CLAUDE.md pointer                                | `python -m process_bigraph_lang.v2 print …` works on all six; `make docs` builds     |
| 10 (stretch) | minimal stage A `describe` over `tests/fixtures/test_registry` → `interfaces.pblang` for toy_library and spatio_flux; the decompiler resolves `local:!…` against them | corpus 4/5/6 snapshots use `import`s instead of inline declarations                  |
| 11 (stretch) | Lark text parser for the printed subset bound to `model.Document`; `read_text(print(model)) == model` on all snapshots                                                | true text-level round trip; the grammar file becomes the Langium v2 acceptance spec  |

## Status (2026-10-11)

Steps 0–9 are implemented on the `v2-design` branch: the package, the tests, the corpus (all six entries, the
hybrid fixture generated in the viva-pde-particle environment), the snapshots and the `print`/`diff` entry point.
The snapshots in `tests/fixtures/data/v2/snapshots/` are the material for the design review. Observations from
printing the corpus that feed back into the design:

- The hybrid repeats the same `grid` literal in four places; the `let` hoisting in the design (section 2.3) is
  worth doing early, and the Stepper child prints as a plain `{ address, config }` struct until edge literals exist.
- Multi-line strings (the generated Smoldyn config) must be externalized at a much lower threshold than other text.
- Reading from a CompositeSpec alone leaves stores untyped (`store molecule_counts = {};`), which is exactly the
  `W-STORE-UNTYPED` case; types will come from interface files (stretch step 10).
- The saved form of a nested composite reads back with an empty inner composite; the printer flags it.

Stretch step 10 is also done in a minimal form: `process_bigraph_lang/v2/interfaces.py` has `describe_module`
(stage A over a Python module: portable address, `config_schema`, ports obtained with the class standing in for
`self`, `dynamic_ports` when that fails, the docstring), an `InterfaceRegistry` with a JSON manifest
(`pblang-manifest/0`), and `python -m process_bigraph_lang.v2 describe <module> --manifest m.json --out m.pblang`.
The printer resolves edge addresses against a registry and prints `import module.{Name};` instead of an inline
declaration; the spatio-flux and saved-toy snapshots show it, and `toy_library.interfaces.pblang` is the first
generated interface file.

Stretch step 11 is done too: `process_bigraph_lang/v2/parser.py` is a Lark LALR grammar for the printed subset
(imports, params, meta/options, inline interface declarations, stores, nodes, edges, nested composites with bridges,
sites, `ports`, `extra`, `schema`, `emit`, the `array(...)`/`file(...)` value forms, and the type spelling). Every
committed snapshot parses back into a model that prints to the same text and writes a document equivalent to the
corpus original (`tests/v2/test_parser.py`), so the round trip now runs from text. The grammar is the executable form
of the sketch in the design and the acceptance spec for the Langium v2 grammar. Not covered yet: expressions,
`replicate`, `{default}` suffixes on types, `when` / `of config.x` faces, and hand-written override files for
dynamic ports.

Two decisions made while building the parser: the normalizer canonicalizes types from the parsed type tree rather
than through bigraph-schema's renderer (the renderer drops custom type names such as `positive_float` and fails on
unknown dict-form types, so the two spellings of one type no longer collided), and `///` doc comments are joined with
spaces when parsed because the printer wraps them.

## Verification

1. `make check` (ruff, prettier, mypy strict, deptry, `poetry check --lock`) green after `git add` of new files.
2. `make test`: all v1 tests pass; `tests/v2/` passes, including the exact parity test and the corpus round trips with
   matching snapshots.
3. Manual review of every `tests/fixtures/data/v2/snapshots/*.pblang` against the examples in the language design; the
   hybrid snapshot must show the Stepper child, the recorder, `file()` and `array(file())` sidecars, and no `extra {}`
   blocks for keys that should have been understood.
4. `python -m process_bigraph_lang.v2 print tests/fixtures/data/v2/corpus/reversible-dimerization.composite.yaml`
   prints the snapshot text; `… diff a.json b.json` prints nothing for equivalent documents and a readable diff
   otherwise.
5. `make docs` builds with the four v2 pages in the nav.
6. If the stretch steps are reached: snapshots regenerate with `import` lines; `read_text(print(m)) == m` passes.

## Risks

Render quirks (handled by re-render and re-access; covered by tests); `local:Name` vs `local:!path` (kept verbatim;
the printer only imports `!` forms; the writer never rewrites); nested-composite save loss (authoring documents only;
negative test); numpy in config and state (`tolist` plus isclose; `array(…)` wrapper or sidecar); saved-form config
bloat (equality only claimed after normalization); deptry and mypy (no `process_bigraph` import in the package;
`yaml` test-only); snapshot churn (fixed ordering and `repr` floats; explicit regeneration flag); prettier reformatting
the copied yaml (accepted; noted in the corpus README).

## Out of scope this round

The Langium v2 grammar and `ast_model.py` changes; the `pblang check/compile/decompile/doc/registry` CLI beyond the
`v2 print | diff` entry point; manifests for real viva packages; viva-catalog, workbench, viva-superpowers and
pbg-template changes; execution-environment work (`rest:`, `git:`); upstream asks to process-bigraph and
bigraph-schema. These are sequenced in the roadmap of the [registry and authoring design](registry-and-authoring.md#7-roadmap).
