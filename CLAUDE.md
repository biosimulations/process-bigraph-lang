# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A statically typed domain-specific language (`.pblang`) for describing process bigraphs, shipped as:

- a **Langium** language server / VS Code extension / CLI (TypeScript, in `dsl/`) that parses and type-checks it, and
- a **Python package** (`process_bigraph_lang/`) that compiles it into a process-bigraph composite document
  (`{"schema": ..., "state": ...}`) for **process-bigraph ≥ 1.8 / bigraph-schema ≥ 1.6**.

## Commands

### Python (repo root, Poetry)

```bash
make install                 # poetry install + pre-commit hooks
make check                   # poetry check --lock, pre-commit on ALL tracked files (ruff, ruff-format, prettier), mypy, deptry
make test                    # pytest with coverage
poetry run pytest tests/compiler/generator/test_dsl_compiler.py::test_type_schemas   # single test
poetry run mypy              # strict typing over process_bigraph_lang/ and tests/ (antlr/ excluded)
make docs                    # mkdocs serve
```

Ruff line length is 120. `make check` is what CI's `quality` job runs. It only sees tracked files, so `git add`
new files before running it.

### DSL (`dsl/`, npm)

```bash
npm install
npm run langium:generate     # regenerate src/language/generated/ and syntaxes/ from the .langium grammar
npm run build                # tsc + esbuild -> out/
npm run lint
npm test                     # vitest run
npx vitest run test/validating/sites.test.ts   # single test file
npx tsc --noEmit -p tsconfig.json              # type-check src/ AND test/ (vitest does not type-check)
npm run build:native         # also builds dist/cli-native with `deno compile` (Deno required, ~10 s)
./bin/cli.js generate <file.pblang> -d <outdir>     # dump AST as JSON (exits 1 on validation errors)
./bin/cli.js parseAndValidate <file.pblang>
```

Run `langium:generate` after every grammar change; `src/language/generated/` is gitignored.

### ANTLR (`antlr/`, legacy)

`antlr/pblang.g4` is the **old** grammar and is not used for parsing. Only `tests/dsl/test_antlr_grammar.py` still
uses it, against the old-syntax fixture `tests/fixtures/data/antlr/abc.pblang`. `make -C antlr` regenerates it
(requires Java).

## The language (`dsl/src/language/process-bigraph-language.langium`)

`Model` is a flat list of elements:

- **Types:** `type float builtin`, `type Conc = float` (alias), `struct Point { x: float; y: float = 0.0; }`,
  plus `array<T>`, `map<K, V>` and named tuples `(a: float, b: string)`.
- **Values and state:**
  - `let x: T = value;`, or the destructuring form `let (a: A, b: B): T = …;`
  - `store s: T;` with `init s = value;`
- **Steps and processes:**
  - `remote step|process Name at "py.path.Class" { config (…) inputs (…) outputs (…) }` declares a type.
  - An instance is a _callable literal_: `let g: Name = Name(cfg = 1.0);`.
  - Without `at`, the remote is an **interface**, whose instances leave their implementation open.
- **Wiring:** `connect g inputs (port = a.b) outputs (port = c);`. Both clauses are optional, and the instance may be a
  member chain (`connect group.g …`).
- **References:** references in values and bindings are `MemberCall` chains (`a.b.c`) over
  `type NamedElement = VarDef | Field | StoreDecl | ParamDecl`.
- **Open values (template sites):** `?` (required) and `?(default)` (optional). They're only allowed where they
  stand for a whole store or a whole config argument.
- **Literals:**
  - Map keys must be literals, so `{ name = … }` is always a struct and `{ "name" = … }` a map; `{}` is either.
  - `INT` / `FLOAT` accept a leading `-`, and `FLOAT` needs a `.` (`1.`, `.5`, `2.5e-3`).
- **Units:** `unit name: ["symbol"]`.

### Type checking and scoping (`dsl/src/language/validation/`)

- `scope-provider.ts`:
  - Scopes each segment of a member chain to the struct fields or tuple elements of the previous segment's type
    (aliases unwrapped).
  - `inferType(memberCall)` is also what the type checker uses to type references.
- `type-resolver.ts`:
  - `resolveType` turns a `TypeRef` into a `ResolvedType`.
  - `validateValueAgainstType` checks a value against it recursively.
  - `isTypeAssignable` allows `int` → `float` and is nominal for structs and remote types.
- `type-validator.ts`: per-node checks. They're registered in `validator.ts` and wired into DI in
  `process-bigraph-language-module.ts`.
- **Adding a check:** add a method to `TypeValidator`, register the node type in `validator.ts`, and add a vitest case
  under `dsl/test/validating/`.

Other files: `sbml.ts` + `commands.ts` implement the "Generate SBML Stub" command, which writes a data-only `.pblang`
stub. Entry points: `main.ts` (LSP), `main-browser.ts` (Monaco demo, `npm run dev`), `../extension/main.ts`,
`../cli/main.ts`.

