/**
 * The embeddable API (`src/api.ts`): a `Pblang` session checks, compiles, decompiles and graphs from strings and
 * plain values, with the same results as the CLI and the committed snapshots.
 */
import { describe, expect, test } from "vitest";
import { execFileSync } from "node:child_process";
import * as fs from "node:fs";
import * as path from "node:path";
import { CompileError, loadDocument, Pblang } from "../../src/api.js";

const fixtures = path.resolve(__dirname, "../../../tests/fixtures/data/v2");
const read = (...parts: string[]) =>
  fs.readFileSync(path.join(fixtures, ...parts), "utf-8");

const manifests = [
  "test_registry.manifest.json",
  "viva_pde_particle.manifest.json",
];

function session(): Pblang {
  const pblang = new Pblang();
  for (const name of manifests) pblang.addManifest(read("interfaces", name));
  return pblang;
}

/** The committed sidecar assets of a snapshot, by the path the text references. */
function snapshotAssets(name: string): Record<string, string> {
  const directory = path.join(fixtures, "snapshots", `${name}.assets`);
  if (!fs.existsSync(directory)) return {};
  return Object.fromEntries(
    fs
      .readdirSync(directory)
      .map((f) => [
        `${name}.assets/${f}`,
        read("snapshots", `${name}.assets`, f),
      ]),
  );
}

describe("decompile", () => {
  test("prints a document to its snapshot", () => {
    const json = read("corpus", "v1", "growth_division.json");
    expect(session().decompile(json, { name: "growth_division" }).text).toBe(
      read("snapshots", "growth_division.pblang"),
    );
  });

  test("takes a parsed value too (lossy: JSON.parse reads 1.0 as 1)", () => {
    const pblang = session();
    const json = read("corpus", "template_sites.json");
    const parsed = JSON.parse(json);
    expect(pblang.decompile(parsed).text).toBe(
      pblang.decompile(JSON.stringify(parsed)).text,
    );
  });

  test("returns sidecar assets by path", () => {
    const printed = session().decompile(
      read("corpus", "hybrid_two_way_exchange.json"),
      { name: "hybrid_two_way_exchange" },
    );
    expect(printed.text).toBe(
      read("snapshots", "hybrid_two_way_exchange.pblang"),
    );
    const committed = snapshotAssets("hybrid_two_way_exchange");
    expect(Object.keys(printed.assets).sort()).toEqual(
      Object.keys(committed).sort(),
    );
    for (const [asset, content] of Object.entries(printed.assets))
      expect(content.replace(/\n$/, "")).toBe(
        committed[asset].replace(/\n$/, ""),
      );
  });

  test("reads a CompositeSpec from YAML", () => {
    const printed = session().decompile(
      read("corpus", "reversible-dimerization.composite.yaml"),
      { name: "reversible-dimerization" },
    );
    expect(printed.text).toBe(
      read("snapshots", "reversible-dimerization.pblang"),
    );
  });

  test("rejects what is not a mapping", () => {
    expect(() => loadDocument("[1, 2]")).toThrow("not a document");
  });
});

