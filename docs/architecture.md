# Architecture

`process-bigraph-lang` defines a domain-specific language (files ending in `.pblang`) for describing
[process bigraph](https://github.com/vivarium-collective/process-bigraph) models. The language is statically
typed: values, stores and the wiring of steps and processes are type-checked as you edit. It compiles those
descriptions into composite documents, or into templates with open sites, that `process-bigraph` (≥ 1.8, with
`bigraph-schema` ≥ 1.6) can run.

The repository holds two cooperating projects:

| Component      | Location                                        | Language                         | Purpose                                                                                                           |
| -------------- | ----------------------------------------------- | -------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| Langium DSL    | `dsl/`                                          | TypeScript                       | Defines the grammar. Provides the parser, language server (LSP), VS Code extension, browser editor demo, and CLI. |
| Python package | `process_bigraph_lang/`                         | Python                           | Parses `.pblang` files by calling the DSL CLI, then compiles the result into a process-bigraph document.          |
| ANTLR grammar  | `antlr/`, `process_bigraph_lang/antlr/`, `cpp/` | ANTLR / generated Python and C++ | A second grammar that is not used for parsing today (see [ANTLR grammar](#antlr-grammar-legacy)).                 |

The Langium grammar is the single source of truth for the language. The Python package does not parse
`.pblang` itself. It runs a native build of the DSL CLI and reads the abstract syntax tree (AST) that the CLI
writes out as JSON.

## End-to-end data flow

```text
                  dsl/ (TypeScript, Langium)                         process_bigraph_lang/ (Python)
 ┌─────────────────────────────────────────────────┐   ┌────────────────────────────────────────────────────────────┐
 │                                                 │   │                                                            │
 │ .pblang ──► Langium parser ──► AST ──► JSON     │   │  dsl/langium_pblang.py                                     │
 │            (grammar +          (linked,         │   │    runs bin/cli-native generate ──► AST JSON               │
 │             validation)        validated)       │   │             │                                              │
 │                                                 │   │             ▼                                              │
 │ bundled with deno compile ──► dist/cli-native ──┼──►│  dsl/ast_model.py      ASTModel (Pydantic)                 │
 │                    (copied by build.py)         │   │  dsl/bind_ast.py       resolve refs by document path       │
 │                                                 │   │             │                                              │
 └─────────────────────────────────────────────────┘   │             ▼                                              │
                                                       │  compiler/generator.py compile_ast ──► PBModel             │
                                                       │  compiler/pb_model.py  (store/step/process schema + state) │
                                                       │             │                                              │
                                                       │             ▼                                              │
                                                       │  compiler/converter.py assemble_pb                         │
                                                       │             ──► {"schema": {...}, "state": {...}}          │
                                                       └────────────────────────────────────────────────────────────┘
                                                                     │
                                                                     ▼
                                          (templates only) process_bigraph.templates.template_document(...)
                                                                     │
                                                                     ▼
                                                        process_bigraph.Composite(document, core=...)
```

## The DSL project (`dsl/`)

`dsl/` is a [Langium](https://langium.org/) project. Langium generates a parser, AST types, and language
server infrastructure from a grammar file. The project then reuses those same services in several entry points.

### Grammar and language services (`dsl/src/language/`)

- **`process-bigraph-language.langium`** is the grammar. A model is a flat list of:
  - **type declarations:** built-in types (`type float builtin`), aliases (`type Conc = float`) and structs. Types
    compose with `array<T>`, `map<K, V>` and named tuples `(a: float, b: string)`.
  - **values and stores:** `let x: T = value;` and `store s: T;` with `init s = value;`
  - **remote types:** `remote step|process Name at "py.path.Class" { config (…) inputs (…) outputs (…) }`.
    - An instance is written as a _callable literal_: `let g: Name = Name(rate = 0.5);`.
    - A remote declared **without `at`** is an _interface_: its instances leave their implementation open.
  - **wiring:** `connect g inputs (port = a.b) outputs (port = c);`, where values are referenced through dotted
    member chains.
  - **open values:** `?` (required) or `?(default)` (optional), which become template sites.
  - **units:** `unit name: ["symbol"]`.
- **`generated/`** holds the AST types, grammar, and module produced by `npm run langium:generate`. It is
  gitignored and must be regenerated after every grammar change.
- **`process-bigraph-language-module.ts`** is the dependency-injection module. It combines Langium's defaults,
  the generated module, and this project's custom services. `createProcessBigraphLanguageServices()` is the
  shared factory that every entry point calls.
- **`validation/`** holds the language's own checks, beyond parsing and linking:
  - `scope-provider.ts` resolves each segment of a member chain (`a.b.c`) against the struct fields or tuple
    elements of the previous segment's type.
  - `type-resolver.ts` resolves type references, checks values against types, and defines assignability
    (`int` → `float`; structs and remote types match by name).
  - `type-validator.ts` holds the per-node checks: `let`/`init` values, callable literals against a remote's
    config, `connect` bindings against its ports, and where open values may appear. `validator.ts` registers them.
  - `unit-validator.ts` checks unit symbols with mathjs.
- **`sbml.ts` and `commands.ts`** implement the _Generate SBML Stub_ command. It parses an SBML file and writes a
  `.pblang` stub that declares the model file, its parameters and its species (as structs whose fields default to
  their values).

### Entry points

All of these entry points build on the same language services:

| Entry point                  | File                            | Used by                                                                                                            |
| ---------------------------- | ------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| Language server (Node)       | `src/language/main.ts`          | The VS Code extension                                                                                              |
| Language server (web worker) | `src/language/main-browser.ts`  | The Monaco-based browser demo (`npm run dev`, `static/`, `setup*.ts`)                                              |
| VS Code extension client     | `src/extension/main.ts`         | VS Code. Starts the language server and adds the SBML stub command to context menus.                               |
| CLI                          | `src/cli/main.ts`, `bin/cli.js` | Humans and the Python package. `generate` writes the linked AST as JSON. `parseAndValidate` reports syntax errors. |

`npm run build` compiles TypeScript and bundles with esbuild into `out/`. `npm run build:native` also runs
`deno compile` to produce a standalone `dist/cli-native` executable that does not need Node at runtime.

## The Python package (`process_bigraph_lang/`)

### Parsing: `process_bigraph_lang/dsl/`

- **`langium_pblang.py`** is the bridge to the DSL. `langium_parse_pblang_file()` and
  `langium_parse_pblang_str()` run `bin/cli-native generate`. They rename Langium's `$type`, `$ref`, and
  `$refText` keys to `obj_type`, `ref`, and `ref_text`, then validate the JSON into an `ASTModel`.
  `generate` refuses a model with validation errors, so the compiler only sees type-checked input.
- **`ast_model.py`** contains Pydantic classes that mirror the Langium AST, one per grammar rule (`VarDef`,
  `StoreDecl`, `RemoteCallableType`, `ConnectStatement`, the literals, `SiteLiteral`, …). It must be kept in sync
  with the grammar by hand.
- **`bind_ast.py`** resolves every `Reference` to the object it points at, so the compiler can follow links
  directly. Langium records each target's document path (e.g. `#/elements@1/fields@0`), so binding follows that
  path from the model root instead of looking names up.

### Compiling: `process_bigraph_lang/compiler/`

- **`generator.py`** has `compile_ast()`, which emits entries into a `PBModel`:
  - **stores:** every `store` and every `let` whose type isn't a remote type becomes a store, with its `init` or
    `let` value as state. A struct-typed store is split into one store per field.
  - **steps and processes:** each value of a remote type becomes one, at its path. Edges nested inside a struct
    form a group. Config comes from the callable literal's arguments.
  - **wires:** each `connect` binding becomes a wire from a port to a store path, relative to the edge's container.
  - **constant values:** references in values are replaced by the referenced value. DSL types map to
    bigraph-schema types (`int` → `integer`, `array<T>` → `list[T]`, `map<string, V>` → `map[V]`, …).
  - **template sites:** open values and the addresses of interface instances become sites.
- **`pb_model.py`** defines the dataclasses for that intermediate model. Each entity has a `key` and a `path`.
  Schema is kept separate from state.
- **`converter.py`** has `assemble_pb()`. It turns a `PBModel` into the process-bigraph 1.x document
  `{"schema": ..., "state": ...}`:
  - `schema` holds store types only.
  - Each step or process is a node in `state` with `_type`, a plain `address` (`local:!<python.class.path>`, or
    as written when it names a protocol), `config`, port types (`_inputs`/`_outputs`), wires and `interval`.
  - process-bigraph 1.x ignores an address placed in `schema`, so it has to be in the state node.

### Templates

A model containing open values (`?`) or instances of interfaces compiles to a **template**: a document with open
_sites_ that `Composite` refuses to run until they are filled.

| DSL                                               | Site in the document                                                                 | Filled at       |
| ------------------------------------------------- | ------------------------------------------------------------------------------------ | --------------- |
| `let rate: float = ?;`                            | `"rate": {"_type": "site", "_sort": "float"}`                                        | `rate`          |
| `let dt: float = ?(0.1);`                         | same, with `"_default": 0.1` (optional)                                              | `dt`            |
| `Grow(rate = ?)`                                  | a site inside the edge's `config`                                                    | `g/config/rate` |
| an instance of `remote process M { … }` (no `at`) | the edge's `address` is a site sorted by its face (`link` with `_inputs`/`_outputs`) | `m/address`     |

Fill a template with process-bigraph:
`template_document(core, core.access(doc["state"]), {"rate": 0.5, "m/address": "local:M"})` from
`process_bigraph.templates`, then build a `Composite` from the result. Open stores get no `schema` entry: process-bigraph
1.8 would otherwise realize the store from its schema entry and silently ignore the unfilled site
([process-bigraph#213](https://github.com/vivarium-collective/process-bigraph/issues/213)). Address sites currently
have to be filled with names registered via `core.register_link`
([bigraph-schema#188](https://github.com/vivarium-collective/bigraph-schema/issues/188)).

### Native binary: `process_bigraph_lang/bin/`

This directory holds the `cli-native` executable that `langium_pblang.py` runs. The binary is not built by the
Python tooling on its own. `build.py` (also Poetry's build script) runs `npm install`,
`npm run langium:generate`, and `npm run build:native` in `dsl/`. It then copies `dsl/dist/cli-native*` here.
The wheel includes the binary, so installed users do not need Node or Deno.

**Any change to the grammar or TypeScript code only reaches Python after `python build.py` is run again.**

## ANTLR grammar (legacy)

`antlr/pblang.g4` is an older ANTLR version of the language, in the old syntax. `make -C antlr` generates Python parsers into
`process_bigraph_lang/antlr/` and C++ parsers into `cpp/src/antlr/`. The Python ANTLR front end
(`dsl/antlr_pblang.py`, `dsl/antlr_ast_builder.py`) is commented out, and `cpp/src/main.cpp` is a placeholder.
Only `tests/dsl/test_antlr_grammar.py` still exercises the generated parser, against the old-syntax fixture
`tests/fixtures/data/antlr/abc.pblang`. Language changes belong in the
Langium grammar.

## Tests

| Location                    | Runner              | What it covers                                                                                                                                                                                                                                 |
| --------------------------- | ------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `dsl/test/`                 | vitest (`npm test`) | Parsing, linking and member-access scoping, type checking (values, callable literals, `connect`, open values), and SBML stubs, run in memory                                                                                                   |
| `tests/dsl/`                | pytest              | Langium parsing and validation through `cli-native`, plus the legacy ANTLR grammar                                                                                                                                                             |
| `tests/compiler/generator/` | pytest              | Each compiler stage (`ASTModel`, `PBModel`, assembled document). Many tests then build a `process_bigraph.Composite` from the output and run it. `test_dsl_compiler.py` goes from DSL source to a document or template, fills it, and runs it. |
| `tests/fixtures/`           | —                   | Sample `.pblang` and SBML files (`data/`), and the Python step and process classes those models point at, written against the process-bigraph 1.x API (`test_registry/`)                                                                       |

The Python tests call `cli-native`, so they depend on an up-to-date binary in `process_bigraph_lang/bin/`.

## Other top-level files

- `pyproject.toml`, `poetry.lock`, `Makefile`, `tox.ini`, `.pre-commit-config.yaml`: Python packaging and
  quality tooling (ruff, mypy, deptry, pytest).
- `mkdocs.yml`, `docs/`: this documentation site. `modules.md` renders API docs for `ast_model` and `pb_model`.
- `.github/workflows/`: CI. It runs quality checks, tests plus mypy on Ubuntu, macOS, and Windows, and the
  docs build.
