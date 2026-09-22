# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A domain-specific language (`.pblang`) for describing process bigraphs, shipped as:
- a **Langium** language server / VS Code extension / CLI (TypeScript, in `dsl/`), and
- a **Python package** (`process_bigraph_lang/`) that parses `.pblang` files and compiles them into a
  `process-bigraph` composite document (`{"composition": ..., "state": ...}`).

## Commands

### Python (repo root, Poetry)
```bash
make install                 # poetry install + pre-commit hooks
make check                   # poetry check --lock, pre-commit (ruff, ruff-format, prettier), mypy, deptry
make test                    # pytest with coverage
poetry run pytest tests/compiler/generator/test_toy_add_floats.py::test_name   # single test
poetry run mypy              # strict typing over process_bigraph_lang/ and tests/ (antlr/ excluded)
make docs                    # mkdocs serve
```
Ruff line length is 120.

### DSL (`dsl/`, npm)
```bash
npm install
npm run langium:generate     # regenerate src/language/generated/ and syntaxes/ from the .langium grammar
npm run build                # tsc + esbuild -> out/
npm run lint
npm test                     # vitest run
npx vitest run test/validating/validating.test.ts   # single test file
npm run build:native         # also builds dist/cli-native with `deno compile` (Deno required)
./bin/cli.js generate <file.pblang> -d <outdir>     # dump AST as JSON
./bin/cli.js parseAndValidate <file.pblang>
```
Run `langium:generate` after every grammar change; `src/language/generated/` is gitignored.

### ANTLR (`antlr/`, legacy/secondary)
`make -C antlr` regenerates the ANTLR parsers from `antlr/pblang.g4` into `process_bigraph_lang/antlr/` (Python)
and `cpp/src/antlr/` (C++). Requires Java.

## Architecture

### Python parses `.pblang` by shelling out to the Langium CLI
The Python package has no parser of its own on the main path. `process_bigraph_lang/dsl/langium_pblang.py`
runs the native binary `process_bigraph_lang/bin/cli-native` (`generate` subcommand), reads the JSON-serialized
Langium AST, renames `$type`/`$ref`/`$refText` to `obj_type`/`ref`/`ref_text`, and loads it into the
Pydantic models in `dsl/ast_model.py`. `dsl/bind_ast.py` then resolves the cross-references by building a symbol table.

Consequences:
- **Python tests need a current `cli-native` in `process_bigraph_lang/bin/`.** After changing the grammar or TS
  code, rebuild it: `python build.py` (runs `npm install`, `langium:generate`, `build:native`, and copies
  `dsl/dist/cli-native*` into `process_bigraph_lang/bin/`). `build.py` is also the Poetry build script.
- The Pydantic `ast_model.py` mirrors the Langium grammar's AST shape. Changing the grammar in
  `dsl/src/language/process-bigraph-language.langium` requires updating `ast_model.py`, `bind_ast.py`, and the compiler.
  Top-level grammar elements (`Type`, `Definition`, `Unit`, `SbmlModel`, `StepDef`, `ProcDef`, `StoreNode`,
  `Parameter`) correspond one-to-one with classes in `ast_model.py`.

### Compilation pipeline (Python)
`langium_parse_pblang_file` → `ASTModel` → `compiler/generator.py::compile_ast` → `PBModel`
(`compiler/pb_model.py`: store/step/process schemas and states with paths) → `compiler/converter.py::assemble_pb`
→ process-bigraph document dict. Step/process addresses are emitted as `local:!<python.path>` quotes.
Tests in `tests/compiler/generator/` assert on each stage and some run the result with `process_bigraph`;
test process/step implementations live in `tests/fixtures/test_registry/`.

### Langium language (`dsl/src/language/`)
- `process-bigraph-language.langium`: the grammar.
- `process-bigraph-language-module.ts`: DI module that wires Langium defaults, the generated module, and custom services.
- `process-bigraph-language-validator.ts`: custom validation checks (`registerValidationChecks` maps AST node types
  to validator methods; currently only unit-symbol checking).
- `sbml.ts` + `commands.ts`: the "Generate SBML Stub" command (SBML model → `.pblang` stub).
- Entry points: `main.ts` (LSP over node), `main-browser.ts` (web worker for the Monaco demo, `npm run dev`),
  `../extension/main.ts` (VS Code client), `../cli/main.ts` (CLI).
