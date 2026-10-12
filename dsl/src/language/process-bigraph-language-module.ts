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
  PblangGeneratedModule,
  ProcessBigraphLanguageGeneratedSharedModule,
} from "./generated/module.js";
import { PblangScopeComputation } from "./pblang-scope.js";
import {
  registerChecks,
  WorkspaceRegistry,
  PblangValidator,
} from "./v2/validator.js";
import { PblangHoverProvider } from "./v2/hover.js";
import { PblangCompletionProvider } from "./v2/completion.js";

/** The language's own services: the static checker (headers, wires, writers, units, emit paths, model sites), hover and completion. */
export type PblangAddedServices = {
  validation: {
    HeaderRegistry: WorkspaceRegistry;
    Validator: PblangValidator;
  };
};

export type PblangServices = LangiumServices & PblangAddedServices;

export const PblangModule: Module<
  PblangServices,
  PartialLangiumServices & PblangAddedServices
> = {
  references: {
    ScopeComputation: (services) => new PblangScopeComputation(services),
  },
  validation: {
    HeaderRegistry: (services) => new WorkspaceRegistry(services),
    Validator: (services) =>
      new PblangValidator(services.validation.HeaderRegistry),
  },
  lsp: {
    HoverProvider: (services) => new PblangHoverProvider(services),
    CompletionProvider: (services) => new PblangCompletionProvider(services),
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
  Pblang: PblangServices;
} {
  const shared = inject(
    createDefaultSharedModule(context),
    ProcessBigraphLanguageGeneratedSharedModule,
  );
  const Pblang = inject(
    createDefaultModule({ shared }),
    PblangGeneratedModule,
    PblangModule,
  );
  shared.ServiceRegistry.register(Pblang);
  registerChecks(Pblang);
  if (!context.connection) {
    // We don't run inside a language server
    // Therefore, initialize the configuration provider instantly
    shared.workspace.ConfigurationProvider.initialized({});
  }
  return { shared, Pblang };
}
