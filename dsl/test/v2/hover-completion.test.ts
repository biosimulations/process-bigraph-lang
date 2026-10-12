/**
 * Hover and completion for v2: headers resolved through the registry (manifests) and through header files
 * open in the workspace, ports and config keys of the edge's header, stores of the enclosing scope in paths.
 */
import { beforeAll, describe, expect, test } from "vitest";
import { EmptyFileSystem } from "langium";
import { expectCompletion, expectHover, parseHelper } from "langium/test";
import type { CompletionList } from "vscode-languageserver";
import * as fs from "node:fs";
import * as path from "node:path";
import { createProcessBigraphLanguageServices } from "../../src/language/process-bigraph-language-module.js";
import * as ast from "../../src/language/generated/ast.js";

const fixtures = path.resolve(__dirname, "../../../tests/fixtures/data/v2");
const TOY = "tests.fixtures.test_registry.toy_library";

const services = createProcessBigraphLanguageServices(EmptyFileSystem);
const parse = parseHelper<ast.Module>(services.Pblang);
const completion = expectCompletion(services.Pblang);
const hover = expectHover(services.Pblang);

beforeAll(() => {
  services.Pblang.validation.HeaderRegistry.addManifest(
    JSON.parse(
      fs.readFileSync(
        path.join(fixtures, "interfaces", "test_registry.manifest.json"),
        "utf-8",
      ),
    ),
  );
});

const ADD = `
import ${TOY}.{AddFloatsProcess, SaveFloatToFileStep};
composite {
  /// the first addend
  store A: float @ "nM" = 2.07;
  store B: float = 3.5;
  store C: float = 0.0;
  node cell { store mass: float = 1.0; }
  process <|>add_nums : <|>AddFloatsProcess every 1.0 {
    inputs { <|>left_hand_addend -> <|>A, right_hand_addend -> B }
    outputs { result -> C }
  }
}
emit <|>ram { A, cell.mass };
`;

describe("hover", () => {
  test("an edge shows its header from the registry", async () => {
    await hover({
      text: ADD,
      index: 0,
      hover:
        /\*\*process\*\* `add_nums` : AddFloatsProcess every 1\.0[\s\S]*process AddFloatsProcess at "local:!tests\.fixtures\.test_registry\.toy_library\.AddFloatsProcess" \{\n {2}inputs \{ left_hand_addend: float; right_hand_addend: float; \}\n {2}outputs \{ result: float; \}\n\}/,
    });
  });

  test("the interface name shows the header too", async () => {
    await hover({ text: ADD, index: 1, hover: /outputs \{ result: float; \}/ });
  });

  test("a port shows its type and the store it is wired to", async () => {
    await hover({
      text: ADD,
      index: 2,
      hover:
        /\*\*input port\*\* `left_hand_addend`: `float` of `AddFloatsProcess`\n\n(?:wired to )?\*\*store\*\* `A`: `float @ "nM"`\n\nunits `nM`/,
    });
  });

  test("a path segment shows the store with its docs", async () => {
    await hover({
      text: ADD,
      index: 3,
      hover: /\*\*store\*\* `A`: `float @ "nM"`[\s\S]*the first addend/,
    });
  });

  test("an emitter alias shows its address", async () => {
    await hover({
      text: ADD,
      index: 4,
      hover: "**emitter** `ram` is `local:RAMEmitter`",
    });
  });

  test("an inline header, a config key and a param", async () => {
    const text = `
/// grows a thing
process Grow at "local:Grow" {
  config {
    /// per tick
    rate: float = 0.1;
    n: int;
  }
  inputs { mass: float; }
}
param <|>dt: float = 0.5;
composite {
  store mass: float = 1.0;
  process <|>g : Grow every \${dt} { config { <|>rate = 0.2, n = 3 } inputs { mass -> mass } }
}
`;
    await hover({
      text,
      index: 0,
      hover: "```pblang\nparam dt: float = 0.5;\n```",
    });
    await hover({
      text,
      index: 1,
      hover:
        /process Grow at "local:Grow" \{\n {2}config \{ rate: float = 0\.1; n: int; \}\n {2}inputs \{ mass: float; \}\n\}[\s\S]*grows a thing/,
    });
    await hover({
      text,
      index: 2,
      hover:
        /\*\*config\*\* ```pblang\nrate: float = 0\.1;\n```\n\nof Grow\n\nper tick/,
    });
  });

  test("a wire to no declared store says so", async () => {
    await hover({
      text: `
composite {
  store A: float = 1.0;
  process p at "local:P" { inputs { x -> <|>missing } }
}`,
      index: 0,
      hover:
        "`missing`: no declared store; process-bigraph would create it from the port",
    });
  });
});

