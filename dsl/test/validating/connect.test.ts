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
  type int builtin
  type float builtin
  type string builtin
  remote step Add at "pkg.Add" {
    config (unused: string)
    inputs (left: float, right: float)
    outputs (result: float)
  }
  type AddAlias = Add
  struct S { A: float; B: float; C: float; I: int; name: string; }
  let s: S = { A=1.0, B=2.0, C=3.0, I=1, name="n" };
  let add: Add = Add(unused="x");
  remote step Emit at "pkg.Emit" {
    config (unused: string)
    inputs (value: float)
  }
  let emit: Emit = Emit(unused="x");
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

describe("connect statement type checking", () => {
  test("accepts a fully and correctly bound instance", async () => {
    expect(
      await errors(
        `connect add inputs (left=s.A, right=s.B) outputs (result=s.C);`,
      ),
    ).toEqual([]);
  });

  test("accepts an instance whose type is an alias of a remote type", async () => {
    expect(
      await errors(`
        let aliased: AddAlias = Add(unused="x");
        connect aliased inputs (left=s.A, right=s.B) outputs (result=s.C);
      `),
    ).toEqual([]);
  });

  test("widens int inputs to float", async () => {
    expect(
      await errors(
        `connect add inputs (left=s.I, right=s.B) outputs (result=s.C);`,
      ),
    ).toEqual([]);
  });

  test("rejects a float output bound to an int element", async () => {
    expect(
      await errors(
        `connect add inputs (left=s.A, right=s.B) outputs (result=s.I);`,
      ),
    ).toEqual([
      "Type mismatch for output 'result': bound element has type int, 'Add' output has type float",
    ]);
  });

  test("rejects input type mismatches", async () => {
    expect(
      await errors(
        `connect add inputs (left=s.name, right=s) outputs (result=s.C);`,
      ),
    ).toEqual([
      "Type mismatch for input 'left': bound element has type string, 'Add' input has type float",
      "Type mismatch for input 'right': bound element has type struct S, 'Add' input has type float",
    ]);
  });

  test("reports unknown, duplicate and missing bindings", async () => {
    expect(
      await errors(
        `connect add inputs (left=s.A, left=s.B, extra=s.A) outputs (total=s.C);`,
      ),
    ).toEqual([
      "Duplicate input binding 'left'",
      "'Add' has no input named 'extra'",
      "'Add' has no output named 'total'",
      "Missing input binding 'right' for 'Add'",
      "Missing output binding 'result' for 'Add'",
    ]);
  });

  test("rejects an instance that is not a remote step or process", async () => {
    expect(
      await errors(
        `connect s inputs (left=s.A, right=s.B) outputs (result=s.C);`,
      ),
    ).toEqual([
      "'s' is not a remote step or process instance (type struct S)",
    ]);
  });

  test("leaves unresolved references to the linker", async () => {
    const result = await errors(
      `connect add inputs (left=s.X, right=s.B) outputs (result=s.C);`,
    );
    expect(result).toHaveLength(1);
    expect(result[0]).toContain("Could not resolve reference");
  });

  test("omits the outputs clause for a remote with no outputs", async () => {
    expect(await errors(`connect emit inputs (value=s.A);`)).toEqual([]);
  });

  test("accepts an empty outputs clause for a remote with no outputs", async () => {
    expect(
      await errors(`connect emit inputs (value=s.A) outputs ();`),
    ).toEqual([]);
  });

  test("reports ports left unbound by an omitted or empty clause", async () => {
    expect(
      await errors(`
        connect add outputs (result=s.C);
        connect emit inputs ();
      `),
    ).toEqual([
      "Missing input binding 'left' for 'Add'",
      "Missing input binding 'right' for 'Add'",
      "Missing input binding 'value' for 'Emit'",
    ]);
  });

  test("instantiates a remote without config using an empty argument list", async () => {
    expect(
      await errors(`
        remote step Sink at "pkg.Sink" { inputs (value: float) }
        let sink: Sink = Sink();
        connect sink inputs (value=s.A);
      `),
    ).toEqual([]);
  });

  test("still requires config arguments when the remote declares config", async () => {
    const result = await errors(`let bad: Emit = Emit();`);
    expect(result.length).toBeGreaterThan(0);
    expect(result.every((m) => m === "Missing required argument 'unused'")).toBe(true);
  });
});
