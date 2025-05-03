import { XMLParser } from "fast-xml-parser";

// Define SBML types (simplified)
export type Species = {
  id: string;
  name?: string;
  compartment: string;
  initialAmount?: number;
  initialConcentration?: number;
};
export type Compartment = { id: string; name?: string; size?: number };
export type Reaction = {
  id: string;
  name?: string;
  reactants?: any;
  products?: any;
};
export type Parameter = {
  id: string;
  name?: string;
  value?: number;
  constant?: boolean;
};
export type SbmlContent = {
  compartments: Compartment[];
  species: Species[];
  reactions: Reaction[];
  parameters: Parameter[];
};

// Extract core features from SBML XML string
export function parseSBML(sbmlXml: string): SbmlContent {
  const parser = new XMLParser({
    ignoreAttributes: false,
    attributeNamePrefix: "",
    allowBooleanAttributes: true,
  });

  const sbml = parser.parse(sbmlXml);

  const model = sbml.sbml?.model;
  if (!model) throw new Error("SBML model not found");

  const compartments = extractArray(model.listOfCompartments?.compartment);
  const species = extractArray(model.listOfSpecies?.species);
  const reactions = extractArray(model.listOfReactions?.reaction);
  const parameters = extractArray(model.listOfParameters?.parameter);

  return {
    compartments: compartments.map(
      (c: any): Compartment => ({
        id: c.id,
        name: c.name,
        size: c.size ? parseFloat(c.size) : undefined,
      }),
    ),
    species: species.map(
      (s: any): Species => ({
        id: s.id,
        name: s.name,
        compartment: s.compartment,
        initialAmount: s.initialAmount
          ? parseFloat(s.initialAmount)
          : undefined,
        initialConcentration: s.initialConcentration
          ? parseFloat(s.initialConcentration)
          : undefined,
      }),
    ),
    reactions: reactions.map(
      (r: any): Reaction => ({
        id: r.id,
        name: r.name,
        reactants: extractArray(r.listOfReactants?.speciesReference),
        products: extractArray(r.listOfProducts?.speciesReference),
      }),
    ),
    parameters: parameters.map(
      (p: any): Parameter => ({
        id: p.id,
        name: p.name,
        value: p.value ? parseFloat(p.value) : undefined,
        constant: p.constant === "true",
      }),
    ),
  };
}

// Handle possible array or single object
function extractArray<T>(value: T | T[] | undefined): T[] {
  if (value === undefined) return [];
  return Array.isArray(value) ? value : [value];
}

export function generateStubPblang(
  sbmlContent: SbmlContent,
  name: string,
  sbmlFilePath: string,
): string {
  /**
   * generates DSL text for pblang for stub of an SBML model
   *
   *         // Generated SBML Stub
   *         type float builtin
   *         unit conc_unit: ["10e-6 mole/liter"]
   *
   *         sbml model file "../model.sbml"
   *             param k0: float default 0.1 [conc_unit]
   *             param k1: float default 1 [conc_unit]
   *             param n: float default 4 [conc_unit]
   *             param k2: float default 0.2 [conc_unit]
   *             var S1: float default 1 [conc_unit]
   *             var S2: float [conc_unit]
   *
   **/
  const float_type = "type float builtin";
  const conc_unit = 'unit conc_unit: ["10e-6 mole/liter"]';
  let pblang = "";
  pblang += `${float_type}\n`;
  pblang += `${conc_unit}\n`;
  pblang += `sbml ${name} file "${sbmlFilePath}"\n`;
  pblang += `\n`;
  for (const parameter of sbmlContent.parameters) {
    pblang += `    param ${parameter.id}: float default ${parameter.value} [conc_unit]\n`;
  }
  for (const species of sbmlContent.species) {
    let initialConcentration: number | undefined;
    if (species.initialConcentration) {
      initialConcentration = species.initialConcentration;
    } else if (species.initialAmount) {
      // find compartment size for this species
      const compartment = sbmlContent.compartments.find(
        (comp) => comp.id === species.compartment,
      );
      if (compartment) {
        const compartmentSize = compartment.size;
        if (compartmentSize) {
          initialConcentration = species.initialAmount / compartmentSize;
        }
      }
    }
    if (initialConcentration) {
      pblang += `    var ${species.id}: float default ${initialConcentration} [conc_unit]\n`;
    } else {
      pblang += `    var ${species.id}: float [conc_unit]\n`;
    }
  }

  return pblang;
}
