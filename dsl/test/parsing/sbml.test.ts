import { describe, expect, test } from "vitest";
import { EmptyFileSystem } from "langium";
import { parseHelper } from "langium/test";
import {
  generateStubPblang,
  parseSBML,
  type SbmlContent,
} from "../../src/language/sbml.js";
import { createProcessBigraphLanguageServices } from "../../src/language/process-bigraph-language-module.js";
import { Model } from "../../src/language/generated/ast.js";

// @ts-ignore
import libsbml from "libsbmljs_stable";

const sbmlstr =
  ' \
<!-- Created by libAntimony version v2.5 on 2014-10-09 21:22 with libSBML version 5.10.0. --> \
<sbml xmlns="http://www.sbml.org/sbml/level3/version1/core" level="3" version="1"> \
  <model id="__main" name="__main"> \
    <listOfCompartments> \
      <compartment sboTerm="SBO:0000410" id="default_compartment" spatialDimensions="3" size="1" constant="true"/> \
    </listOfCompartments> \
    <listOfSpecies> \
      <species id="S1" compartment="default_compartment" initialConcentration="1" hasOnlySubstanceUnits="false" boundaryCondition="false" constant="false"/> \
      <species id="S2" compartment="default_compartment" initialConcentration="0" hasOnlySubstanceUnits="false" boundaryCondition="false" constant="false"/> \
    </listOfSpecies> \
    <listOfParameters> \
      <parameter id="k0" value="0.1" constant="true"/> \
      <parameter id="k1" value="1" constant="true"/> \
      <parameter id="n" value="4" constant="true"/> \
      <parameter id="k2" value="0.2" constant="true"/> \
    </listOfParameters> \
    <listOfReactions> \
      <reaction id="_J0" reversible="true" fast="false"> \
        <listOfProducts> \
          <speciesReference species="S1" stoichiometry="1" constant="true"/> \
        </listOfProducts> \
        <kineticLaw> \
          <math xmlns="http://www.w3.org/1998/Math/MathML"> \
            <ci> k0 </ci> \
          </math> \
        </kineticLaw> \
      </reaction> \
      <reaction id="_J1" reversible="true" fast="false"> \
        <listOfReactants> \
          <speciesReference species="S1" stoichiometry="1" constant="true"/> \
        </listOfReactants> \
        <listOfProducts> \
          <speciesReference species="S2" stoichiometry="1" constant="true"/> \
        </listOfProducts> \
        <kineticLaw> \
          <math xmlns="http://www.w3.org/1998/Math/MathML"> \
            <apply> \
              <divide/> \
              <apply> \
                <times/> \
                <ci> k1 </ci> \
                <ci> S1 </ci> \
              </apply> \
              <apply> \
                <plus/> \
                <cn type="integer"> 1 </cn> \
                <apply> \
                  <power/> \
                  <ci> S1 </ci> \
                  <ci> n </ci> \
                </apply> \
              </apply> \
            </apply> \
          </math> \
        </kineticLaw> \
      </reaction> \
      <reaction id="_J2" reversible="true" fast="false"> \
        <listOfReactants> \
          <speciesReference species="S2" stoichiometry="1" constant="true"/> \
        </listOfReactants> \
        <kineticLaw> \
          <math xmlns="http://www.w3.org/1998/Math/MathML"> \
            <apply> \
              <times/> \
              <ci> k2 </ci> \
              <ci> S2 </ci> \
            </apply> \
          </math> \
        </kineticLaw> \
      </reaction> \
    </listOfReactions> \
  </model> \
</sbml>';

// also see https://github.com/sys-bio/libantimonyjs/blob/main/test/test_antimony_wrap.js

