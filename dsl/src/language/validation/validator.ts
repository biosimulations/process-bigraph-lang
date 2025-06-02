import type { ProcessBigraphLanguageServices } from "../process-bigraph-language-module.js";

/**
 * Register custom validation checks.
 */
export function registerValidationChecks(
  services: ProcessBigraphLanguageServices,
) {
  const registry = services.validation.ValidationRegistry;
  const unit_validator = services.validation.UnitValidator;
  const type_validator = services.validation.CustomValidator;
  registry.register({ Unit: unit_validator.checkUnitSymbol }, unit_validator);
  registry.register(
    {
      VarDef: type_validator.checkVarDef,
      Field: type_validator.checkField,
      CallableSignature: type_validator.validateSignature,
      TypeRef: type_validator.validateTypeRef,
      CallExpression: type_validator.validateCallExpression,
      RemoteDef: type_validator.validateRemoteDef,
    },
    type_validator,
  );
}
