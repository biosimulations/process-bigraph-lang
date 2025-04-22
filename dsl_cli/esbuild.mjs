//@ts-check
import * as esbuild from "esbuild";

import commonjsPlugin from '@chialab/esbuild-plugin-commonjs';

await esbuild.build({
  entryPoints: ["./bin/cli.mjs"], // Your CLI entry point
  outfile: "out/cli-bundled.mjs", // Output file
  bundle: true,
  target: "node23",
  format: "esm",
  // To prevent confusing node, we explicitly use the `.cjs` extension
  outExtension: {
    ".js": ".mjs",
  },
  loader: { ".ts": "ts" },
  external: [], // Exclude unnecessary dependencies if needed
  platform: "node",
  sourcemap: false,
  plugins: [commonjsPlugin()],
});
