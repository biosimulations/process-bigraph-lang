import { describe, expect, test } from "vitest";
import { EmptyFileSystem } from "langium";
import { parseHelper } from "langium/test";
import * as fs from "node:fs";
import * as path from "node:path";
import { createProcessBigraphLanguageServices } from "../../src/language/process-bigraph-language-module.js";
import * as ast from "../../src/language/generated/ast.js";

// The v2 snapshots the Python prototype prints and parses back; the Langium grammar must accept them all.
const snapshots = path.resolve(
  __dirname,
  "../../../tests/fixtures/data/v2/snapshots",
);
const files = fs.readdirSync(snapshots).filter((f) => f.endsWith(".pblang"));

const services = createProcessBigraphLanguageServices(EmptyFileSystem);
const parse = parseHelper<ast.Module>(services.Pblang);

describe("v2 snapshots parse with the Langium grammar", () => {
  test("there are snapshots", () => {
    expect(files.length).toBeGreaterThan(5);
  });
  for (const file of files) {
    test(file, async () => {
      const text = fs.readFileSync(path.join(snapshots, file), "utf-8");
      const document = await parse(text, { validation: true });
      const errors = [
        ...document.parseResult.lexerErrors.map((e) => `lexer: ${e.message}`),
        ...document.parseResult.parserErrors.map((e) => `parser: ${e.message}`),
        ...(document.diagnostics ?? [])
          .filter((d) => d.severity === 1)
          .map((d) => `${d.range.start.line + 1}: ${d.message}`),
      ];
      expect(errors).toEqual([]);
      expect(document.parseResult.value.$type).toBe("Module");
    });
  }
});

describe("v2 constructs", () => {
  test("an edge references an imported interface, a model site references a header", async () => {
    const document = await parse(
      `import pkg.mod.{Grow};
       model ODE { time @ "?T"; species { _: float @ "?U"; ... } }
       model Demo from "demo.xml" { time @ "s"; species { A: float @ "uM" = 1.0; } }
       composite {
         store m : ODE = Demo;
         process g : Grow every 0.5 { config { rate = 0.1, every = 2 } inputs { mass -> ../cell.mass[0] } }
       }`,
      { validation: true },
    );
    const errors = (document.diagnostics ?? [])
      .filter((d) => d.severity === 1)
      .map((d) => d.message);
    expect(document.parseResult.parserErrors).toEqual([]);
    expect(errors).toEqual([]);
  });
});
