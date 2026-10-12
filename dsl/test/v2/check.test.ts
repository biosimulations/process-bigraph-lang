/**
 * The compliance suite of the static checker: the cases ported from the Python prototype's
 * tests/v2/test_check.py and tests/v2/test_models.py, run through the Langium grammar.
 */
import { beforeAll, describe, expect, test } from "vitest";
import { EmptyFileSystem } from "langium";
import { parseHelper } from "langium/test";
import * as fs from "node:fs";
import * as path from "node:path";
import { createProcessBigraphLanguageServices } from "../../src/language/process-bigraph-language-module.js";
import type { V2Module } from "../../src/language/generated/ast.js";
import { checkModule, type Diagnostic } from "../../src/language/v2/check.js";
import { Registry } from "../../src/language/v2/headers.js";

const fixtures = path.resolve(__dirname, "../../../tests/fixtures/data/v2");
const TOY = "tests.fixtures.test_registry.toy_library";
const SPATIO = "tests.fixtures.test_registry.spatio_flux.processes";

let parse: ReturnType<typeof parseHelper<V2Module>>;
let registry: Registry;

beforeAll(() => {
  const services = createProcessBigraphLanguageServices(EmptyFileSystem);
  parse = parseHelper<V2Module>(services.PblangV2);
  registry = new Registry();
  for (const name of [
    "test_registry.manifest.json",
    "viva_pde_particle.manifest.json",
  ]) {
    registry.addManifest(
      JSON.parse(
        fs.readFileSync(path.join(fixtures, "interfaces", name), "utf-8"),
      ),
    );
  }
});

async function check(
  text: string,
  reg: Registry = registry,
): Promise<Diagnostic[]> {
  const document = await parse(text);
  expect(document.parseResult.lexerErrors).toEqual([]);
  expect(document.parseResult.parserErrors).toEqual([]);
  return checkModule(document.parseResult.value, reg);
}

function codes(diagnostics: Diagnostic[]): Record<string, string[]> {
  const out: Record<string, string[]> = {};
  for (const d of diagnostics) (out[d.code] ??= []).push(d.path);
  return out;
}

describe("checks against headers, with no process code", () => {
  test("a clean document has no findings", async () => {
    const text = `
import ${TOY}.{AddFloatsProcess, SaveFloatToFileStep};
composite {
  store A: float = 2.07;
  store B: float = 3.5;
  store C: float;
  process add_nums : AddFloatsProcess {
    inputs { left_hand_addend -> A, right_hand_addend -> B }
    outputs { result -> C }
  }
  step print_result : SaveFloatToFileStep {
    config { output_file_path = "output.txt" }
    inputs { result -> C }
  }
}`;
    expect(await check(text)).toEqual([]);
  });

  test("mistakes are found", async () => {
    const text = `
import ${TOY}.{AddFloatsProcess, SaveFloatToFileStep};
import ${SPATIO}.{DynamicFBA};
composite {
  store A: float = 1.0;
  store label: string = "x";
  process add : AddFloatsProcess {
    inputs { left_hand_addend -> A, right_hand_addend -> label, extra -> A }
    outputs { result -> nowhere }
  }
  step save : SaveFloatToFileStep every 1.0 {
    config { output_file_path = "out.txt" }
    inputs { result -> ../../A }
  }
  process dfba : DynamicFBA { config { model_file = "textbook", colour = "red" } }
  step mystery at "local:Mystery" { inputs { a -> A } }
}`;
    const found = codes(await check(text));
    expect(found.S021).toEqual(["add/inputs/extra"]);
    expect(found.W200).toEqual(["add/inputs/right_hand_addend"]);
    expect(found.W211).toEqual(["add/outputs/result"]);
    expect(found.S022).toEqual(["dfba/config/colour"]);
    expect(found.T121).toContain("dfba/config/bounds");
    expect(found.T121).toContain("dfba/config/kinetic_params");
    expect(found.T130).toEqual(["save"]);
    expect(found.W110).toEqual(["save/inputs/result"]);
    expect(found.S020).toEqual(["mystery"]);
  });

  test("the viva-pde-particle hybrid against its generated headers", async () => {
    const text = fs.readFileSync(
      path.join(fixtures, "snapshots", "hybrid_two_way_exchange.pblang"),
      "utf-8",
    );
    const found = codes(await check(text));
    expect(
      Object.keys(found).filter(
        (c) => c.startsWith("E") || c.startsWith("T") || c === "S021",
      ),
    ).toEqual([]);
    expect(found.W211).toContain("recorder/inputs/particle_positions");
    expect(found.W211).toContain("particles/outputs/particle_positions");
    expect(found.I210).toEqual(["particles"]);
    expect(found.I220).toContain("pde/inputs/fields");
    expect(found.W221).toBeUndefined();
    expect(found.W223).toBeUndefined();
  });

  test("sub-port wires use the map value type", async () => {
    const text = `
import ${SPATIO}.{DynamicFBA};
composite {
  node fields { store glucose: positive_float = 1.0; store biomass: string = "x"; }
  process dfba : DynamicFBA {
    config { model_file = "textbook", kinetic_params = {}, substrate_update_reactions = {}, biomass_identifier = "biomass", bounds = {} }
    inputs { substrates { glucose -> fields.glucose, biomass -> fields.biomass } }
  }
}`;
    const found = codes(await check(text));
    expect(found.W200).toEqual(["dfba/inputs/substrates/biomass"]);
    expect(found.T121).toBeUndefined();
    expect(found.S021).toBeUndefined();
  });
});

