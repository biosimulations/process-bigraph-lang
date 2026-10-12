/** The pieces of the pivot: type spellings, paths, the reader's classification rules and the printer's layout. */
import { describe, expect, test } from "vitest";
import { parseJson } from "../../src/language/v2/json.js";
import {
  type Dict,
  type Edge,
  MISSING,
  type Node,
  type Store,
} from "../../src/language/v2/model.js";
import {
  parsePath,
  pathFromDocument,
  pathToDocument,
  pathToText,
  wireFromDocument,
  wireToDocument,
} from "../../src/language/v2/paths.js";
import { printDocument, scalarText } from "../../src/language/v2/printer.js";
import {
  floatLiteral,
  pyFloatRepr,
  wrapText,
} from "../../src/language/v2/format.js";
import {
  readCompositeSpec,
  readDocument,
} from "../../src/language/v2/reader.js";
import { parseType, surface, toBigraph } from "../../src/language/v2/types.js";
import { writeDocument } from "../../src/language/v2/writer.js";
import { stringifyJson } from "../../src/language/v2/json.js";
import { assetLoader } from "../../src/language/v2/assets.js";

const doc = (text: string): Dict => parseJson(text) as Dict;

describe("types", () => {
  // (bigraph-schema form, DSL spelling): every row parses, prints its spelling and renders back to its source
  const table: [string, string][] = [
    ['"float"', "float"],
    ['"integer"', "int"],
    ['"boolean"', "bool"],
    ['"list[float]"', "list<float>"],
    ['"map[float]"', "map<string, float>"],
    ['"map[string,float]"', "map<string, float>"],
    ['"tuple[float,float]"', "tuple<float, float>"],
    ['"maybe[float]"', "maybe<float>"],
    ['"overwrite[array[float]]"', "overwrite<array<float>>"],
    ['"enum[a,b]"', "enum<a, b>"],
    ['"array[(3|4),float]"', "array<float>[3, 4]"],
    ['"a:float|b:integer"', "{ a: float; b: int; }"],
    ['"A~B"', "A | B"],
    ['"float{3.5}"', "float{3.5}"],
    ['"positive_float"', "positive_float"],
    [
      '{"_type": "map", "_value": "positive_float"}',
      "map<string, positive_float>",
    ],
    ['{"_type": "list", "_element": {"x": "float"}}', "list<{ x: float; }>"],
    ['{"_type": "float", "_default": 2.0}', "float{2.0}"],
    [
      '{"_type": "positive_array", "_shape": [10, 10], "_data": "float"}',
      "positive_array<float>[10, 10]",
    ],
    [
      '{"_type": "array", "_shape": [3, 3], "_data": "float", "_units": "uM"}',
      'array<float>[3, 3] @ "uM"',
    ],
    [
      '{"x": "float", "y": {"_type": "integer", "_default": 3}}',
      "{ x: float; y: int{3}; }",
    ],
    [
      '{"_type": "link", "_inputs": {"x": "float"}, "_outputs": {"y": "float"}}',
      "link<{ x: float; }, { y: float; }>",
    ],
    ['{"_type": "process", "_inputs": {"x": "float"}}', "process"],
  ];
  for (const [source, spelling] of table) {
    test(`${source} is ${spelling}`, () => {
      const spec = parseJson(source);
      const expr = parseType(spec);
      expect(surface(expr)).toBe(spelling);
      expect(stringifyJson(toBigraph(expr))).toBe(stringifyJson(spec)); // lossless: the source is kept
    });
  }
  test("rendering without a source uses the string form when possible", () => {
    expect(
      toBigraph({
        kind: "named",
        name: "list",
        args: [{ kind: "named", name: "float", args: [] }],
      }),
    ).toBe("list[float]");
    expect(toBigraph({ kind: "named", name: "int", args: [] })).toBe("integer");
    expect(
      toBigraph({
        kind: "named",
        name: "float",
        args: [],
        hasDefault: true,
        default: 1.0,
      }),
    ).toEqual({ _type: "float", _default: 1.0 });
    expect(
      toBigraph({
        kind: "struct",
        fields: { a: { kind: "named", name: "float", args: [] } },
      }),
    ).toEqual({ a: "float" });
  });
  test("a missing default is distinct from null", () => {
    expect(
      (parseType("float") as { hasDefault?: boolean }).hasDefault,
    ).toBeUndefined();
    const withNull = parseType(
      parseJson('{"_type": "float", "_default": null}'),
    ) as { default?: unknown };
    expect(withNull.default).toBeNull();
  });
});

