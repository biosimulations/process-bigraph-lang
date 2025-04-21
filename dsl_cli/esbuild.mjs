//@ts-check
import * as esbuild from 'esbuild';
import path from "node:path";

await esbuild.build({
    entryPoints: ['./bin/cli.js'], // Your CLI entry point
    outfile: 'out/cli-bundled.mjs', // Output file
    bundle: true,
    target: 'node20',
    format: 'esm',
    // To prevent confusing node, we explicitly use the `.cjs` extension
    outExtension: {
        '.js': '.mjs'
    },
    loader: { '.ts': 'ts' },
    external: [], // Exclude unnecessary dependencies if needed
    platform: 'node',
    sourcemap: false,
    inject: [path.resolve('./shims/require-shim.js')],
});