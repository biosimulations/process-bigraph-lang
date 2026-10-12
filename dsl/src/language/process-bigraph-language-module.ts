import { type Module, inject } from "langium";
import {
  createDefaultModule,
  createDefaultSharedModule,
  type DefaultSharedModuleContext,
  type LangiumServices,
  type LangiumSharedServices,
  type PartialLangiumServices,
} from "langium/lsp";
import {
  PblangV2GeneratedModule,
  ProcessBigraphLanguageGeneratedSharedModule,
} from "./generated/module.js";
import { V2ScopeComputation } from "./pblang-v2-scope.js";
import { registerV2Checks, V2Registry, V2Validator } from "./v2/validator.js";
import { V2HoverProvider } from "./v2/hover.js";
import { V2CompletionProvider } from "./v2/completion.js";

/** The language's own services: the static checker (headers, wires, writers, units, emit paths, model sites), hover and completion. */
export type PblangV2AddedServices = {
  validation: {
    V2Registry: V2Registry;
    V2Validator: V2Validator;
  };
};

export type PblangV2Services = LangiumServices & PblangV2AddedServices;

export const PblangV2Module: Module<
  PblangV2Services,
  PartialLangiumServices & PblangV2AddedServices
> = {
  references: {
    ScopeComputation: (services) => new V2ScopeComputation(services),
  },
  validation: {
    V2Registry: (services) => new V2Registry(services),
    V2Validator: (services) => new V2Validator(services.validation.V2Registry),
  },
  lsp: {
    HoverProvider: (services) => new V2HoverProvider(services),
    CompletionProvider: (services) => new V2CompletionProvider(services),
  },
};

/**
 * Create the full set of services required by Langium: the shared services (Langium's defaults plus the
 * generated shared module), then the language's services (Langium's defaults, the generated module and
 * the services above).
 *
 * @param context Optional module context with the LSP connection
 * @returns An object wrapping the shared services and the language-specific services
 */
export function createProcessBigraphLanguageServices(
  context: DefaultSharedModuleContext,
): {
  shared: LangiumSharedServices;
  PblangV2: PblangV2Services;
} {
  const shared = inject(
    createDefaultSharedModule(context),
    ProcessBigraphLanguageGeneratedSharedModule,
  );
  const PblangV2 = inject(
    createDefaultModule({ shared }),
    PblangV2GeneratedModule,
    PblangV2Module,
  );
  shared.ServiceRegistry.register(PblangV2);
  registerV2Checks(PblangV2);
  if (!context.connection) {
    // We don't run inside a language server
    // Therefore, initialize the configuration provider instantly
    shared.workspace.ConfigurationProvider.initialized({});
  }
  return { shared, PblangV2 };
}
