# process-bigraph-lang (the `dsl/` package)

The `.pblang` language: a Langium language server, a VS Code extension, a CLI and an embeddable API.

## Use in another application

```shell
npm run pack                      # dist/process-bigraph-lang-<version>.tgz
npm install path/to/process-bigraph-lang-<version>.tgz   # in the other project
```

```ts
import { Pblang } from "process-bigraph-lang";

const pblang = new Pblang().addManifest(manifestJson); // headers (optional)
const { text, assets } = pblang.decompile(documentJson); // a {schema, state} document or a CompositeSpec -> .pblang
const { ok, diagnostics } = await pblang.check(text); // the checker's findings
const compiled = await pblang.compile(text, { assets }); // .pblang -> document JSON (CompileError on errors)
const graph = await pblang.graph({ text }); // nodes, stores, edges for a viewer
```

For an editor, start `process-bigraph-lang/worker` in a web worker and connect it with `monaco-languageclient`;
`process-bigraph-lang/monarch`, `/textmate` and `/language-configuration` are the grammars. `src/setup*.ts` and
`static/` show the wiring (`npm run dev`).

## CLI

## Build/Run as Node.js CLI

install Node 23, install dependencies, generate the language server, and build the CLI (the output is in `out/`)

```shell
nvm use 23
npm install
npm run langium:generate
npm run build
```

run the script as a shell script (needs Node 23 and node_modules)

```shell
./bin/cli.js
```

or, run the bundled script (needs Node 23 only)

```shell
node ./out/cli-bundled.mjs
```

### [Optional] build the native CLI

warning: first time takes 2.5 hours (until the source build of Node 23 is cached). The output is in `dist/`.

```shell
node ./out/npm run build:native
```

Run the CLI as a native executable

```shell
./dist/cli-native
```