describe("compile", () => {
  test("text -> document -> text is a fixpoint, assets included", async () => {
    const pblang = session();
    const name = "hybrid_two_way_exchange";
    const text = read("snapshots", `${name}.pblang`);
    const compiled = await pblang.compile(text, {
      assets: snapshotAssets(name),
      force: true,
    });
    expect(compiled.format).toBe("json");
    const again = pblang.decompile(compiled.text, { name });
    expect(again.text).toBe(text);
    expect(Object.keys(again.assets).sort()).toEqual(
      Object.keys(snapshotAssets(name)).sort(),
    );
  });

  test("agrees with the CLI", async () => {
    const name = "growth_division";
    const text = read("snapshots", `${name}.pblang`);
    const compiled = await session().compile(text, { force: true });
    const cli = execFileSync(
      "node",
      [
        path.resolve(__dirname, "../../bin/cli.js"),
        "compile",
        path.join(fixtures, "snapshots", `${name}.pblang`),
        "--force",
        "-i",
        ...manifests.map((m) => path.join(fixtures, "interfaces", m)),
      ],
      { encoding: "utf-8", stdio: ["ignore", "pipe", "ignore"] },
    );
    expect(compiled.text).toBe(cli);
  });

  test("writes a CompositeSpec as YAML", async () => {
    const compiled = await session().compile(
      read("snapshots", "reversible-dimerization.pblang"),
      { to: "spec" },
    );
    expect(compiled.format).toBe("yaml");
    expect(compiled.text).toContain("name: reversible-dimerization");
    expect(compiled.text).toContain("emitters:");
  });

  test("stops on errors and reports them", async () => {
    const pblang = session();
    const text = `import tests.fixtures.test_registry.toy_library.{AddFloatsProcess};
composite demo {
  store a: float = 1.0;
  process add : AddFloatsProcess { inputs { nope -> a } }
}
`;
    const error = await pblang.compile(text).catch((e: unknown) => e);
    expect(error).toBeInstanceOf(CompileError);
    const codes = (error as CompileError).diagnostics.map((d) => d.code);
    expect(codes).toContain("S021");
  });

  test("a parse error is a diagnostic", async () => {
    const result = await session().check("composite { store a: float = ; }");
    expect(result.ok).toBe(false);
    expect(result.diagnostics[0].slug).toBe("parse");
  });

  test("a missing asset fails loudly", async () => {
    await expect(
      session().compile(read("snapshots", "hybrid_two_way_exchange.pblang"), {
        force: true,
      }),
    ).rejects.toThrow("missing asset");
  });
});

describe("check", () => {
  test("checks a snapshot against the session's manifests, and sessions are independent", async () => {
    const text = read("snapshots", "saved_toy_add_floats.pblang");
    const withHeaders = await session().check(text);
    expect(withHeaders.ok).toBe(true);
    const without = await new Pblang().check(text);
    expect(without.diagnostics.map((d) => d.code)).toContain("S020");
  });

  test("a header text added to the session answers imports", async () => {
    const pblang = new Pblang();
    await pblang.addHeader(`module demo.lib;
process Add at "local:!demo.lib.Add" {
  inputs { a: float; b: float; }
  outputs { sum: float; }
}
`);
    const result = await pblang.check(`import demo.lib.{Add};
composite demo {
  store a: float = 1.0;
  store b: float = 2.0;
  store sum: float = 0.0;
  process add : Add { inputs { a -> a, b -> b } outputs { sum -> sum } }
}
`);
    expect(result.diagnostics.filter((d) => d.severity === "error")).toEqual(
      [],
    );
  });

  test("checked texts do not accumulate in the session", async () => {
    const pblang = new Pblang();
    const header = `module demo.lib;
process Add at "local:!demo.lib.Add" { inputs { a: float; } }
`;
    const user = `import demo.lib.{Add};
composite demo { store a: float = 1.0; process add : Add { inputs { a -> a } } }
`;
    // a header that merely passed through `check` is gone again; one added with `addHeader` stays
    await pblang.check(header);
    expect((await pblang.check(user)).diagnostics.map((d) => d.code)).toContain(
      "S020",
    );
    await pblang.addHeader(header);
    expect((await pblang.check(user)).ok).toBe(true);
  });
});

describe("graph", () => {
  test("from text and from a document", async () => {
    const pblang = session();
    const fromDocument = await pblang.graph({
      document: read("corpus", "v1", "growth_division.json"),
    });
    const fromText = await pblang.graph({
      text: read("snapshots", "growth_division.pblang"),
    });
    expect(fromDocument.nodes.map((n) => n.id)).toEqual(
      fromText.nodes.map((n) => n.id),
    );
    expect(fromDocument.edges.length).toBeGreaterThan(0);
    expect(JSON.stringify(fromDocument)).toBe(JSON.stringify(fromText));
  });
});
