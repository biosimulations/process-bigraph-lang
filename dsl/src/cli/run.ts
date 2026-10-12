// The entry esbuild bundles into dist/cli.mjs (one self-contained file), which `deno compile` turns into
// dist/cli-native without embedding node_modules. `bin/cli.js` is the same entry for a Node checkout.
import main from "./main.js";

main();
