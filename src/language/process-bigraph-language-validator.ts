import type { ValidationAcceptor, ValidationChecks } from 'langium';
import type { ProcessBigraphLanguageAstType, Type } from './generated/ast.js';
import type { ProcessBigraphLanguageServices } from './process-bigraph-language-module.js';

/**
 * Register custom validation checks.
 */
export function registerValidationChecks(services: ProcessBigraphLanguageServices) {
    const registry = services.validation.ValidationRegistry;
    const validator = services.validation.ProcessBigraphLanguageValidator;
    const checks: ValidationChecks<ProcessBigraphLanguageAstType> = {
        Type: validator.checkPersonStartsWithCapital
    };
    registry.register(checks, validator);
}

/**
 * Implementation of custom validations.
 */
export class ProcessBigraphLanguageValidator {

    checkPersonStartsWithCapital(type: Type, accept: ValidationAcceptor): void {
        // if (type.name) {
        //     const firstChar = type.name.substring(0, 1);
        //     if (firstChar.toUpperCase() !== firstChar) {
        //         accept('hint', 'Type name should start with a capital.', { node: type, property: 'name' });
        //     }
        // }
    }

}
