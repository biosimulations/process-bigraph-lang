import * as fs from "node:fs";
import * as path from "node:path";
import { describe, expect, test } from "vitest";
import { Pblang } from "../../src/api.js";

// The SED-ML translations (process_bigraph_lang/v2/sedml_translate.py) are generated text, not the printer's
// fixpoints, so they are not in snapshots/: here each must parse and check. A template reports only its open
// solver site; an instance is clean against the pbsim-common steps of registry_env.
const fixtures = path.resolve(__dirname, "../../../tests/fixtures/data/v2");
const dir = path.join(fixtures, "sedml", "snapshots");
const manifest = fs.readFileSync(
  path.join(fixtures, "interfaces", "registry_env_pbsim.manifest.json"),
  "utf-8",
);

describe("SED-ML translations", () => {
  for (const file of fs.readdirSync(dir).filter((f) => f.endsWith(".pblang"))) {
    test(file, async () => {
      const text = fs.readFileSync(path.join(dir, file), "utf-8");
      const result = await new Pblang().addManifest(manifest).check(text);
      const template = file.split(".").length === 3; // <model>.<task>.pblang; instances add the solver
      expect(result.diagnostics.map((d) => d.code)).toEqual(
        template ? ["I300"] : [],
      );
    });
  }
});
