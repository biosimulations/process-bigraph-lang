# process-bigraph-lang CLI

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
