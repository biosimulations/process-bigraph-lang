import { XMLParser } from 'fast-xml-parser';

// Define SBML types (simplified)
type Species = { id: string; name?: string; compartment: string; initialAmount?: number; initialConcentration?: number };
type Compartment = { id: string; name?: string; size?: number };
type Reaction = { id: string; name?: string; reactants?: any; products?: any };
type Parameter = { id: string; name?: string; value?: number; constant?: boolean };

// Extract core features from SBML XML string
export function parseSBML(sbmlXml: string) {
    const parser = new XMLParser({
        ignoreAttributes: false,
        attributeNamePrefix: '',
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
        compartments: compartments.map((c: any): Compartment => ({
            id: c.id,
            name: c.name,
            size: c.size ? parseFloat(c.size) : undefined,
        })),
        species: species.map((s: any): Species => ({
            id: s.id,
            name: s.name,
            compartment: s.compartment,
            initialAmount: s.initialAmount ? parseFloat(s.initialAmount) : undefined,
            initialConcentration: s.initialConcentration ? parseFloat(s.initialConcentration) : undefined,
        })),
        reactions: reactions.map((r: any): Reaction => ({
            id: r.id,
            name: r.name,
            reactants: extractArray(r.listOfReactants?.speciesReference),
            products: extractArray(r.listOfProducts?.speciesReference),
        })),
        parameters: parameters.map((p: any): Parameter => ({
            id: p.id,
            name: p.name,
            value: p.value ? parseFloat(p.value) : undefined,
            constant: p.constant === 'true',
        })),
    };
}

// Handle possible array or single object
function extractArray<T>(value: T | T[] | undefined): T[] {
    if (value === undefined) return [];
    return Array.isArray(value) ? value : [value];
}
