# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A domain-specific language (`.pblang`) for describing process-bigraph composites, shipped as:

- a **Langium** language server / VS Code extension / CLI (TypeScript, in `dsl/`) that parses, checks, compiles
  and decompiles it, and
- a **Python package** (`process_bigraph_lang/`) that calls that CLI (`compile`, `decompile`, `check`), describes
  Python packages and SBML models as headers, and compares documents, for **process-bigraph ≥ 1.8 /
  bigraph-schema ≥ 1.6**.

`docs/v2/` holds the design (`design.md`), the research notes, the registry/authoring design and the plan. The
language is a tree-shaped, verifiable projection of the composite document; the DSL text is the target that
authoring tools (prompt-guided or human) produce and that the checker verifies. **There is no Python model of a
composite**: never add a Python path to a runnable document that skips the checker.

## Commands

### Python (repo root, Poetry)

```bash
make install                 # poetry install + pre-commit hooks
make check                   # poetry check --lock, pre-commit on ALL tracked files (ruff, ruff-format, prettier), mypy, deptry
make test                    # pytest with coverage
poetry run pytest tests/v2/test_roundtrip_corpus.py::test_template_sites   # single test
poetry run mypy              # strict typing over process_bigraph_lang/ and tests/
make docs                    # mkdocs serve
python -m process_bigraph_lang.v2 compile | decompile | check | diff | describe | describe-model
```

Ruff line length is 120. `make check` is what CI's `quality` job runs. It only sees tracked files, so `git add`
new files before running it. `poetry install` runs `build.py` (`npm install` + native build), which dirties
`dsl/package-lock.json` when nothing changed in `package.json`; restore it with `git checkout dsl/package-lock.json`.

### DSL (`dsl/`, npm)

```bash
npm install
npm run langium:generate     # regenerate src/language/generated/ and syntaxes/ from the .langium grammar
npm run build                # tsc + esbuild -> out/
npm run lint
npm test                     # vitest run
npx vitest run test/v2/check.test.ts           # single test file
npx tsc --noEmit -p tsconfig.json              # type-check src/ AND test/ (vitest does not type-check)
npm run build:native         # also builds dist/cli-native with `deno compile` (Deno required, ~10 s)
npm run pack                 # the npm tarball (prepack regenerates and builds) into dist/, for other apps to install
# A GitHub release publishes the wheel to PyPI (on-release-main.yml) and dsl/ to npm as process-bigraph-lang
# (publish-npm.yml, trusted publishing: no npm token; the tag is the version)
./bin/cli.js check <file.pblang> [-i manifest.json...] [--json]
./bin/cli.js compile <file.pblang> [-i ...] [--to document|spec] [--strict] [--force] [-o out]
./bin/cli.js decompile <doc.json | x.composite.yaml> [-i ...] [--name n] [-o out.pblang]
./bin/cli.js headers <manifest.json> [-o dir]; ./bin/cli.js model-header <model.json>; ./bin/cli.js graph <file>
```

Run `langium:generate` after every grammar change; `src/language/generated/` is gitignored.

**`cli-native` is gitignored and must match the TypeScript.** After any grammar or TS change, rebuild it with
`python build.py` (also the Poetry build script, which is how CI builds it), or quickly with
`cd dsl && npm run build:native && cp dist/cli-native ../process_bigraph_lang/bin/`. The Python tests skip when
no CLI is built.

## The language (`dsl/src/language/pblang.langium`)

Language id `pblang`, files `.pblang` (and `.pbl`). A module is a flat list of statements:

- `module a.b;` (headers), `import a.b.{X, Y};` (`a.b.{` lexes as one `IMPORT_PATH` token), `param x: T = v;`
  (`= ?` open, `choices [...]`), `meta { ... }`, `options { ... }`, `emit alias { paths } with { ... };`.
