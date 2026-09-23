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
      CallableLiteral: type_validator.validateCallableLiteral,
      TypeRef: type_validator.validateTypeRef,
      ConnectStatement: type_validator.validateConnectStatement,
      RemoteCallableType: type_validator.validateRemoteCallableType,
      StoreDecl: type_validator.checkStoreDecl,
      InitDecl: type_validator.checkInitDecl,
      SiteLiteral: type_validator.checkSiteLiteral,
      MemberCall: type_validator.checkOpenReference,
    },
    type_validator,
  );
}