describe("paths", () => {
  const cases: [unknown[], string][] = [
    [["A"], "A"],
    [["fields", "acetate"], "fields.acetate"],
    [["fields", "acetate", 0, 1], "fields.acetate[0][1]"],
    [["..", "A"], "../A"],
    [["..", "..", "x"], "../../x"],
    [[".."], ".."],
    [["*"], "*"],
    [["dFBA[0,0]", "mass"], '"dFBA[0,0]".mass'],
  ];
  for (const [wire, text] of cases) {
    test(text, () => {
      const path = pathFromDocument(wire);
      expect(pathToText(path)).toBe(text);
      expect(parsePath(text)).toEqual(path);
      expect(
        pathToDocument(path).map((s) =>
          typeof s === "bigint" ? Number(s) : s,
        ),
      ).toEqual(wire);
    });
  }
  test("a string wire is one step; nested wires are dicts", () => {
    expect(pathFromDocument("A").steps).toEqual(["A"]);
    const wire = wireFromDocument(
      doc(
        '{"substrates": {"glucose": ["fields", "glucose"], "acetate": "fields"}}',
      ),
    );
    expect(stringifyJson(wireToDocument(wire))).toBe(
      '{"substrates":{"glucose":["fields","glucose"],"acetate":["fields"]}}',
    );
  });
});

describe("reader", () => {
  test("stores, nodes and edges", () => {
    const document = readDocument(
      doc(`{"schema": {"A": "float", "C": "float", "fields": {"glucose": "positive_float"}},
            "state": {"A": 2.07, "fields": {"glucose": 10}, "counts": {},
                      "adder": {"_type": "process", "address": "local:!pkg.mod.Add", "inputs": {"a": ["A"]}, "interval": 0.5}}}`),
    );
    const children = document.root.children;
    const a = children.get("A") as Store;
    expect(a.$kind).toBe("store");
    expect(a.value).toBe(2.07);
    expect(surface(a.type!)).toBe("float");
    expect((children.get("C") as Store).value).toBe(MISSING); // schema only
    const fields = children.get("fields") as Node;
    expect(fields.$kind).toBe("node");
    expect((fields.children.get("glucose") as Store).value).toBe(BigInt(10));
    expect((children.get("counts") as Store).$kind).toBe("store"); // an untyped dict is a store
    const adder = children.get("adder") as Edge;
    expect(adder.kind).toBe("process");
    expect(adder.interval).toBe(0.5);
    expect(adder.address).toEqual({ protocol: "local", data: "!pkg.mod.Add" });
    expect(adder.ports).toBeUndefined();
  });
  test("sites and address sites", () => {
    const document = readDocument(
      doc(`{"schema": {}, "state": {"rate": {"_type": "site", "_sort": "float", "_default": 0.5},
            "p": {"x": {"_type": "site", "_sort": "float"}},
            "s": {"_type": "process", "address": {"_type": "site", "_sort": {"_type": "link", "_inputs": {"x": "float"}}}}}}`),
    );
    const rate = document.root.children.get("rate") as Store;
    expect(rate.site?.default).toBe(0.5);
    expect((document.root.children.get("p") as Node).$kind).toBe("node");
    expect(
      ((document.root.children.get("s") as Edge).address as { $kind: string })
        .$kind,
    ).toBe("site");
  });
  test("a map of edges keeps its type; a nested composite is read into its edge", () => {
    const adders = readDocument(
      doc(`{"schema": {"adders": {"_type": "map", "_value": {"_type": "process", "_inputs": {"a": "float"}}}},
            "state": {"adders": {"one": {"_type": "process", "address": "local:X"}}}}`),
    ).root.children.get("adders") as Node;
    expect(adders.$kind).toBe("node");
    expect(adders.type).toBeDefined();
    const agent = readDocument(
      doc(`{"schema": {}, "state": {"agent": {"_type": "process", "address": "local:Composite",
            "config": {"state": {"mass": 1.0, "grow": {"_type": "process", "address": "local:Grow", "inputs": {"mass": ["mass"]}}},
                       "bridge": {"inputs": {"mass": ["mass"]}}, "run_steps_on_init": true},
            "inputs": {"mass": ["mass"]}}, "mass": 1.0}}`),
    ).root.children.get("agent") as Edge;
    expect(agent.inner?.children.get("grow")?.$kind).toBe("edge");
    expect([...agent.config.keys()]).toEqual(["run_steps_on_init"]);
  });
  test("the saved form is detected and cleaned", () => {
    const document = readDocument(
      doc(`{"schema": {"A": "float", "global_time": "float",
                       "add": {"_type": "process", "address": "local:!m.Add", "_inputs": "a:float|b:float", "inputs": "wires", "interval": 1.0}},
            "state": {"A": 1.0, "global_time": 2.0,
                      "add": {"address": {"protocol": "local", "data": "!m.Add"}, "config": {}, "_inputs": "a:float|b:float",
                              "inputs": {"a": ["A"]}, "interval": 1.0, "_contract": {"face": {}}, "instance": "<object>"}}}`),
    );
    expect(document.source).toBe("saved");
    expect([...document.root.children.keys()]).toEqual(["A", "add"]);
    const add = document.root.children.get("add") as Edge;
    expect(add.kind).toBe("process");
    expect(Object.keys(add.ports!.inputs!)).toEqual(["a", "b"]);
    expect(add.extras.size).toBe(0);
  });
  test("extra keys and options are kept; an edge without a kind is an error", () => {
    const document = readDocument(
      doc(`{"schema": {}, "state": {"e": {"_type": "step", "address": "local:X", "note": "hi", "_triggers": [["a"]]}},
            "global_time_precision": 6, "composition": {"legacy": true}}`),
    );
    const e = document.root.children.get("e") as Edge;
    expect([...e.extras.keys()]).toEqual(["note", "_triggers"]);
    expect([...document.options.keys()]).toEqual(["global_time_precision"]);
    expect([...document.extras.keys()]).toEqual(["composition"]);
    expect(() =>
      readDocument(
        doc('{"schema": {}, "state": {"x": {"address": "local:X"}}}'),
      ),
    ).toThrow(/neither a _type/);
  });
  test("a CompositeSpec's parameters and emitters", () => {
    const spec = readCompositeSpec(
      doc(`{"name": "demo", "description": "A demo.", "tags": ["t"], "requires": {"processes": ["X"]},
            "parameters": {"dt": {"type": "float", "default": 0.1, "description": "step"}, "label": {"type": "string"}},
            "emitters": [{"address": "local:ParquetEmitter", "paths": ["a", "b/c"]}],
            "state": {"x": {"_type": "process", "address": "local:X", "interval": "\${dt}", "config": {"name": "run_\${label}"}}},
            "default_n_steps": 10}`),
    );
    expect(spec.source).toBe("composite_spec");
    expect(spec.params.map((p) => p.name)).toEqual(["dt", "label"]);
    const x = spec.root.children.get("x") as Edge;
    expect(x.interval).toEqual({ $kind: "param", name: "dt" });
    expect(x.config.get("name")).toEqual({
      $kind: "param",
      name: "label",
      template: "run_${label}",
    });
    expect(spec.emitters[0].paths.map((p) => p.steps)).toEqual([
      ["a"],
      ["b", "c"],
    ]);
    expect([...spec.extras.keys()]).toEqual(["default_n_steps"]);
  });
});