describe("completion", () => {
  const labels = (list: CompletionList) => list.items.map((i) => i.label);

  test("ports of the header, unwired first, and no keyword noise", async () => {
    await completion({
      text: `
import ${TOY}.{AddFloatsProcess};
composite {
  store A: float = 1.0;
  process p : AddFloatsProcess { inputs { right_hand_addend -> A, <|> } }
}`,
      index: 0,
      assert: (list) => {
        const sorted = [...list.items].sort((a, b) =>
          (a.sortText ?? a.label).localeCompare(b.sortText ?? b.label),
        );
        expect(sorted.map((i) => i.label)).toEqual([
          "left_hand_addend",
          "right_hand_addend",
        ]);
        expect(sorted[0].detail).toBe("float");
      },
    });
  });

  test("a partly typed port filters", async () => {
    await completion({
      text: `
import ${TOY}.{AddFloatsProcess};
composite {
  store A: float = 1.0;
  process p : AddFloatsProcess { outputs { re<|> } }
}`,
      index: 0,
      expectedItems: ["result"],
    });
  });

  test("a wire path offers the stores and nodes of the edge's parent", async () => {
    await completion({
      text: `
import ${TOY}.{AddFloatsProcess};
composite {
  store A: float = 1.0;
  store "[0,1]": float = 2.0;
  node cell { store mass: float = 1.0; }
  process p : AddFloatsProcess { inputs { left_hand_addend -> <|> } }
}`,
      index: 0,
      assert: (list) => {
        expect(labels(list)).toEqual(["A", "[0,1]", "cell"]);
        const quoted = list.items.find((i) => i.label === "[0,1]");
        expect(quoted?.textEdit).toMatchObject({ newText: '"[0,1]"' });
      },
    });
  });

  test("a path continues into a node's declarations and a dict store's keys", async () => {
    await completion({
      text: `
import ${TOY}.{AddFloatsProcess};
composite {
  store fields = { "glucose" = 1.0, "acetate" = 2.0 };
  node cell { store mass: float = 1.0; process p : AddFloatsProcess { inputs { left_hand_addend -> ../fields.<|> } } }
}`,
      index: 0,
      expectedItems: ["glucose", "acetate"],
    });
    await completion({
      text: `
composite {
  node cell { store mass: float = 1.0; store volume: float = 2.0; }
}
emit ram { cell.<|> };`,
      index: 0,
      expectedItems: ["mass", "volume"],
    });
  });

  test("config keys of the header, required first, with the value separator", async () => {
    await completion({
      text: `
process Grow at "local:Grow" { config { rate: float = 0.1; n: int; } }
composite {
  process g : Grow { config { <|> } }
}`,
      index: 0,
      assert: (list) => {
        const items = [...list.items].sort((a, b) =>
          (a.sortText ?? "").localeCompare(b.sortText ?? ""),
        );
        expect(items.map((i) => i.label)).toEqual(["n", "rate"]);
        expect(items[0].textEdit).toMatchObject({ newText: "n = " });
        expect(items[1].detail).toBe("rate: float = 0.1");
      },
    });
    await completion({
      text: `
process Grow at "local:Grow" { config { rate: float = 0.1; n: int; } }
composite {
  process g : Grow { config { n = 1, <|> } }
}`,
      index: 0,
      expectedItems: ["rate"],
    });
  });

  test("registry interfaces are offered with the import they need", async () => {
    await completion({
      text: `
import ${TOY}.{AddFloatsProcess};
composite {
  process p : <|>
}`,
      index: 0,
      assert: (list) => {
        expect(labels(list)).toContain("shared");
        expect(labels(list)).toContain("AddFloatsProcess");
        const save = list.items.find((i) => i.label === "SaveFloatToFileStep");
        expect(save?.detail).toBe(`step from ${TOY}`);
        expect(save?.additionalTextEdits?.[0].newText).toBe(
          ", SaveFloatToFileStep",
        );
        const spatio = list.items.find((i) => i.label === "DynamicFBA");
        expect(spatio?.additionalTextEdits?.[0].newText).toMatch(
          /^\nimport tests\.fixtures\.test_registry\.spatio_flux\.processes\.\{DynamicFBA\};$/,
        );
        // an already imported name needs no edit
        const add = list.items.find((i) => i.label === "AddFloatsProcess");
        expect(add?.additionalTextEdits).toBeUndefined();
      },
    });
  });

  test("emit aliases", async () => {
    await completion({
      text: `composite { store A: float = 1.0; }\nemit <|>`,
      index: 0,
      expectedItems: ["ram", "parquet", "sqlite", "xarray", "console", "json"],
    });
  });
});

describe("header files in the workspace", () => {
  test("an import resolves against an open header file: checked, hovered, completed", async () => {
    await parse(
      `
module demo.headers;
/// doubles a mass
process Doubler at "local:!demo.headers.Doubler" {
  config { factor: float = 2.0; }
  inputs { mass: float; }
  outputs { mass: float; }
}
`,
      { documentUri: "file:///workspace/demo/headers.pblang" },
    );
    const text = `
import demo.headers.{Doubler};
composite {
  store m: float = 1.0;
  process <|>d : Doubler { inputs { <|>mass -> m } outputs { bogus -> m } }
}
`;
    const document = await parse(text.replace(/<\|>/g, ""), {
      documentUri: "file:///workspace/demo/main.pblang",
      validation: true,
    });
    const codes = (document.diagnostics ?? []).map((d) => d.code);
    expect(codes).toContain("S021"); // the bogus output port, checked against the header file
    expect(codes).not.toContain("S020");
    await hover({
      text,
      index: 0,
      hover:
        /process Doubler at "local:!demo\.headers\.Doubler"[\s\S]*from `demo\.headers`[\s\S]*doubles a mass/,
      parseOptions: { documentUri: "file:///workspace/demo/hover.pblang" },
    });
    await completion({
      text: `
composite {
  store m: float = 1.0;
  process d : <|>
}`,
      index: 0,
      parseOptions: { documentUri: "file:///workspace/demo/completion.pblang" },
      assert: (list) => {
        const item = list.items.find((i) => i.label === "Doubler");
        expect(item?.detail).toBe("process from demo.headers");
        expect(item?.additionalTextEdits?.[0]).toMatchObject({
          newText: "import demo.headers.{Doubler};\n\n",
          range: { start: { line: 0, character: 0 } },
        });
      },
    });
  });
});
