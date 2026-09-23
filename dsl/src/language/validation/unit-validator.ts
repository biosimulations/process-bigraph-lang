import type { ValidationAcceptor } from "langium";
import type { Unit as ASTUnit } from "../generated/ast.js";
import { unit as MathjsUnit } from "mathjs";

export class UnitValidator {
  checkUnitSymbol(unit: ASTUnit, accept: ValidationAcceptor): void {
    if (unit.name) {
      try {
        if (unit.symbol != null) {
          const mathUnit = MathjsUnit(unit.symbol!);
          if (mathUnit == null) {
            accept(
              "error",
              'Unit ["' +
                unit.symbol! +
                '"] could not be parsed - returned null.',
              { node: unit, property: "symbol" },
            );
          }
        }
      } catch (e) {
        const errorMessage = e instanceof Error ? e.message : String(e);
        accept(
          "error",
          `Unit ["${unit.symbol!}"] could not be parsed: ${errorMessage}`,
          { node: unit, property: "symbol" },
        );
      }
    }
  }
}