describe("printer", () => {
  test("scalars spell as Python does", () => {
    expect(scalarText(null)).toBe("null");
    expect(scalarText(true)).toBe("true");
    expect(scalarText(BigInt(3))).toBe("3");
    expect(scalarText('a"b')).toBe('"a\\"b"');
    expect(floatLiteral(1.0)).toBe("1.0");
    expect(floatLiteral(2.5e-3)).toBe("0.0025");
    expect(floatLiteral(1e-7)).toBe("1.0e-07");
    expect(pyFloatRepr(100000.0)).toBe("100000.0");
    expect(pyFloatRepr(1e16)).toBe("1e+16");
    expect(pyFloatRepr(0.1)).toBe("0.1");
    expect(pyFloatRepr(1234567890123456.0)).toBe("1234567890123456.0");
  });
  test("struct and map literals, quoting, tuples", () => {
    const text = printDocument(
      readDocument(
        doc(
          '{"schema": {}, "state": {"cfg": {"a": {"b": 1}, "k-1": 2}, "dFBA[0,0]": 1.5, "t": {"__tuple__": true, "data": [1, 2]}}}',
        ),
      ),
    ).text;
    expect(text).toContain('store cfg = { "a" = { b = 1 }, "k-1" = 2 };'); // one non-identifier key makes it a map literal
    expect(text).toContain('store "dFBA[0,0]" = 1.5;');
    expect(text).toContain("store t = (1, 2);");
  });
  test("blocks break when too wide", () => {
    const config = Object.fromEntries(
      [...Array(8).keys()].map((i) => [`key_${i}`, `value number ${i}`]),
    );
    const text = printDocument(
      readDocument(
        doc(
          JSON.stringify({
            schema: {},
            state: { e: { _type: "step", address: "local:X", config } },
          }),
        ),
      ),
    ).text;
    expect(text).toContain('    config {\n      key_0 = "value number 0",\n');
    expect(text.endsWith("}\n")).toBe(true);
  });
  test("interfaces are declared once and named by address; edges without ports use `at`", () => {
    const edge = {
      _type: "process",
      _inputs: { a: "float" },
      address: "local:!pkg.mod.Add",
    };
    const other = {
      _type: "process",
      _inputs: { b: "float" },
      address: "local:!pkg.mod.Add",
    };
    const text = printDocument(
      readDocument(
        doc(
          JSON.stringify({
            schema: {},
            state: { one: edge, two: { ...edge }, three: other },
          }),
        ),
      ),
    ).text;
    expect(text.split('process Add at "local:!pkg.mod.Add" {').length - 1).toBe(
      1,
    );
    expect(text).toContain('process Add_2 at "local:!pkg.mod.Add" {');
    expect(text).toContain("process one : Add {");
    expect(text).toContain("process three : Add_2 {");
    const bare = printDocument(
      readDocument(
        doc(
          '{"schema": {}, "state": {"em": {"_type": "step", "address": "local:RAMEmitter", "inputs": {"a": ["A"]}}}}',
        ),
      ),
    ).text;
    expect(bare).toContain(
      'step em at "local:RAMEmitter" {\n    inputs { a -> A }\n  }',
    );
  });
  test("sites print as open values", () => {
    const text = printDocument(
      readDocument(
        doc(`{"schema": {}, "state": {"rate": {"_type": "site", "_sort": "float", "_default": 0.5},
              "s": {"_type": "process", "address": {"_type": "site", "_sort": "link[x:float,y:float]"},
                    "config": {"k": {"_type": "site", "_sort": "integer"}}}}}`),
      ),
    ).text;
    expect(text).toContain("store rate: float = ?(0.5);");
    expect(text).toContain("process s at ? {");
    expect(text).toContain("config { k = ? as int }");
  });
  test("large values are externalized and reloadable; small arrays print inline", () => {
    const data = [...Array(5).keys()].map((i) =>
      [...Array(100).keys()].map((j) => i * 100 + j + 0.0),
    );
    const big = { __numpy__: true, dtype: "float64", shape: [5, 100], data };
    const long = "x".repeat(2000);
    const original = readDocument(
      doc(
        JSON.stringify({
          schema: {},
          state: {
            fields: { A: big },
            e: { _type: "step", address: "local:X", config: { text: long } },
          },
        }),
      ),
    );
    const printed = printDocument(original, { name: "demo" });
    expect(printed.text).toContain(
      'A = array(file("demo.assets/fields_A.json"), dtype = "float64", shape = [5, 100])',
    );
    expect(printed.text).toContain('text = file("demo.assets/e_text.txt")');
    expect([...printed.assets.keys()]).toEqual([
      "demo.assets/fields_A.json",
      "demo.assets/e_text.txt",
    ]);
    // the writer resolves sidecar references through a loader
    const loader = assetLoader((p) => printed.assets.get(p)!);
    const reloaded = assetLoader((p) => printed.assets.get(p)!)({
      $kind: "external",
      path: "demo.assets/e_text.txt",
      format: "text",
    });
    expect(reloaded).toBe(long);
    expect(stringifyJson(writeDocument(original, loader))).toBe(
      stringifyJson(writeDocument(original)),
    );
    const small = printDocument(
      readDocument(
        doc(
          '{"schema": {"a": "array[float]"}, "state": {"a": {"__numpy__": true, "dtype": "float64", "shape": [2], "data": [1.0, 2.0]}}}',
        ),
      ),
    ).text;
    expect(small).toContain(
      'store a: array<float> = array([1.0, 2.0], dtype = "float64");',
    );
  });
  test("a typed store without a value, and doc comments wrap like textwrap", () => {
    expect(
      printDocument(
        readDocument(doc('{"schema": {"C": "float"}, "state": {}}')),
      ).text,
    ).toContain("store C: float;");
    expect(wrapText("a two-way exchange of words that goes on", 20)).toEqual([
      "a two-way exchange",
      "of words that goes",
      "on",
    ]);
  });
});