- Interface declarations (headers): `process|step|adapter Name at "addr" { config { f: T = v; } inputs { p: T @
"units"; } outputs { ... } }`; `{ ... }` marks an open face (dynamic ports).
- Model declarations: `model Name from "file" { time @ "s"; species { A: float @ "uM" = 1.0; } ... }`; without
  `from` it is a sort; `_` stands for every member, a trailing `...` admits more.
- The composite tree: `composite name { store s: T = v; node n : T { ... } process p : Iface at ? every dt priority
k { config { ... } inputs { port -> path } outputs { ... } ports { ... } extra { ... } } composite c every dt {
bridge { ... } interface { ... } composite { ... } } shared process ...; schema { ... } }`.
- Values: ints, floats (`1.0`, `1e-3`), strings, `true`/`false`/`null`, `${param}`, `?`/`?(default)`/`? as T`,
  struct literals `{ a = 1 }` and map literals `{ "a" = 1 }`, lists, tuples `( ... )`, `array([...], dtype =
"float64")`, `file("...")`, a model reference by name. Paths: `../fields.A[0][1]`.
- Types: `float`, `int`, `bool`, `string`, `list<T>`, `map<string, V>`, `maybe<T>`, `overwrite<T>`, `enum<a, b>`,
  `array<float>[3, 3] @ "uM"`, `{ a: T; b: U; }`, `A | B`, `link<{...}, {...}>`, a raw string, and `float{0.5}`
  (bigraph-schema's default-in-type form). Keywords are admitted as keys and type names.

### The TypeScript side (`dsl/src/language/v2/`)

- `check.ts` is the checker, registered as a Langium validation (`validator.ts`); codes follow
  `docs/v2/registry-and-authoring.md` section 4 (`S021 unknown-port`, `W200 wire-type-mismatch`, `W211
store-not-declared`, `T121 config-missing`, `W220/W221/W223` writers, `W240/W241` emit, `W201`/`I230-I232`
  units, `G300/G301` model sites, ...). Diagnostics carry `code` and `data: {slug, path}`. Compliance suite:
  `dsl/test/v2/check.test.ts`.
- `headers.ts` (interface and model declarations from manifests and the text; `Registry.lookup` by address or
  unique short name), `types.ts` (type expressions: bigraph-schema's forms, the DSL spelling `surface`, a
  canonical form; parsed types keep their `source` so `toBigraph` is lossless), `units.ts` (mathjs; unit
  variables `?U`).
- `model.ts` is the object model: ints `bigint`, floats `number`, dicts `Map` (source order whatever the keys),
  tagged objects for numpy arrays (`$kind: "ndarray"`), tuples, params, sidecar refs, sites and model refs;
  `MISSING` for absent values. `json.ts` is the lossless codec (`__numpy__`, `__tuple__`); `yaml.ts` the
  CompositeSpec form with bigint ints.
- `reader.ts` (document/CompositeSpec → model), `writer.ts` (model → document/CompositeSpec), `printer.ts`
  (model → text + sidecar assets; `format.ts` reproduces Python's float repr and `json.dumps` so snapshots
  stay byte-identical), `bind.ts` (AST → model), `assets.ts` (sidecar decoding), `graph.ts`, `modelheader.ts`.
- `resolve.ts` is shared by the checker, `hover.ts` and `completion.ts`: which header an edge is declared by
  (inline, import, registry), how a path walks the tree. `WorkspaceRegistry` (`validator.ts`) answers imports from manifests
  (CLI `--interfaces`) or from header `.pblang` files open in the workspace (`module a.b;` + `X` is
  `local:!a.b.X`).
- `src/api.ts` is the embeddable API (package export `process-bigraph-lang`): a `Pblang` session with `addManifest`,
  `addHeader`, `check`, `compile`, `decompile`, `graph`, all from strings and plain values, no file system; the CLI
  shares its diagnostic mapping and spec detection. `process-bigraph-lang/worker` is the language server for a
  browser editor; `/monarch`, `/textmate`, `/language-configuration` are the grammars. `npm run bundle` (Vite) empties
  `dist/`, which also removes `dist/cli-native`.
- The generated AST's names (`Store`, `Node`, `Path`, `Composite`, ...) coincide with the object model's, so every
  consumer imports it as a namespace: `import * as ast from "../generated/ast.js"`, then `ast.Store`, `ast.isPlainEdge`.
- **Adding a check:** add it in `check.ts`, add a case to `dsl/test/v2/check.test.ts`; the Python tests under
  `tests/v2/` run the same expectations through the CLI.

### The Python side (`process_bigraph_lang/v2/`)

- `api.py`: `compile_text` / `compile_file` (check, then compile; `CompileError` on errors; `strict`, `force`)
  and `decompile` (text + assets). Documents cross the CLI as `json_codec` JSON with `__tuple__` tags
  (`dumps` / `loads`).
- `interfaces.py`: `describe_module` → `InterfaceDecl`s with types in bigraph-schema's own form → manifest JSON
  (`pblang-manifest/0`); `render_interfaces` via the CLI. `sbml.py`: `describe_sbml` → JSON (`pblang-model/0`);
  `print_model_header` via the CLI. `check.py`: `check_file` / `check_text`. `normalize.py`: `equivalent`,
  `diff_documents`, `deep_equal` (+ `types.py`, its parser). `langium.py`: `langium_cli`, `run_cli`.
- Keep `process_bigraph` out of the shipped package (tests only); `bigraph_schema` and `numpy` are main deps.

## Tests and fixtures

- `dsl/test/v2/`: `check.test.ts`, `hover-completion.test.ts`, `snapshots.test.ts` (every snapshot parses),
  `model.test.ts` (reader, printer, types, paths), `roundtrip.test.ts` (every corpus document prints to its
  snapshot byte for byte; every snapshot is a fixpoint; the v1 expected documents write back exactly),
  `api.test.ts` (the embeddable API against the snapshots and the CLI).
- `tests/v2/`: round trips, equivalence and realized equivalence through the CLI; `describe`; the SBML header;
  the checker's cases. Test processes live in `tests/fixtures/test_registry/` (`local:!` addresses import them
  directly; `pg.allocate_core()`; the spatio-flux custom types register with `register_types`).
