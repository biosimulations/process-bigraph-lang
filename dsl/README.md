# process-bigraph-lang (the `dsl/` package)

The `.pblang` language: a Langium language server, a VS Code extension, a CLI and an embeddable API.

## Use in another application

```shell
npm install process-bigraph-lang   # published from this directory on every GitHub release, same version as the wheel
```

For an unreleased build: `npm run pack` writes `dist/process-bigraph-lang-<version>.tgz`, which the other project
can `npm install` by path.

```ts
import { Pblang } from "process-bigraph-lang";

const pblang = new Pblang().addManifest(manifestJson); // headers (optional)
const { text, assets } = pblang.decompile(documentJson); // a {schema, state} document or a CompositeSpec -> .pblang
const { ok, diagnostics } = await pblang.check(text); // the checker's findings
const compiled = await pblang.compile(text, { assets }); // .pblang -> document JSON (CompileError on errors)
const graph = await pblang.graph({ text }); // nodes, stores, edges for a viewer
```

For an editor, start `process-bigraph-lang/worker` in a web worker and connect a language client to it. Give it the
manifests of the environment the text will run in with the `pblang/setManifests` notification; it re-checks every
open document, and sending it again (another environment) replaces them:

```ts
import { SET_MANIFESTS_NOTIFICATION } from "process-bigraph-lang";

connection.sendNotification(SET_MANIFESTS_NOTIFICATION, {
  manifests: [manifestJson],
});
pblang.setManifests([manifestJson]); // the main-thread session, for compile and graph
```

`process-bigraph-lang/monarch`, `/textmate` and `/language-configuration` are the grammars. `src/setup*.ts` and
`static/` show the wiring (`npm run dev`).

### Releasing

`.github/workflows/publish-npm.yml` stages the package on npm when a GitHub release is published, at the release's
tag as the version, by [trusted publishing](https://docs.npmjs.com/trusted-publishers) (OIDC): there is no npm
token. A maintainer then approves the staged version on npmjs.com (Staged Packages, with 2FA;
[staged publishing](https://docs.npmjs.com/staged-publishing)), and only then is it public. The package's Trusted
Publisher on npmjs.com is GitHub Actions, organization `biosimulations`, repository `process-bigraph-lang`, workflow
`publish-npm.yml`, no environment, allowed action `npm stage publish`; provenance is attached automatically. A
manual `workflow_dispatch` run packs without staging (`dry_run`), or stages the committed version when `dry_run` is
off.

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

or, run the bundled script (needs Node only, no `node_modules`)

```shell
node ./dist/cli.mjs
```

### [Optional] build the native CLI

`deno compile` (Deno 2 required, about 10 s) turns the bundle `dist/cli.mjs` into `dist/cli-native`, a standalone
executable of about 75 MB (the Deno runtime plus the 3 MB bundle; `--node-modules-dir=none` keeps `node_modules` out
of it).

```shell
npm run build:native
```

Run the CLI as a native executable

```shell
./dist/cli-native
```
