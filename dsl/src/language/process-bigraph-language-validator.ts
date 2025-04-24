import type { ValidationAcceptor, ValidationChecks } from "langium";
import type {
  ProcessBigraphLanguageAstType,
  Unit as ASTUnit,
} from "./generated/ast.js";
import type { ProcessBigraphLanguageServices } from "./process-bigraph-language-module.js";
import { unit as MathjsUnit } from "mathjs";

/**
 * Register custom validation checks.
 */
export function registerValidationChecks(
  services: ProcessBigraphLanguageServices,
) {
  const registry = services.validation.ValidationRegistry;
  const validator = services.validation.ProcessBigraphLanguageValidator;
  const checks: ValidationChecks<ProcessBigraphLanguageAstType> = {
    Unit: validator.checkUnitSymbol,
  };
  registry.register(checks, validator);
}

/**
 * Implementation of custom validations.
 */
export class ProcessBigraphLanguageValidator {
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
