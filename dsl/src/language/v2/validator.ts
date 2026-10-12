import type { ValidationAcceptor, ValidationChecks } from "langium";
import type {
  ProcessBigraphLanguageAstType,
  V2Module,
} from "../generated/ast.js";
import { isV2Interface } from "../generated/ast.js";
import type { PblangV2Services } from "../process-bigraph-language-module.js";
import { checkModule } from "./check.js";
import {
  type InterfaceDecl,
  interfaceFromAst,
  Registry,
  shortName,
} from "./headers.js";
import { importedAddress } from "./resolve.js";

/**
 * The header registry the v2 checks resolve addresses in. The CLI fills it from manifests; in the editor the
 * header files open in the workspace answer too: a `.pbl` with `module a.b;` declaring `X` is `local:!a.b.X`.
 */
export class V2Registry extends Registry {
  constructor(private readonly services: PblangV2Services) {
    super();
  }

  override lookup(address: string): InterfaceDecl | undefined {
    return super.lookup(address) ?? this.fromWorkspace(address);
  }

  /** Every interface declared in the workspace, with its module (for completion). */
  workspaceInterfaces(): InterfaceDecl[] {
    const out: InterfaceDecl[] = [];
    for (const description of this.services.shared.workspace.IndexManager.allElements(
      "V2Interface",
    )) {
      const decl = this.declOf(description.documentUri, description.path);
      if (decl) out.push(decl);
    }
    return out;
  }

  private fromWorkspace(address: string): InterfaceDecl | undefined {
    if (!address.startsWith("local:")) return undefined;
    const name = shortName(address);
    const byName: InterfaceDecl[] = [];
    for (const description of this.services.shared.workspace.IndexManager.allElements(
      "V2Interface",
    )) {
      if (description.name !== name) continue;
      const decl = this.declOf(description.documentUri, description.path);
      if (!decl) continue;
      if (decl.address === address) return decl;
      if (
        decl.address === undefined &&
        decl.module !== undefined &&
        importedAddress(name, decl.module) === address
      )
        byName.push(decl);
    }
    return byName.length === 1 ? byName[0] : undefined;
  }

  private declOf(
    uri: import("langium").URI,
    path: string,
  ): InterfaceDecl | undefined {
    const document =
      this.services.shared.workspace.LangiumDocuments.getDocument(uri);
    if (!document) return undefined;
    const root = document.parseResult.value as V2Module;
    const node = this.services.workspace.AstNodeLocator.getAstNode(root, path);
    return isV2Interface(node) ? interfaceFromAst(node, root.name) : undefined;
  }
}

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
