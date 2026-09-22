# Architecture

`process-bigraph-lang` defines a domain-specific language (files ending in `.pblang`) for describing
[process bigraph](https://github.com/vivarium-collective/process-bigraph) models. It compiles those
descriptions into composite documents that `process-bigraph` can run.

The repository holds two cooperating projects:

| Component | Location | Language | Purpose |
|---|---|---|---|
| Langium DSL | `dsl/` | TypeScript | Defines the grammar. Provides the parser, language server (LSP), VS Code extension, browser editor demo, and CLI. |
| Python package | `process_bigraph_lang/` | Python | Parses `.pblang` files by calling the DSL CLI, then compiles the result into a process-bigraph document. |
| ANTLR grammar | `antlr/`, `process_bigraph_lang/antlr/`, `cpp/` | ANTLR / generated Python and C++ | A second grammar that is not used for parsing today (see [ANTLR grammar](#antlr-grammar-legacy)). |

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
 │                    (copied by build.py)         │   │  dsl/bind_ast.py       resolve cross-references            │
 │                                                 │   │             │                                              │
 └─────────────────────────────────────────────────┘   │             ▼                                              │
                                                       │  compiler/generator.py compile_ast ──► PBModel             │
                                                       │  compiler/pb_model.py  (store/step/process schema + state) │
                                                       │             │                                              │
                                                       │             ▼                                              │
                                                       │  compiler/converter.py assemble_pb                         │
                                                       │             ──► {"composition": {...}, "state": {...}}     │
                                                       └────────────────────────────────────────────────────────────┘
                                                                     │
                                                                     ▼
                                                        process_bigraph.Composite(config=...)
```

## The DSL project (`dsl/`)

`dsl/` is a [Langium](https://langium.org/) project. Langium generates a parser, AST types, and language
server infrastructure from a grammar file. The project then reuses those same services in several entry points.

### Grammar and language services (`dsl/src/language/`)

- **`process-bigraph-language.langium`** is the grammar. Top-level constructs are `type` declarations,
  `def` expressions, units, `sbml` model imports, `step` and `proc` definitions (bound to a Python class path),
  `param`s, and `store` nodes. A store holds either a typed value or an invocation of a step or process that is
  wired to other stores.
- **`generated/`** holds the AST types, grammar, and module produced by `npm run langium:generate`. It is
  gitignored and must be regenerated after every grammar change.
- **`process-bigraph-language-module.ts`** is the dependency-injection module. It combines Langium's defaults,
  the generated module, and this project's custom services. `createProcessBigraphLanguageServices()` is the
  shared factory that every entry point calls.
- **`process-bigraph-language-validator.ts`** holds custom validation checks, such as unit-symbol checks.
- **`sbml.ts` and `commands.ts`** implement the *Generate SBML Stub* command. It parses an SBML file and writes a
  `.pblang` stub that declares its species, compartments, parameters, and reactions.

### Entry points

All of these entry points build on the same language services:

| Entry point | File | Used by |
|---|---|---|
| Language server (Node) | `src/language/main.ts` | The VS Code extension |
| Language server (web worker) | `src/language/main-browser.ts` | The Monaco-based browser demo (`npm run dev`, `static/`, `setup*.ts`) |
| VS Code extension client | `src/extension/main.ts` | VS Code. Starts the language server and adds the SBML stub command to context menus. |
| CLI | `src/cli/main.ts`, `bin/cli.js` | Humans and the Python package. `generate` writes the linked AST as JSON. `parseAndValidate` reports syntax errors. |

`npm run build` compiles TypeScript and bundles with esbuild into `out/`. `npm run build:native` also runs
`deno compile` to produce a standalone `dist/cli-native` executable that does not need Node at runtime.

## The Python package (`process_bigraph_lang/`)

### Parsing: `process_bigraph_lang/dsl/`

- **`langium_pblang.py`** is the bridge to the DSL. `langium_parse_pblang_file()` and
  `langium_parse_pblang_str()` run `bin/cli-native generate`. They rename Langium's `$type`, `$ref`, and
  `$refText` keys to `obj_type`, `ref`, and `ref_text`, then validate the JSON into an `ASTModel`.
- **`ast_model.py`** contains Pydantic classes that mirror the Langium AST: `Type`, `StepDef`, `ProcDef`,
  `StoreNode`, `Parameter`, `Definition`, expressions, and so on. It must be kept in sync with the grammar by hand.
- **`bind_ast.py`** builds a symbol table of types, definitions, parameters, step and process definitions, and
  store paths. It then resolves every `Reference` in the model to the object it points at, so the compiler can
  follow links directly.

### Compiling: `process_bigraph_lang/compiler/`

- **`generator.py`** has `compile_ast()`. It walks the store tree and emits entries into a `PBModel`:
  - store schemas and states, with types, defaults, and map collections
  - step and process schemas, built from `StepDef` and `ProcDef` config, inputs, and outputs
  - step and process states, whose input and output wires are store paths computed relative to the
    invoking store
- **`pb_model.py`** defines the dataclasses for that intermediate model. Each entity has a `key` and a `path`.
  Schema is kept separate from state.
- **`converter.py`** has `assemble_pb()`. It turns a `PBModel` into the process-bigraph document
  `{"composition": ..., "state": ...}`. Each step or process address becomes a `local:!<python.class.path>` quote.

### Native binary: `process_bigraph_lang/bin/`

This directory holds the `cli-native` executable that `langium_pblang.py` runs. The binary is not built by the
Python tooling on its own. `build.py` (also Poetry's build script) runs `npm install`,
`npm run langium:generate`, and `npm run build:native` in `dsl/`. It then copies `dsl/dist/cli-native*` here.
The wheel includes the binary, so installed users do not need Node or Deno.

**Any change to the grammar or TypeScript code only reaches Python after `python build.py` is run again.**

## ANTLR grammar (legacy)

`antlr/pblang.g4` is an older ANTLR version of the language. `make -C antlr` generates Python parsers into
`process_bigraph_lang/antlr/` and C++ parsers into `cpp/src/antlr/`. The Python ANTLR front end
(`dsl/antlr_pblang.py`, `dsl/antlr_ast_builder.py`) is commented out, and `cpp/src/main.cpp` is a placeholder.
Only `tests/dsl/test_antlr_grammar.py` still exercises the generated parser. Language changes belong in the
Langium grammar.

## Tests

| Location | Runner | What it covers |
|---|---|---|
| `dsl/test/` | vitest (`npm test`) | Parsing, linking, validation, and SBML handling in the Langium services, run in memory |
| `tests/dsl/` | pytest | Langium parsing and validation through `cli-native`, plus the legacy ANTLR grammar |
| `tests/compiler/generator/` | pytest | Each compiler stage (`ASTModel`, `PBModel`, assembled document). Many tests then build a `process_bigraph.Composite` from the output and run it. |
| `tests/fixtures/` | — | Sample `.pblang` and SBML files (`data/`) and the Python step and process classes those models point at (`test_registry/`) |

The Python tests call `cli-native`, so they depend on an up-to-date binary in `process_bigraph_lang/bin/`.

## Other top-level files

- `pyproject.toml`, `poetry.lock`, `Makefile`, `tox.ini`, `.pre-commit-config.yaml`: Python packaging and
  quality tooling (ruff, mypy, deptry, pytest).
- `mkdocs.yml`, `docs/`: this documentation site. `modules.md` renders API docs for `ast_model` and `pb_model`.
- `.github/workflows/`: CI. It runs quality checks, tests plus mypy on Ubuntu, macOS, and Windows, and the
  docs build.