## Python package

### Parsing: shells out to the Langium CLI

- `dsl/langium_pblang.py` runs `process_bigraph_lang/bin/cli-native generate`. It renames
  `$type`/`$ref`/`$refText` to `obj_type`/`ref`/`ref_text` and validates the JSON into `dsl/ast_model.py`.
- `generate` refuses invalid models, so the compiler only ever sees type-checked input.
- **`cli-native` is gitignored and must match the grammar.** After any grammar or TS change, rebuild it with
  `python build.py` (also the Poetry build script, which is how CI builds it), or quickly with
  `cd dsl && npm run build:native && cp dist/cli-native ../process_bigraph_lang/bin/`.
- **`ast_model.py` mirrors the grammar by hand.** Change it with any grammar change.
  - A struct field is `Field_`, to avoid shadowing `pydantic.Field`.
  - JSON writes `1.0` as `1`, and `FloatLiteral.value: float` coerces it back.
  - `StringLiteral.value` has its quotes already stripped.
- **`bind_ast.py` resolves each reference by the Langium document path** in `ref` (e.g. `#/elements@1/fields@0`),
  not by name.

### Compiler: `compile_ast` → `PBModel` → `assemble_pb`

`compiler/generator.py` (`compile_ast`):

- **Stores:**
  - Every `store` and every `let` with a non-remote type becomes a store, so constants used only as config
    become stores too.
  - A struct-typed store is split into one store per field, nested under the struct's name. Field defaults
    become `_default` in `schema`.
- **Edges:**
  - A value of remote type becomes a step or process at its path. Edges nested in a struct form groups.
  - Each `connect` binding becomes a wire, relative to the edge's container (`compute_relative_path`).
  - The compiler errors on a port bound twice or a binding to a non-store.
- **Constant values:**
  - References in values are inlined.
  - Ints widen to floats for float types.
  - Tuple values follow the declared element order.
- **Types:**
  - `int` becomes `integer` and `bool` becomes `boolean`. Other builtin names pass through, and aliases are
    replaced by their target.
  - `array<T>` becomes `list[T]`, `map<string, V>` becomes `map[V]` (other key types are an error), and tuples become
    `tuple[...]`. The dict form is used when an inner type is a struct.
  - A dict-form tuple uses `_values`: 1.x silently turns `_0`/`_1` into an empty tuple.
- **Template sites:**
  - `?` becomes `{"_type": "site", "_sort": <type>, "_default"?: v}`.
  - An interface instance's `address` becomes a site sorted by its face (`link` with `_inputs`/`_outputs`).
  - The result is a template. Fill it before running, with
    `template_document(core, core.access(doc["state"]), bindings)` from `process_bigraph.templates`.

`compiler/converter.py` (`assemble_pb`) emits the 1.x format:

- `schema` holds store types only.
- Each edge is a node in `state` with `_type`, a plain `address`, `config` (values), `_inputs`/`_outputs`, wires and
  `interval`. A bare Python path becomes `local:!path`; an address with a protocol is kept.
- **Open stores get no `schema` entry.** 1.x realizes a store that has a schema entry from that entry and silently
  ignores its unfilled site (process-bigraph#213).

### process-bigraph 1.x traps (each fails silently)

- The document keys are `schema` and `state`. A `composition` key is ignored.
- An edge's `address` must be a plain value in its **state** node. An address given only in `schema` (or wrapped in
  `quote`) leaves the edge as a no-op base `Edge`.
- There is no `_config`: config is a value, and its types come from the class's `config_schema`.
- Unknown type names such as `int` or `any` are accepted as raw strings. Use `integer`, `boolean`, `node`, ….
- Steps don't run on construction unless `run_steps_on_init` is set.
- Address and model sites can only be filled with names registered via `core.register_link`: the face check can't
  see `local:!` classes (bigraph-schema#188). A `Composite` given an open address crashes rather than reporting it
  (process-bigraph#213), so fill with `template_document`.

## Tests

- `tests/compiler/generator/`:
  - Most files pair a hand-written expected 1.x document (run with `pg.Composite`) with a `PBModel` built by hand
    and checked through `assemble_pb`.
  - `test_dsl_compiler.py` goes from DSL source to a compiled document or template, and runs it on process-bigraph.
- Test processes live in `tests/fixtures/test_registry/`:
  - Cores come from `pg.allocate_core()`. `local:!` addresses import classes directly, so no registration is needed.
  - Emitters use `local:RAMEmitter` with `node` types.
  - The spatio-flux custom types (`positive_float`, `positive_array`) are 1.x dataclass schema types with an
    `apply` dispatch.
- `test_spatio_flux_V.py` is skipped: its per-particle process template is a 0.0.x idiom that 1.x replaces with
  template sites.
- The toy add-floats tests write `output.txt` into the working directory.
