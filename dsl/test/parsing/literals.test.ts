import { afterEach, beforeAll, describe, expect, test, vi } from "vitest";
import { EmptyFileSystem, type LangiumDocument } from "langium";
import { clearDocuments, parseHelper } from "langium/test";
import { createProcessBigraphLanguageServices } from "../../src/language/process-bigraph-language-module.js";
import { Model } from "../../src/language/generated/ast.js";

let services: ReturnType<typeof createProcessBigraphLanguageServices>;
let document: LangiumDocument<Model> | undefined;
// Chevrotain reports an ambiguous decision once, the first time the parser reaches it,
// so parse a sample that exercises the top-level and value alternatives.
let parserBuildOutput = "";
const sample = `
  type float builtin
  type string builtin
  struct P { x: float; }
  type A = P
  remote step R at "pkg.R" { config (c: string) inputs (i: float) outputs (o: float) }
  unit u: ["m"]
  store s: P;
  init s = { x = 1.0 };
  let r: R = R(c = "c");
  let v: array<P> = [{ x = 1.0 }, {}];
  let m: map<string, float> = { "a" = 1.0 };
  let t: (a: float) = (a = 1.0);
  let q: float = s.x;
  connect r inputs (i = s.x) outputs (o = s.x);
`;

beforeAll(async () => {
  const log = vi.spyOn(console, "log").mockImplementation(() => {});
  const warn = vi.spyOn(console, "warn").mockImplementation(() => {});
  try {
    services = createProcessBigraphLanguageServices(EmptyFileSystem);
    const doc = await parseHelper<Model>(services.ProcessBigraphLanguage)(sample);
    expect(doc.parseResult.parserErrors).toHaveLength(0);
    clearDocuments(services.shared, [doc]);
    parserBuildOutput = [...log.mock.calls, ...warn.mock.calls]
      .flat()
      .join("\n");
  } finally {
    log.mockRestore();
    warn.mockRestore();
  }
});

afterEach(async () => {
  document && clearDocuments(services.shared, [document]);
});

const preamble = `
  type int builtin
  type float builtin
  type string builtin
  type bool builtin
  struct P { x: float; y: float; }
  struct Empty { }
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

describe("grammar", () => {
  test("parses without ambiguity warnings", () => {
    expect(parserBuildOutput).not.toContain("Ambiguous");
  });
});

describe("struct and map literals", () => {
  test("parses struct literals and literal-keyed maps", async () => {
    expect(
      await errors(`
        let p: P = { x = 1.0, y = 2.0 };
        let byName: map<string, P> = { "a" = { x = 1.0, y = 2.0 }, };
        let byInt: map<int, float> = { 1 = 1.0, 2 = 2.0 };
        let byBool: map<bool, string> = { true = "t", false = "f" };
      `),
    ).toEqual([]);
  });

  test("accepts {} as an empty map or an empty struct", async () => {
    expect(
      await errors(`
        let m: map<string, float> = {};
        let e: Empty = {};
      `),
    ).toEqual([]);
  });

  test("explains that map keys must be literals", async () => {
    expect(await errors(`let m: map<string, float> = { a = 1.0 };`)).toEqual([
      `Expected a map literal; map keys must be literals, e.g. { "key" = value }`,
    ]);
  });

  test("checks map key types", async () => {
    expect(await errors(`let m: map<int, float> = { "a" = 1.0 };`)).toEqual([
      "Expected value of type 'int'",
    ]);
  });

  test("rejects a map literal where a struct is expected", async () => {
    expect(await errors(`let p: P = { "x" = 1.0 };`)).toEqual([
      "Expected struct of type 'P'",
    ]);
  });
});
