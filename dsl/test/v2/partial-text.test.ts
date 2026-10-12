/**
 * An editor checks text as it is typed, so the checker sees every half-written statement. None may make it throw:
 * a crash inside a check only reaches the console, and that text's findings are lost.
 */
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import * as fs from "node:fs";
import * as path from "node:path";
import { Pblang } from "../../src/api.js";

const manifest = JSON.parse(
  fs.readFileSync(
    path.resolve(
      __dirname,
      "../../../tests/fixtures/data/v2/interfaces/test_registry.manifest.json",
    ),
    "utf-8",
  ),
);

const TEXT = `import tests.fixtures.test_registry.toy_library.{AddFloatsProcess};
param scale: float = 2.0;
composite demo {
  store a: float = 1.0;
  store b: float = \${scale};
  store sum: float = 0.0;
  process add : AddFloatsProcess every 1.0 {
    inputs { left_hand_addend -> a, right_hand_addend -> b }
    outputs { result -> sum }
  }
  step other at "local:!somewhere.Else" { inputs { x -> a } }
  composite cell every 1.0 {
    composite { store x: float = 1.0; }
  }
}
emit console { sum } with { };
`;

describe("half-typed text", () => {
  let errors: unknown[][] = [];
  beforeEach(() => {
    errors = [];
    vi.spyOn(console, "error").mockImplementation((...args) => {
      errors.push(args);
    });
  });
  afterEach(() => {
    vi.restoreAllMocks();
  });

  test("no prefix of a composite makes the checker throw", async () => {
    const pblang = new Pblang().setManifests([manifest]);
    for (let end = 1; end <= TEXT.length; end++) {
      await pblang.check(TEXT.slice(0, end));
      if (errors.length)
        throw new Error(
          `the checker threw on a prefix ending ${JSON.stringify(
            TEXT.slice(Math.max(0, end - 40), end),
          )}: ${String(errors[0]?.[1] ?? errors[0]?.[0])}`,
        );
    }
    expect((await pblang.check(TEXT)).ok).toBe(true);
  });
});
