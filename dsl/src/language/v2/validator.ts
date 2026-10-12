import type { ValidationAcceptor, ValidationChecks } from "langium";
import type {
  ProcessBigraphLanguageAstType,
  V2Module,
} from "../generated/ast.js";
import type { PblangV2Services } from "../process-bigraph-language-module.js";
import { checkModule } from "./check.js";
import { Registry } from "./headers.js";

/** The header registry the v2 checks resolve addresses in; the CLI fills it from manifests, the LSP from the workspace (later). */
export class V2Registry extends Registry {}

export class V2Validator {
  constructor(private readonly registry: V2Registry) {}

  checkModule(module: V2Module, accept: ValidationAcceptor): void {
    for (const d of checkModule(module, this.registry)) {
      accept(d.severity, d.message, {
        node: d.node,
        property: d.property,
        code: d.code,
        data: { slug: d.slug, path: d.path },
      });
    }
  }
}

export function registerV2Checks(services: PblangV2Services): void {
  const validator = services.validation.V2Validator;
  const checks: ValidationChecks<ProcessBigraphLanguageAstType> = {
    V2Module: validator.checkModule,
  };
  services.validation.ValidationRegistry.register(checks, validator);
}
