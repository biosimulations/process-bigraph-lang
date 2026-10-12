# Architecture

`process-bigraph-lang` defines a domain-specific language (files ending in `.pblang`) for describing
[process bigraph](https://github.com/vivarium-collective/process-bigraph) composites. A `.pblang` file is a
tree-shaped, verifiable projection of the composite document that `process-bigraph` (≥ 1.8, with
`bigraph-schema` ≥ 1.6) runs: stores, nodes and edges with their wires, plus the static semantics that compile
away (imported or inline interface declarations, parameters, open sites, units, model headers). The design is
in [the v2 design](v2/design.md), its [background](v2/research.md), the
[registry and authoring design](v2/registry-and-authoring.md) and the [plan](v2/plan.md).

The repository holds two cooperating projects:

| Component      | Location                | Language   | Purpose                                                                                                                                     |
| -------------- | ----------------------- | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| Langium DSL    | `dsl/`                  | TypeScript | The grammar, the checker, the compiler and the decompiler; the language server, the VS Code extension, the browser editor demo and the CLI. |
| Python package | `process_bigraph_lang/` | Python     | Calls the CLI (compile, decompile, check); describes Python packages and SBML models as headers; compares documents.                        |

Everything the language does is TypeScript. The Python package has no model of a composite: it is the entry
to the CLI from Python plus the pieces that have to run in Python.

## End-to-end data flow

```text
                         dsl/ (TypeScript, Langium)                              process_bigraph_lang/ (Python)
 ┌──────────────────────────────────────────────────────────────────┐   ┌─────────────────────────────────────────┐
 │ .pblang ──► parser ──► AST ──► checker (check.ts) ──► diagnostics │   │ v2/api.py                               │
 │                         │                                        │   │   compile_text / compile_file           │
 │                         ▼ bind.ts                                │   │     runs cli-native check, then compile │
 │                       model (model.ts) ──► writer.ts ──► document│◄──┤   decompile                             │
 │                         ▲                               or spec  │   │     runs cli-native decompile           │
 │ document / spec ──► reader.ts ──┘                                │   │                                         │
 │                       model ──► printer.ts ──► .pblang + assets  │   │ v2/interfaces.py  describe_module       │
 │                                                                  │   │   (imports classes) ──► manifest JSON ──┼──► headers
 │ bundled with deno compile ──► dist/cli-native (copied by build.py)│   │ v2/sbml.py        describe_sbml ──► JSON┼──► model-header
 └──────────────────────────────────────────────────────────────────┘   │ v2/normalize.py   equivalent / diff     │
                                                                        └─────────────────────────────────────────┘
```

Documents cross the CLI boundary as JSON in `bigraph_schema.json_codec`'s encoding (numpy arrays tagged), with
tuples tagged as `{"__tuple__": true, "data": [...]}` by the Python side.

## The DSL project (`dsl/`)

`dsl/` is a [Langium](https://langium.org/) project. Langium generates a parser, AST types and language server
infrastructure from the grammar; the project adds its own services and reuses them in every entry point.

### Grammar and language services (`dsl/src/language/`)

- **`pblang.langium`** is the grammar (language id `pblang`, files `.pblang` and `.pbl`). A module is a flat list of
  statements:
  imports, params, meta and options blocks, interface declarations (headers), model declarations (headers and
  sorts), the composite tree (`store`, `node`, `process`/`step` edges with `config`, `inputs`, `outputs`,
  `ports`, nested `composite`s, `shared` processes) and `emit` declarations. See the design's section 2 for the
  syntax and section 3 for the mapping to the document.
- **`generated/`** holds the AST types, grammar and module produced by `npm run langium:generate`. It is
  gitignored and must be regenerated after every grammar change.
- **`process-bigraph-language-module.ts`** is the dependency-injection module;
  `createProcessBigraphLanguageServices()` is the factory every entry point calls.
- **`pblang-scope.ts`** exports every named node (interface and model declarations, imported names), so
  edges resolve interfaces and model sites resolve headers.
- **`v2/`** is the language:
  - `check.ts` is the static checker, registered as a Langium validation (`validator.ts`): unknown ports,
    config keys, wires to undeclared stores, wire type mismatches, paths above the root, intervals on steps,
    unknown components, dynamic ports, untyped stores; writer analysis (additive, overwrite, step arrays);
    emit paths; units with unit variables (`units.ts`, mathjs); model sites admitted against sorts. Codes follow
    the registry design's section 4.
  - `headers.ts` reads interface and model declarations from manifests and from the text; `types.ts` is the
    type expression language (bigraph-schema's string and dict forms, the DSL spelling, a canonical form).
  - `model.ts` is the object model of a composite, the pivot of compile and decompile: ints are `bigint`,
    floats `number`, dicts `Map`s in source order; numpy arrays, tuples, params, sidecar references and sites
    are tagged objects. `json.ts` is the lossless document codec; `yaml.ts` the CompositeSpec form.
  - `reader.ts` classifies a document (or CompositeSpec) into the model; `writer.ts` writes the model back;
    `printer.ts` prints canonical text with sidecar assets for large values, byte-identical to the Python
    printer it replaced (`format.ts` reproduces Python's float and `json.dumps` spellings); `bind.ts` binds the
    Langium AST to the model; `resolve.ts` is what the checker, hover and completion share (which header an
    edge is declared by, how a path walks the tree).
  - `hover.ts` and `completion.ts` are the editor services; `graph.ts` the wiring graph for viewers;
    `modelheader.ts` renders `describe-model`'s JSON.

### Entry points

| Entry point                  | File                            | Used by                                                                                                                                                                               |
| ---------------------------- | ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Language server (Node)       | `src/language/main.ts`          | The VS Code extension                                                                                                                                                                 |
| Language server (web worker) | `src/language/main-browser.ts`  | The Monaco-based browser demo (`npm run dev`, `static/`, `setup*.ts`)                                                                                                                 |
| VS Code extension client     | `src/extension/main.ts`         | VS Code. Starts the language server.                                                                                                                                                  |
| Embeddable API               | `src/api.ts`                    | Other applications (web apps, scripts, workers): a `Pblang` session that checks, compiles, decompiles and graphs from strings and plain values. See "Embedding" below.                |
| CLI                          | `src/cli/main.ts`, `bin/cli.js` | Humans and the Python package: `check [--json]`, `compile [--to document\|spec] [--strict] [--force]`, `decompile`, `headers`, `model-header`, `graph`, `generate` (the AST as JSON). |

`npm run build` compiles TypeScript (with declarations) and bundles with esbuild: the extension and the language
server into `out/`, the CLI into one self-contained file `dist/cli.mjs`. `npm run build:native` also runs
`deno compile --node-modules-dir=none` on that bundle to produce a standalone `dist/cli-native` executable (about 75 MB,
the Deno runtime plus the bundle) that does not need Node at runtime.

### Embedding in another application

`dsl/` is also the npm package `process-bigraph-lang`, staged on npm by every GitHub release at the release's version by
`.github/workflows/publish-npm.yml` through npm's trusted publishing (OIDC, no token) and approved by a maintainer
(see `dsl/README.md`, "Releasing"); `npm run pack` writes an unreleased build's tarball to `dist/`. Nothing in
`src/language/` or `src/api.ts` touches the file system, so the whole language runs in a browser. The package exports:

| Export                                        | What it is                                                                                                                                                                 |
| --------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `process-bigraph-lang`                        | `Pblang`: `addManifest`, `addHeader`, `check`, `compile` (`to: "document" \| "spec"`, `strict`, `force`, `assets`), `decompile` (text + sidecar assets by path), `graph`.  |
| `process-bigraph-lang/worker`                 | The language server as a web worker entry (`main-browser.ts`): diagnostics as you type, hover and completion for an editor such as Monaco through `monaco-languageclient`. |
| `process-bigraph-lang/monarch`                | The Monarch tokenizer (Monaco's "classic" highlighting).                                                                                                                   |
| `process-bigraph-lang/textmate`               | The TextMate grammar (`source.pblang`), for VS Code-style highlighting.                                                                                                    |
| `process-bigraph-lang/language-configuration` | Comments, brackets and auto-closing pairs.                                                                                                                                 |

A viewer decompiles a run's document on the main thread with a `Pblang` session, shows the text in an editor fed by
the worker, and draws `graph(...)`. An authoring tool adds the manifests of the environment the document will run in to both: the session
through `addManifest` or `setManifests`, the worker through the `pblang/setManifests` notification
(`SET_MANIFESTS_NOTIFICATION`, `{ manifests }`), after which it re-checks every open document. It then compiles the
text and submits the document. Manifests come from `describe_env.py` run inside that environment
([registry and authoring](v2/registry-and-authoring.md), section 1.7). `static/` and
`src/setup*.ts` are the reference wiring of Monaco to the worker (`npm run dev`).

## The Python package (`process_bigraph_lang/v2/`)

- **`api.py`** is the public API. `compile_text` / `compile_file` run `cli-native check` and then
  `cli-native compile`, returning a `{"schema", "state"}` document or a CompositeSpec mapping (`CompileError`
  on errors; `strict=True` makes warnings fatal; `force=True` compiles an existing document that relies on
  defaults the checker flags). `decompile` runs `cli-native decompile` and returns canonical `.pblang` text with
  its sidecar assets. There is no Python model of a composite and no way to a runnable document that skips the
  checker: a Python tool that builds composites targets the DSL text.
- **`interfaces.py`** generates interface declarations from a module's step/process classes (`describe_module`,
  the publish-time step that imports the classes) as the JSON interface manifest (`pbg-interfaces/1`, a format shared with other tools; JSON Schema in `docs/schemas/`) the CLI reads;
  `render_interfaces` has the CLI print the `.pblang` header file. **`sbml.py`** describes an SBML model as
  JSON (`pblang-model/0`); the CLI renders the model header.
- **`check.py`** wraps `cli-native check --json`; **`normalize.py`** defines document equivalence (`equivalent`,
  `diff_documents`), with `types.py` as its type parser; **`langium.py`** locates and runs the CLI
  (`cli-native`, or `node dsl/bin/cli.js` in a checkout).
- `python -m process_bigraph_lang.v2 compile | decompile | check | diff | describe | describe-model`.

### Native binary: `process_bigraph_lang/bin/`

This directory holds the `cli-native` executable the package runs. `build.py` (also Poetry's build script) runs
`npm install`, `npm run langium:generate` and `npm run build:native` in `dsl/`, then copies `dsl/dist/cli-native*`
here. The wheel includes the binary, so installed users do not need Node or Deno. The wheel is therefore
platform-specific: a release builds one per platform (Linux x86_64 and arm64, macOS arm64 and Intel, Windows),
re-tagged `py3-none-<platform>` since the Python is pure, and publishes them to PyPI by trusted publishing
(`.github/workflows/on-release-main.yml`).

**Any change to the grammar or TypeScript code only reaches Python after the binary is rebuilt**
(`python build.py`, or `cd dsl && npm run build:native && cp dist/cli-native ../process_bigraph_lang/bin/`).

## Tests

- `dsl/test/v2/`: the checker's compliance suite (`check.test.ts`), hover and completion, the grammar over
  every snapshot, the model's unit tests (`model.test.ts`) and the round trip (`roundtrip.test.ts`): every corpus
  document prints to its committed snapshot byte for byte, every snapshot is a fixpoint through parse → bind →
  print, the v1 expected documents write back exactly.
- `tests/v2/`: the same round trips, equivalence under the normalizer and realized equivalence under
  `process_bigraph.Composite`, all through the CLI; `describe` of the test registry; the SBML header.
- `tests/fixtures/data/v2/`: `corpus/` (see its README for provenance; `v1/*.json` are the expected documents of
  the former v1 compiler), `snapshots/` (the printed text, regenerated with `PBLANG_UPDATE_SNAPSHOTS=1 pytest
tests/v2`), `interfaces/` (manifests and headers, those of viva-pde-particle generated in its own
  environment), `models/` (SBML). `tests/fixtures/test_registry/` holds the processes the composites run.
