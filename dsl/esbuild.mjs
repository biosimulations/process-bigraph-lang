//@ts-check
import * as esbuild from "esbuild";
import * as fs from "node:fs/promises";

const watch = process.argv.includes("--watch");
const minify = process.argv.includes("--minify");

const success = watch ? "Watch build succeeded" : "Build succeeded";

function getTime() {
  const date = new Date();
  return `[${`${padZeroes(date.getHours())}:${padZeroes(
    date.getMinutes(),
  )}:${padZeroes(date.getSeconds())}`}] `;
}

function padZeroes(i) {
  return i.toString().padStart(2, "0");
}

const plugins = [
  {
    name: "watch-plugin",
    setup(build) {
      build.onEnd((result) => {
        if (result.errors.length === 0) {
          console.log(getTime() + success);
        }
      });
    },
  },
];

// The CLI as one self-contained ESM file for `deno compile`: with the npm packages inlined, Deno embeds nothing
// from node_modules (which otherwise made cli-native 250 MB larger). CommonJS dependencies may `require` Node
// builtins at runtime, which the banner's `require` serves.
const version = JSON.parse(await fs.readFile("package.json", "utf-8")).version;
const cli = await esbuild.context({
  entryPoints: ["src/cli/run.ts"],
  outfile: "dist/cli.mjs",
  bundle: true,
  format: "esm",
  platform: "node",
  target: "node22",
  loader: { ".ts": "ts" },
  define: { __PBLANG_VERSION__: JSON.stringify(version) },
  banner: {
    // Deno runs the bundle as a plain module, without the Node globals it gives code loaded from node_modules
    js: [
      'import { createRequire as __createRequire } from "node:module";',
      'import { Buffer as __Buffer } from "node:buffer";',
      'import __process from "node:process";',
      'import { setImmediate as __setImmediate, clearImmediate as __clearImmediate } from "node:timers";',
      "const require = __createRequire(import.meta.url);",
      "globalThis.Buffer ??= __Buffer;",
      "globalThis.process ??= __process;",
      "globalThis.global ??= globalThis;",
      "globalThis.setImmediate ??= __setImmediate;",
      "globalThis.clearImmediate ??= __clearImmediate;",
    ].join(" "),
  },
  sourcemap: false,
  minify,
  plugins,
});

const ctx = await esbuild.context({
  // Entry points for the vscode extension and the language server
  entryPoints: ["src/extension/main.ts", "src/language/main.ts"],
  outdir: "out",
  bundle: true,
  target: "ES2017",
  // VSCode's extension host is still using cjs, so we need to transform the code
  format: "cjs",
  // To prevent confusing node, we explicitly use the `.cjs` extension
  outExtension: {
    ".js": ".cjs",
  },
  loader: { ".ts": "ts" },
  external: ["vscode"],
  platform: "node",
  sourcemap: !minify,
  minify,
  plugins,
});

if (watch) {
  await ctx.watch();
  await cli.watch();
} else {
  await ctx.rebuild();
  await cli.rebuild();
  ctx.dispose();
  cli.dispose();
}
