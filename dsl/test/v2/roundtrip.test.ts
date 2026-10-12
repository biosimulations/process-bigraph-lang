/**
 * The round trip of real documents through the model: every corpus document prints to its committed snapshot
 * byte for byte (text and sidecar assets), every snapshot is a fixpoint through parse -> bind -> print, the v1
 * expected documents write back exactly, and a bound snapshot writes a document equivalent to its original.
 */
import { describe, expect, test } from "vitest";
import { EmptyFileSystem } from "langium";
import { parseHelper } from "langium/test";
import * as fs from "node:fs";
import * as path from "node:path";
import { createProcessBigraphLanguageServices } from "../../src/language/process-bigraph-language-module.js";
import type { V2Module } from "../../src/language/generated/ast.js";
import { assetLoader } from "../../src/language/v2/assets.js";
import { bindModule } from "../../src/language/v2/bind.js";
import { Registry } from "../../src/language/v2/headers.js";
import { parseJson, stringifyJson } from "../../src/language/v2/json.js";
import {
  type Dict,
  isDict,
  isNdArray,
  isTuple,
} from "../../src/language/v2/model.js";
import {
  printDocument,
  printInterfaces,
  printModel,
} from "../../src/language/v2/printer.js";
import {
  readCompositeSpec,
  readDocument,
} from "../../src/language/v2/reader.js";
import { canon, parseType } from "../../src/language/v2/types.js";
import { writeDocument } from "../../src/language/v2/writer.js";
import { parseYaml } from "../../src/language/v2/yaml.js";

const fixtures = path.resolve(__dirname, "../../../tests/fixtures/data/v2");
const corpus = (name: string) => path.join(fixtures, "corpus", name);
const snapshot = (name: string) =>
  fs.readFileSync(path.join(fixtures, "snapshots", name), "utf-8");

const registry = new Registry();
for (const name of [
  "test_registry.manifest.json",
  "viva_pde_particle.manifest.json",
])
  registry.addManifest(
    JSON.parse(
      fs.readFileSync(path.join(fixtures, "interfaces", name), "utf-8"),
    ),
  );

const services = createProcessBigraphLanguageServices(EmptyFileSystem);
const parse = parseHelper<V2Module>(services.PblangV2);

function loadDocument(file: string): Dict {
  return parseJson(fs.readFileSync(file, "utf-8")) as Dict;
}

/** The documents with a committed snapshot, by snapshot name. */
const SNAPSHOT_DOCUMENTS: [string, string][] = [
  ["hybrid_two_way_exchange", corpus("hybrid_two_way_exchange.json")],
  ["template_sites", corpus("template_sites.json")],
  ["growth_division", corpus("v1/growth_division.json")],
  ["spatio_flux_II", corpus("v1/spatio_flux_II.json")],
  ["spatio_flux_III", corpus("v1/spatio_flux_III.json")],
  ["saved_toy_add_floats", corpus("v1/saved_toy_add_floats.json")],
];

describe("decompile prints the committed snapshots", () => {
  for (const [name, file] of SNAPSHOT_DOCUMENTS) {
    test(name, () => {
      const printed = printDocument(readDocument(loadDocument(file)), {
        name,
        registry,
      });
      expect(printed.text).toBe(snapshot(`${name}.pblang`));
      for (const [asset, content] of printed.assets) {
        // pre-commit's end-of-file fixer appends a newline to committed assets; that is not a difference
        const committed = snapshot(asset).replace(/\n$/, "");
        expect(content.replace(/\n$/, "")).toBe(committed);
      }
    });
  }
  test("reversible-dimerization (CompositeSpec yaml)", () => {
    const spec = parseYaml(
      fs.readFileSync(
        corpus("reversible-dimerization.composite.yaml"),
        "utf-8",
      ),
    ) as Dict;
    const printed = printDocument(readCompositeSpec(spec), {
      name: "reversible-dimerization",
    });
    expect(printed.text).toBe(snapshot("reversible-dimerization.pblang"));
  });
});

describe("every snapshot is a fixpoint through parse, bind and print", () => {
  const files = fs
    .readdirSync(path.join(fixtures, "snapshots"))
    .filter((f) => f.endsWith(".pblang"));
  const strip = (t: string) =>
    t
      .split("\n")
      .filter((l) => !l.startsWith("//"))
      .join("\n");
  for (const file of files) {
    test(file, async () => {
      const text = snapshot(file);
      const document = await parse(text);
      expect(document.parseResult.parserErrors).toEqual([]);
      const model = bindModule(document.parseResult.value, registry);
      const name = file.replace(/\.pblang$/, "");
      let printed: string;
      if (
        model.models.length > 0 &&
        model.root.children.size === 0 &&
        model.interfaces.length === 0
      )
        printed = model.models.map((m) => printModel(m)).join("");
      else if (model.interfaces.length > 0 && model.root.children.size === 0)
        printed = printInterfaces(model.interfaces, model.module ?? name);
      else printed = printDocument(model, { name, registry }).text;
      // model headers and interface files are regenerated from data: their comments are not the fixpoint's
      expect(strip(printed)).toBe(strip(text));
    });
  }
});

