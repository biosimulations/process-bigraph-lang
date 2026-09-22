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
  remote step Emit at "pkg.Emit" {
    config (path: string)
    inputs (value: float)
  }
  remote step Sink at "pkg.Sink" { inputs (value: float) }
  type EmitAlias = Emit
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

describe("callable literal type checking", () => {
  test("accepts instances of the declared remote, directly or via an alias", async () => {
    expect(
      await errors(`
        let e: Emit = Emit(path="p");
        let a: EmitAlias = Emit(path="p",);
        let s: Sink = Sink();
      `),
    ).toEqual([]);
  });

  test("rejects an instance of a different remote", async () => {
    expect(await errors(`let e: Emit = Sink();`)).toEqual([
      "Expected an instance of remote 'Emit' but got an instance of 'Sink'",
    ]);
  });

  test("rejects a non-callable value for a remote type", async () => {
    expect(await errors(`let e: Emit = "p";`)).toEqual([
      "Expected an instance of remote 'Emit', e.g. Emit(…)",
    ]);
  });

  test("reports each config argument error exactly once", async () => {
    expect(
      await errors(`
        let missing: Emit = Emit();
        let extra: Sink = Sink(path="p");
        let duplicate: Emit = Emit(path="p", path="q");
        let wrongType: Emit = Emit(path=1.0);
      `),
    ).toEqual([
      "Missing required argument 'path'",
      "Unexpected argument 'path'",
      "Duplicate argument 'path'",
      "Expected value of type 'string'",
    ]);
  });

  test("checks config arguments outside of typed declarations", async () => {
    expect(await errors(`let xs: array<Emit> = [Emit()];`)).toEqual([
      "Missing required argument 'path'",
    ]);
  });

  test("does not accept a callable literal for a tuple type", async () => {
    expect(await errors(`let t: (path: string) = Emit(path="p");`)).toEqual([
      "Expected a tuple literal",
    ]);
  });

  test("assigns references to instances of the same remote only", async () => {
    expect(
      await errors(`
        let e: Emit = Emit(path="p");
        let same: Emit = e;
        let other: Sink = e;
      `),
    ).toEqual([
      "Reference is not assignable to expected type: actual=remote step Emit, expected=remote step Sink",
    ]);
  });
});
