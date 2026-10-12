import type { ValidationAcceptor, ValidationChecks } from "langium";
import * as ast from "../generated/ast.js";
import type { PblangServices } from "../process-bigraph-language-module.js";
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
export class WorkspaceRegistry extends Registry {
  constructor(private readonly services: PblangServices) {
    super();
  }

  override lookup(address: string): InterfaceDecl | undefined {
    return super.lookup(address) ?? this.fromWorkspace(address);
  }

  /** Every interface declared in the workspace, with its module (for completion). */
  workspaceInterfaces(): InterfaceDecl[] {
    const out: InterfaceDecl[] = [];
    for (const description of this.services.shared.workspace.IndexManager.allElements(
      "Interface",
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
      "Interface",
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
    const root = document.parseResult.value as ast.Module;
    const node = this.services.workspace.AstNodeLocator.getAstNode(root, path);
    return ast.isInterface(node)
      ? interfaceFromAst(node, root.name)
      : undefined;
  }
}

export class PblangValidator {
  constructor(private readonly registry: WorkspaceRegistry) {}

  checkModule(module: ast.Module, accept: ValidationAcceptor): void {
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

export function registerChecks(services: PblangServices): void {
  const validator = services.validation.Validator;
  const checks: ValidationChecks<ast.ProcessBigraphLanguageAstType> = {
    Module: validator.checkModule,
  };
  services.validation.ValidationRegistry.register(checks, validator);
}