- `tests/fixtures/data/v2/`: `corpus/` (yaml, hybrid JSON generated in viva-pde-particle's pixi env,
  `template_sites.json`, `v1/*.json` the former v1 compiler's expected documents, `make_v1_fixtures.py`),
  `snapshots/` (regenerate with `PBLANG_UPDATE_SNAPSHOTS=1 pytest tests/v2`; run the corpus, interfaces and
  sbml tests first), `interfaces/` (manifests + headers), `models/` (SBML). `corpus/` and `snapshots/` are
  excluded from prettier and checked out with LF line endings (`.gitattributes`): the tests compare bytes.
- The toy add-floats composite writes `output.txt` into the working directory when run.

## process-bigraph 1.x traps (each fails silently)

- The document keys are `schema` and `state`. A `composition` key is ignored.
- An edge's `address` must be a plain value in its **state** node. An address given only in `schema` (or wrapped in
  `quote`) leaves the edge as a no-op base `Edge`.
- There is no `_config`: config is a value, and its types come from the class's `config_schema`. A missing config
  key is filled from the type's default (the checker reports `T121`).
- Unknown type names such as `int` or `any` are accepted as raw strings. Use `integer`, `boolean`, `node`, ….
- Steps don't run on construction unless `run_steps_on_init` is set.
- Open stores get no `schema` entry: 1.x realizes a store that has a schema entry from that entry and silently
  ignores its unfilled site (process-bigraph#213). Fill templates with `template_document`.
- Address and model sites can only be filled with names registered via `core.register_link`: the face check can't
  see `local:!` classes (bigraph-schema#188).
- A wire to `..` from a root edge is clamped at the root (`W110`, a warning).