describe("the v1 expected documents write back exactly (not just modulo normalization)", () => {
  // the saved form is read with its runtime keys dropped, so it is not an exact case (see the equivalence tests)
  const files = fs
    .readdirSync(path.join(fixtures, "corpus", "v1"))
    .filter((f) => f.endsWith(".json") && !f.startsWith("saved_"));
  const exact = (document: Dict) => stringifyJson(sortedKeys(document), 1);
  for (const file of files) {
    test(file, () => {
      const original = loadDocument(corpus(`v1/${file}`));
      expect(exact(writeDocument(readDocument(original)))).toBe(
        exact(original),
      );
    });
  }
  test("template sites", () => {
    const original = loadDocument(corpus("template_sites.json"));
    expect(exact(writeDocument(readDocument(original)))).toBe(exact(original));
  });
});

/** Dict keys in sorted order, recursively; lists, tuples and arrays keep theirs (Python compares dicts as sets). */
function sortedKeys(value: unknown): unknown {
  if (isDict(value))
    return new Map(
      [...value]
        .sort(([a], [b]) => (a < b ? -1 : a > b ? 1 : 0))
        .map(([k, v]) => [k, sortedKeys(v)]),
    );
  if (Array.isArray(value)) return value.map(sortedKeys);
  if (isTuple(value)) return { ...value, items: value.items.map(sortedKeys) };
  if (isNdArray(value)) return { ...value, data: sortedKeys(value.data) };
  if (value && typeof value === "object")
    return Object.fromEntries(
      Object.entries(value as Record<string, unknown>)
        .sort()
        .map(([k, v]) => [k, sortedKeys(v)]),
    );
  return value;
}

describe("a bound snapshot writes a document equivalent to its original", () => {
  for (const [name, file] of SNAPSHOT_DOCUMENTS) {
    test(name, async () => {
      const original = readDocument(loadDocument(file));
      const printed = printDocument(original, { name, registry });
      const document = await parse(printed.text);
      const model = bindModule(document.parseResult.value, registry);
      const loader = assetLoader((p) => printed.assets.get(p)!);
      const bound = stringifyJson(canonical(writeDocument(model, loader)), 1);
      const expected = stringifyJson(canonical(writeDocument(original)), 1);
      expect(bound).toBe(expected);
    });
  }
});

// --- what the Python normalizer ignores: key order, type spelling, repeated faces, registry vs import addresses

function canonical(doc: Dict): unknown {
  return new Map<string, unknown>([
    ["schema", canonSchema(doc.get("schema"))],
    ["state", canonState(doc.get("state"))],
  ]);
}

function toMaps(value: unknown): unknown {
  if (isDict(value)) return new Map([...value].map(([k, v]) => [k, toMaps(v)]));
  if (Array.isArray(value)) return value.map(toMaps);
  if (isTuple(value)) return value.items.map(toMaps);
  if (
    value &&
    typeof value === "object" &&
    !(value as { $kind?: string }).$kind
  )
    return new Map(
      Object.entries(value as Record<string, unknown>).map(([k, v]) => [
        k,
        toMaps(v),
      ]),
    );
  return value;
}

function canonSchema(raw: unknown): unknown {
  const schema = toMaps(raw);
  if (
    typeof schema === "string" ||
    (isDict(schema) && schema.has("_type") && !schema.has("_inputs"))
  )
    return canon(parseType(schema));
  if (isDict(schema))
    return new Map(
      [...schema]
        .filter(([k]) => k !== "_type")
        .sort()
        .map(([k, v]) => [k, canonSchema(v)]),
    );
  return schema;
}

function canonState(state: unknown): unknown {
  if (isDict(state)) {
    const entries = [...state]
      .filter(
        ([k]) =>
          k !== "_inputs" &&
          k !== "_outputs" &&
          !(k === "_type" && state.get("_type") === "link"),
      )
      .sort();
    return new Map(
      entries.map(([k, v]) => [
        k,
        k === "_sort" || k === "schema"
          ? canonSchema(v)
          : k === "address" && typeof v === "string"
          ? v.replace(/^local:.*\./, "local:").replace(/^local:!/, "local:")
          : canonState(v),
      ]),
    );
  }
  if (Array.isArray(state)) return state.map(canonState);
  if (isTuple(state)) return state.items.map(canonState);
  if (isNdArray(state)) return canonState(state.data);
  if (typeof state === "bigint") return Number(state);
  return state;
}