describe("Synchronous reading from inline string", function () {
  test("loads SBML from an inline string", async () => {
    const parsed = parseSBML(sbmlstr);

    // two species
    expect(parsed.species.length).toEqual(2);
    expect(parsed.species[0].id).toEqual("S1");
    expect(parsed.species[0].initialConcentration).toEqual(1);
    expect(parsed.species[1].id).toEqual("S2");
    expect(parsed.species[1].initialConcentration).toEqual(0);

    // one compartment
    expect(parsed.compartments.length).toEqual(1);
    expect(parsed.compartments[0].id).toEqual("default_compartment");
    expect(parsed.compartments[0].size).toEqual(1);

    // // three parameters
    expect(parsed.parameters.length).toEqual(4);
    expect(parsed.parameters[0].id).toEqual("k0");
    expect(parsed.parameters[0].value).toEqual(0.1);
    expect(parsed.parameters[1].id).toEqual("k1");
    expect(parsed.parameters[1].value).toEqual(1);
    expect(parsed.parameters[2].id).toEqual("n");
    expect(parsed.parameters[2].value).toEqual(4);
    expect(parsed.parameters[3].id).toEqual("k2");
    expect(parsed.parameters[3].value).toEqual(0.2);

    // three reactions in model
    expect(parsed.reactions.length).toEqual(3);
    expect(parsed.reactions[0].id).toEqual("_J0");
    expect(parsed.reactions[0].reactants.length).toEqual(0);
    expect(parsed.reactions[0].products.length).toEqual(1);
    expect(parsed.reactions[1].products[0].species).toEqual("S2");
    expect(parsed.reactions[1].id).toEqual("_J1");
    expect(parsed.reactions[1].reactants.length).toEqual(1);
    expect(parsed.reactions[1].reactants[0].species).toEqual("S1");
    expect(parsed.reactions[2].id).toEqual("_J2");
    expect(parsed.reactions[2].reactants.length).toEqual(1);
    expect(parsed.reactions[2].reactants[0].species).toEqual("S2");
  });
});

async function validationErrors(pblang: string): Promise<string[]> {
  const services = createProcessBigraphLanguageServices(EmptyFileSystem);
  const document = await parseHelper<Model>(services.ProcessBigraphLanguage)(
    pblang,
    { validation: true },
  );
  return [
    ...document.parseResult.lexerErrors.map((e) => e.message),
    ...document.parseResult.parserErrors.map((e) => e.message),
    ...(document.diagnostics ?? [])
      .filter((d) => d.severity === 1)
      .map((d) => d.message),
  ];
}

describe("SBML stub generation", () => {
  test("generates a stub in the current DSL syntax", async () => {
    const stub = generateStubPblang(parseSBML(sbmlstr), "model", "../model.sbml");
    expect(stub).toBe(
      [
        "type float builtin",
        "type string builtin",
        "",
        "// SBML model 'model' (concentrations in 10e-6 mole/liter)",
        'let model_file: string = "../model.sbml";',
        "",
        "struct model_parameters {",
        "    k0: float = 0.1;",
        "    k1: float = 1;",
        "    n: float = 4;",
        "    k2: float = 0.2;",
        "}",
        "",
        "struct model_species {",
        "    S1: float = 1;",
        "    S2: float = 0;",
        "}",
        "",
      ].join("\n"),
    );
    expect(await validationErrors(stub)).toEqual([]);
  });

  test("handles missing values, amounts, exponents and unsafe names", async () => {
    const content: SbmlContent = {
      compartments: [{ id: "cell", size: 2 }],
      species: [
        { id: "A", compartment: "cell", initialAmount: 3 },
        { id: "B", compartment: "cell" },
        { id: "store", compartment: "cell", initialConcentration: -1e-7 },
      ],
      reactions: [],
      parameters: [
        { id: "kf", value: 2.5e-8 },
        { id: "kr" },
      ],
    };
    const stub = generateStubPblang(content, "BIOMD-0912.v2", "models/m.xml");
    expect(stub).toContain('let BIOMD_0912_v2_file: string = "models/m.xml";');
    expect(stub).toContain("    kf: float = 2.5e-8;");
    expect(stub).toContain("    kr: float;");
    expect(stub).toContain("    A: float = 1.5;");
    expect(stub).toContain("    B: float;");
    expect(stub).toContain("    store_: float = -1.0e-7;");
    expect(await validationErrors(stub)).toEqual([]);
  });
});