describe("writer analysis", () => {
  const writers = (
    storeType: string,
    ...outputs: [string, string, string][]
  ) => `
composite {
  store x: ${storeType} = 0.0;
  ${outputs
    .map(
      ([kind, name, portType]) =>
        `${kind} ${name} at "local:${name}" { ports { outputs { out: ${portType}; } } outputs { out -> x } }`,
    )
    .join("\n  ")}
}`;

  test("additive writers are reported for review", async () => {
    const found = codes(
      await check(
        writers("float", ["process", "a", "float"], ["process", "b", "float"]),
      ),
    );
    expect(found.W220).toEqual(["x"]);
    expect(found.W221).toBeUndefined();
  });

  test("an overwriting writer next to another is order-dependent", async () => {
    expect(
      codes(
        await check(
          writers(
            "float",
            ["process", "a", "overwrite<float>"],
            ["process", "b", "float"],
          ),
        ),
      ).W221,
    ).toEqual(["x"]);
    expect(
      codes(
        await check(
          writers(
            "float",
            ["process", "a", "overwrite<float>"],
            ["process", "b", "overwrite<float>"],
          ),
        ),
      ).W221,
    ).toEqual(["x"]);
    expect(
      codes(
        await check(
          writers(
            "overwrite<float>",
            ["process", "a", "float"],
            ["process", "b", "float"],
          ),
        ),
      ).W221,
    ).toEqual(["x"]);
    const single = codes(
      await check(writers("float", ["process", "a", "overwrite<float>"])),
    );
    expect(single.W220 ?? single.W221 ?? single.W223).toBeUndefined();
  });

  test("a step publishing an array additively is suspicious", async () => {
    const text = `
composite {
  store fields: map<string, array<float>>;
  store conc: map<string, array<float>>;
  step adapter at "local:Adapter" { ports { outputs { conc: map<string, array<float>>; } } outputs { conc -> conc } }
  step good at "local:Good" { ports { outputs { conc: map<string, overwrite<array<float>>>; } } outputs { conc -> fields } }
  process pde at "local:Pde" { ports { outputs { f: map<string, array<float>>; } } outputs { f -> fields } }
}`;
    const found = codes(await check(text));
    expect(found.W223).toEqual(["adapter/outputs/conc"]);
    expect(found.W221).toEqual(["fields"]);
  });
});

