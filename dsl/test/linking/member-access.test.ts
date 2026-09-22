import { afterEach, beforeAll, describe, expect, test } from "vitest";
import { EmptyFileSystem, type LangiumDocument } from "langium";
import { clearDocuments, parseHelper } from "langium/test";
import { createProcessBigraphLanguageServices } from "../../src/language/process-bigraph-language-module.js";
import {
  Model,
  MemberCall,
  isConnectStatement,
} from "../../src/language/generated/ast.js";

let services: ReturnType<typeof createProcessBigraphLanguageServices>;
let parse: ReturnType<typeof parseHelper<Model>>;
let document: LangiumDocument<Model> | undefined;

beforeAll(async () => {
  services = createProcessBigraphLanguageServices(EmptyFileSystem);
  parse = parseHelper<Model>(services.ProcessBigraphLanguage);
});

afterEach(async () => {
  document && clearDocuments(services.shared, [document]);
});

const preamble = `
  type float builtin
  type string builtin
  remote step Add at "pkg.Add" {
    inputs (left: float, right: float)
    outputs (result: float)
  }
  let add: Add = Add(unused="x");
`;

// Renders each binding as `name=a.b.c` with unresolved segments shown as `<?name>`.
function bindings(doc: LangiumDocument<Model>): string[] {
  const connect = doc.parseResult.value.elements.find(isConnectStatement)!;
  return [...connect.inputBindings, ...connect.outputBindings].map(
    (b) => `${b.name}=${renderChain(b.variable)}`,
  );
}

function renderChain(call: MemberCall): string {
  const segment = call.element.ref?.name ?? `<?${call.element.$refText}>`;
  return call.previous ? `${renderChain(call.previous)}.${segment}` : segment;
}

function linkingErrors(doc: LangiumDocument<Model>): string[] {
  return doc.references
    .filter((r) => r.error)
    .map((r) => r.error!.message);
}

describe("Member access scoping", () => {
  test("resolves struct fields", async () => {
    document = await parse(`
      ${preamble}
      struct S { A: float; B: float; C: float; }
      let s: S = { A=1.0, B=2.0, C=3.0 };
      connect add inputs (left=s.A, right=s.B) outputs (result=s.C);
    `);
    expect(document.parseResult.parserErrors).toHaveLength(0);
    expect(bindings(document)).toEqual(["left=s.A", "right=s.B", "result=s.C"]);
  });

  test("resolves nested structs through type aliases", async () => {
    document = await parse(`
      ${preamble}
      struct Inner { x: float; }
      type InnerAlias = Inner
      struct Outer { inner: InnerAlias; y: float; }
      type OuterAlias = Outer
      let o: OuterAlias = { inner={ x=1.0 }, y=2.0 };
      connect add inputs (left=o.inner.x, right=o.y) outputs (result=o.inner.x);
    `);
    expect(document.parseResult.parserErrors).toHaveLength(0);
    expect(bindings(document)).toEqual([
      "left=o.inner.x",
      "right=o.y",
      "result=o.inner.x",
    ]);
  });

  test("resolves tuple elements", async () => {
    document = await parse(`
      ${preamble}
      let t: (a: float, b: float) = (a=1.0, b=2.0);
      connect add inputs (left=t.a, right=t.b) outputs (result=t.a);
    `);
    expect(document.parseResult.parserErrors).toHaveLength(0);
    expect(bindings(document)).toEqual(["left=t.a", "right=t.b", "result=t.a"]);
  });

  test("does not resolve unknown members or members of primitives", async () => {
    document = await parse(`
      ${preamble}
      struct S { A: float; }
      struct Other { B: float; }
      let s: S = { A=1.0 };
      let f: float = 1.0;
      connect add inputs (left=s.B, right=f.A) outputs (result=s.A.A);
    `);
    expect(document.parseResult.parserErrors).toHaveLength(0);
    expect(bindings(document)).toEqual([
      "left=s.<?B>",
      "right=f.<?A>",
      "result=s.A.<?A>",
    ]);
    expect(linkingErrors(document)).toHaveLength(3);
  });
});
