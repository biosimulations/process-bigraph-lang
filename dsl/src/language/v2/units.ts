/**
 * Unit consistency with unit variables. A port's units may be an expression with variables (`?U`, `?U/?T`);
 * the variables are bound per instance from the stores the ports are wired to (a variable that only appears in a
 * derived expression is solved for), so a component that works in any consistent unit system is still checked.
 */
import { create, all, type MathJsInstance, type Unit } from "mathjs";

export interface UnitObligation {
  /** the port (or member) the obligation is about; `node` is for the diagnostic range */
  path: (string | number)[];
  node: unknown;
  portUnits: string;
  storeUnits: string;
  store: string;
}

export interface UnitFinding {
  code: string;
  slug: string;
  severity: "warning" | "info";
  obligation: UnitObligation;
  message: string;
}

const UNIT_VAR = /\?([A-Za-z_][A-Za-z0-9_]*)/g;

let math: MathJsInstance | undefined;

function registry(): MathJsInstance {
  if (!math) {
    math = create(all);
    // the vocabulary the headers use that mathjs lacks: molar (with prefixes), counts, dimensionless
    math.createUnit("M", { definition: "1 mol/L", prefixes: "short" });
    math.createUnit("count", "1");
  }
  return math;
}

function parseUnit(text: string): Unit {
  const m = registry();
  const normalized = text.trim() === "dimensionless" ? "1" : text.trim();
  // a bare number (a solved variable substituted by `1`, or `dimensionless`) is a dimensionless unit
  const bare = normalized.replace(/[()\s]/g, "");
  if (/^-?\d+(\.\d+)?$/.test(bare))
    return (m as unknown as { unit(value: number): Unit }).unit(Number(bare));
  return m.unit(1, normalized) as Unit;
}

function substitute(expr: string, bindings: Record<string, string>): string {
  return expr.replace(UNIT_VAR, (whole, name: string) =>
    name in bindings ? `(${bindings[name]})` : whole,
  );
}

function freeVariables(expr: string): string[] {
  const names = new Set<string>();
  for (const match of expr.matchAll(UNIT_VAR)) names.add(match[1]);
  return [...names].sort();
}

function factor(a: Unit, b: Unit): number | undefined {
  if (!a.equalBase(b)) return undefined;
  const m = registry();
  const ratio = m.divide(a, b) as unknown;
  if (typeof ratio === "number") return ratio;
  const asUnit = ratio as Unit;
  try {
    return Number(asUnit.toNumeric());
  } catch {
    return Number(asUnit.toString());
  }
}

/** The units of `?variable` that make `expr` equal `target`, for expressions linear in the variable. */
function solve(
  expr: string,
  variable: string,
  target: string,
): string | undefined {
  try {
    const m = registry();
    // mathjs unit strings cannot contain a bare `1`; `count` is the registered dimensionless unit
    const rest = parseUnit(
      expr.replace(UNIT_VAR, (whole, name: string) =>
        name === variable ? "count" : whole,
      ),
    );
    const wanted = parseUnit(target);
    for (const candidate of [m.divide(wanted, rest), m.divide(rest, wanted)]) {
      const text =
        typeof candidate === "number" ? "1" : (candidate as Unit).formatUnits();
      const trial = parseUnit(substitute(expr, { [variable]: text }));
      const ratio = factor(trial, wanted);
      if (ratio !== undefined && Math.abs(ratio - 1) < 1e-9) return text;
    }
  } catch {
    return undefined;
  }
  return undefined;
}

/** Solve the obligations of one instance and report mismatches (`W201`), unparsable (`I230`) and unbound (`I231`). */
export function checkUnits(obligations: UnitObligation[]): UnitFinding[] {
  const findings: UnitFinding[] = [];
  if (obligations.length === 0) return findings;
  const bindings: Record<string, string> = {};
  let pending = [...obligations];
  for (let round = 0; round <= obligations.length; round++) {
    const still: UnitObligation[] = [];
    for (const ob of pending) {
      const expr = substitute(ob.portUnits, bindings);
      const free = freeVariables(expr);
      if (free.length === 0) findings.push(...compare(ob, expr));
      else if (free.length === 1) {
        const solved = solve(expr, free[0], ob.storeUnits);
        if (solved === undefined) {
          findings.push({
            code: "I231",
            slug: "unit-unresolved",
            severity: "info",
            obligation: ob,
            message: `cannot solve '${ob.portUnits}' for ?${free[0]} from '${ob.storeUnits}'`,
          });
        } else {
          bindings[free[0]] = solved;
          findings.push(...compare(ob, substitute(ob.portUnits, bindings)));
        }
      } else still.push(ob);
    }
    if (still.length === pending.length) {
      for (const ob of still)
        findings.push({
          code: "I231",
          slug: "unit-unresolved",
          severity: "info",
          obligation: ob,
          message: `'${ob.portUnits}' has unbound unit variables; no store pins them`,
        });
      break;
    }
    pending = still;
  }
  return findings;
}

function compare(ob: UnitObligation, expr: string): UnitFinding[] {
  let port: Unit;
  let store: Unit;
  try {
    port = parseUnit(expr);
    store = parseUnit(ob.storeUnits);
  } catch {
    return [
      {
        code: "I230",
        slug: "unit-unparsed",
        severity: "info",
        obligation: ob,
        message: `cannot parse units '${expr}' or '${ob.storeUnits}'`,
      },
    ];
  }
  const ratio = factor(port, store);
  if (ratio === undefined) {
    return [
      {
        code: "W201",
        slug: "unit-mismatch",
        severity: "warning",
        obligation: ob,
        message: `port units '${expr}' are incompatible with store '${ob.store}' in '${ob.storeUnits}'`,
      },
    ];
  }
  if (Math.abs(ratio - 1) > 1e-9) {
    return [
      {
        code: "W201",
        slug: "unit-mismatch",
        severity: "warning",
        obligation: ob,
        message: `port units '${expr}' but store '${ob.store}' is in '${
          ob.storeUnits
        }': convertible, factor ${Number(
          ratio.toPrecision(6),
        )}; insert a conversion or align the units`,
      },
    ];
  }
  return [];
}