describe("emit declarations", () => {
  test("emit paths are checked against stores and writers", async () => {
    const text = `
import ${TOY}.{AddFloatsProcess};
composite demo {
  store A: float = 1.0;
  store C: float;
  store label: string = "run";
  node pt { store x: float = 0.0; store y: float = 0.0; }
  process add : AddFloatsProcess { inputs { left_hand_addend -> A, right_hand_addend -> A } outputs { result -> C } }
}
emit ram { A, C, label, nope, global_time, pt.x };`;
    const found = codes(await check(text));
    expect(found.W240).toEqual(["emit/0/nope"]);
    expect(found.W241).toEqual(["emit/0/A", "emit/0/label", "emit/0/pt/x"]);
  });

  test("a store written below or above counts as written", async () => {
    const text = `
composite {
  node fields { store glucose: float = 1.0; store acetate: float = 1.0; }
  process p at "local:P" { outputs { out -> fields.glucose } }
}
emit ram { fields, fields.glucose };`;
    const found = codes(await check(text));
    expect(found.W240).toBeUndefined();
    expect(found.W241).toBeUndefined();
  });
});

describe("units", () => {
  const solver = (
    stores: [string, string][],
    ports: [string, string, string][],
  ) => `
composite {
  ${stores
    .map(([name, units]) => `store ${name}: float @ "${units}" = 0.0;`)
    .join("\n  ")}
  process solver at "local:Solver" {
    ports {
      inputs { ${ports
        .filter(([d]) => d === "inputs")
        .map(([, p, u]) => `${p}: float @ "${u}";`)
        .join(" ")} }
      outputs { ${ports
        .filter(([d]) => d === "outputs")
        .map(([, p, u]) => `${p}: float @ "${u}";`)
        .join(" ")} }
    }
    inputs { ${ports
      .filter(([d]) => d === "inputs")
      .map(([, p]) => `${p} -> ${p}`)
      .join(", ")} }
    outputs { ${ports
      .filter(([d]) => d === "outputs")
      .map(([, p]) => `${p} -> ${p}`)
      .join(", ")} }
  }
}`;

  test("unit variables bind from stores and check derived rates", async () => {
    const found = codes(
      await check(
        solver(
          [
            ["conc", "uM"],
            ["time", "s"],
            ["flux", "uM/s"],
          ],
          [
            ["inputs", "conc", "?U"],
            ["inputs", "time", "?T"],
            ["outputs", "flux", "?U/?T"],
          ],
        ),
      ),
    );
    expect(found.W201 ?? found.I230 ?? found.I231).toBeUndefined();
  });

  test("convertible units report the factor; incompatible ones are reported", async () => {
    const convertible = await check(
      solver(
        [
          ["conc", "uM"],
          ["time", "s"],
          ["flux", "mM/s"],
        ],
        [
          ["inputs", "conc", "?U"],
          ["inputs", "time", "?T"],
          ["outputs", "flux", "?U/?T"],
        ],
      ),
    );
    const w201 = convertible.filter((d) => d.code === "W201");
    expect(w201.map((d) => d.path)).toEqual(["solver/outputs/flux"]);
    expect(w201[0].message).toContain("factor 0.001");
    const incompatible = await check(
      solver(
        [
          ["conc", "kg"],
          ["time", "s"],
        ],
        [
          ["inputs", "conc", "uM"],
          ["inputs", "time", "?T"],
        ],
      ),
    );
    expect(
      incompatible.filter((d) => d.code === "W201").map((d) => d.path),
    ).toEqual(["solver/inputs/conc"]);
    expect(incompatible.find((d) => d.code === "W201")?.message).toContain(
      "incompatible",
    );
  });

  test("a variable is solved from a derived port; a direct binding wins", async () => {
    const solved = codes(
      await check(
        solver(
          [
            ["conc", "uM"],
            ["flux", "uM/min"],
          ],
          [
            ["inputs", "conc", "?U"],
            ["outputs", "flux", "?U/?T"],
          ],
        ),
      ),
    );
    expect(solved.W201 ?? solved.I230 ?? solved.I231).toBeUndefined();
    const direct = await check(
      solver(
        [
          ["conc", "uM"],
          ["flux", "uM/min"],
          ["clock", "s"],
        ],
        [
          ["inputs", "conc", "?U"],
          ["outputs", "flux", "?U/?T"],
          ["inputs", "clock", "?T"],
        ],
      ),
    );
    const w201 = direct.filter((d) => d.code === "W201");
    expect(w201.map((d) => d.path)).toEqual(["solver/outputs/flux"]);
    expect(w201[0].message).toContain("factor 60");
  });

  test("units on a map apply to sub-port wires", async () => {
    const text = `
composite {
  node fields { store A: float @ "mM" = 1.0; }
  process p at "local:P" { ports { inputs { substrates: map<string, float> @ "uM"; } } inputs { substrates { A -> fields.A } } }
}`;
    expect(codes(await check(text)).W201).toEqual(["p/inputs/substrates/A"]);
  });

  test("config values referencing a param are checked against the header's config units", async () => {
    const text = `
param step: float @ "min" = 0.5;
process Engine { config { dt: float @ "?T"; } inputs { t: float @ "?T"; } outputs { } }
composite {
  store clock: float @ "s" = 0.0;
  process e : Engine at "local:Engine" { config { dt = \${step} } inputs { t -> clock } }
}`;
    expect(codes(await check(text)).W201).toEqual(["e/config/dt"]);
  });
});

