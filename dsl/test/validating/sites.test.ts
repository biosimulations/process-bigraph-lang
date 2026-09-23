import { afterEach, beforeAll, describe, expect, test } from "vitest";
import { EmptyFileSystem, type LangiumDocument } from "langium";
import { clearDocuments, parseHelper } from "langium/test";
import { createProcessBigraphLanguageServices } from "../../src/language/process-bigraph-language-module.js";
import { Model } from "../../src/language/generated/ast.js";

let services: ReturnType<typeof createProcessBigraphLanguageServices>;
let document: LangiumDocument<Model> | undefined;

beforeAll(async () => {
  services = createProcessBigraphLanguageServices(EmptyFileSystem);
});

afterEach(async () => {
  document && clearDocuments(services.shared, [document]);
});

const preamble = `
  type float builtin
  type string builtin
  remote process Grow at "pkg.Grow" {
    config (rate: float)
    inputs (size: float)
    outputs (size: float)
  }
  remote process Model {
    config (label: string)
    inputs (x: float)
    outputs (y: float)
  }
  struct Point { x: float; y: float; }
`;

async function errors(text: string): Promise<string[]> {
  document = await parseHelper<Model>(services.ProcessBigraphLanguage)(
    `${preamble}\n${text}`,
    { validation: true },
  );
  expect(document.parseResult.parserErrors).toHaveLength(0);
  return (document.diagnostics ?? [])
    .filter((d) => d.severity === 1)
    .map((d) => d.message);
}

describe("open values (template sites)", () => {
  test("are allowed as whole stores and config arguments", async () => {
    expect(
      await errors(`
        let rate: float = ?;
        let dt: float = ?(0.1);
        let pair: (a: float, b: string) = ?;
        let xs: array<float> = ?([1.0, 2.0]);
        let whole: Point = ?;
        let partial: Point = { x = ?, y = ?(2.0) };
        store s: float;
        init s = ?;
        let grow: Grow = Grow(rate = ?(0.5));
        connect grow inputs (size = s) outputs (size = partial.x);
      `),
    ).toEqual([]);
  });

  test("check their default against the expected type", async () => {
    expect(await errors(`let rate: float = ?("fast");`)).toEqual([
      "Expected value of type 'float' or 'int'",
    ]);
  });

  test("are rejected inside arrays, maps and tuples", async () => {
    expect(
      await errors(`
        let xs: array<float> = [1.0, ?];
        let m: map<string, float> = { "a" = ? };
        let t: (a: float) = (a = ?);
        let ps: array<Point> = [{ x = ?, y = 1.0 }];
      `),
    ).toEqual(
      Array(4).fill(
        "An open value (?) must be a whole store or config argument, not part of an array, map or tuple",
      ),
    );
  });

  test("are rejected as field defaults, destructured lets and nested defaults", async () => {
    expect(
      await errors(`
        struct S { v: float = ?; }
        let (a: float, b: float): (a: float, b: float) = ?;
        let n: float = ?(?);
      `),
    ).toEqual([
      "A struct field default cannot be open",
      "A destructuring 'let' cannot be open",
      "The default of an open value cannot itself be open",
    ]);
  });

  test("cannot stand in for a remote instance", async () => {
    expect(await errors(`let g: Grow = ?;`)).toEqual([
      "An instance of remote 'Grow' cannot be open; write Grow(…) and declare 'Grow' without 'at' to leave its implementation open",
    ]);
  });

  test("cannot be used as a constant, but can be wired", async () => {
    expect(
      await errors(`
        let rate: float = ?;
        let p: Point = { x = ?, y = 1.0 };
        store s: float;
        init s = ?;
        let copy: float = rate;
        let px: float = p.x;
        let py: float = p.y;
        let sv: float = s;
        let grow: Grow = Grow(rate = rate);
        connect grow inputs (size = rate) outputs (size = p.x);
      `),
    ).toEqual([
      "'rate' is open (?) and has no value to use here",
      "'p.x' is open (?) and has no value to use here",
      "'s' is open (?) and has no value to use here",
      "'rate' is open (?) and has no value to use here",
    ]);
  });
});

describe("interfaces (remote types without 'at')", () => {
  test("can be instantiated, configured and connected", async () => {
    expect(
      await errors(`
        let a: float = 1.0;
        let b: float = 0.0;
        let m: Model = Model(label = "baseline");
        connect m inputs (x = a) outputs (y = b);
      `),
    ).toEqual([]);
  });

  test("are type checked like any remote", async () => {
    expect(
      await errors(`
        let a: string = "x";
        let m: Model = Model(label = 1.0);
        connect m inputs (x = a) outputs (y = a);
      `),
    ).toEqual([
      "Expected value of type 'string'",
      "Type mismatch for input 'x': bound element has type string, 'Model' input has type float",
      "Type mismatch for output 'y': bound element has type string, 'Model' output has type float",
    ]);
  });
});