describe("model sites", () => {
  const header = fs.readFileSync(
    path.join(fixtures, "snapshots", "Caravagna2010.model.pblang"),
    "utf-8",
  );
  const sort = `
model ODEModel {
  time @ "?T";
  species { _: float @ "?U"; ... }
  parameters { r2: float; mu2: float; ... }
  meta { events = 0, kind = "concentration" }
}`;
  const use = `composite { store model : ODEModel = Caravagna2010; }`;

  test("a header is admitted by a matching sort", async () => {
    const found = codes(await check(header + sort + use));
    expect(found.G300 ?? found.G301 ?? found.W201).toBeUndefined();
  });

  test("sort requirements are enforced", async () => {
    expect(
      codes(
        await check(
          header +
            sort.replace(
              "parameters { r2: float; mu2: float; ... }",
              "parameters { r2: float; zz: float; ... }",
            ) +
            use,
        ),
      ).G301,
    ).toEqual(["model/parameters/zz"]);
    expect(
      codes(
        await check(header + sort.replace("events = 0", "events = 2") + use),
      ).G301,
    ).toEqual(["model/meta/events"]);
    expect(
      codes(
        await check(
          header +
            sort.replace(
              "parameters { r2: float; mu2: float; ... }",
              "parameters { r2: float; }",
            ) +
            use,
        ),
      ).G301,
    ).toEqual(["model/parameters"]);
    expect(
      codes(
        await check(
          header + sort + "composite { store model : ODEModel = Nope; }",
        ),
      ).G300,
    ).toEqual(["model"]);
  });

  test("sort units bind across the header", async () => {
    const fixed = sort.replace(
      'species { _: float @ "?U"; ... }',
      'species { T: float @ "uM"; ... }',
    );
    expect(codes(await check(header + fixed + use)).W201).toEqual([
      "model/species/T",
    ]);
    const undeclared = sort.replace(
      "parameters { r2: float; mu2: float; ... }",
      'parameters { r2: float @ "1/?T"; ... }',
    );
    expect(codes(await check(header + undeclared + use)).I232).toEqual([
      "model/parameters/r2",
    ]);
  });

  test("an open model site is reported as such", async () => {
    expect(
      codes(await check(sort + "composite { store model : ODEModel = ?; }"))
        .I301,
    ).toEqual(["model"]);
  });
});
