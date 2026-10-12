import {
  type AstNode,
  AstUtils,
  DefaultScopeComputation,
  type LangiumDocument,
} from "langium";
import type { AstNodeDescription } from "langium";

/**
 * Exports every named node of a v2 document, not only the root's direct children: interface and model
 * declarations sit under a `V2Statement` wrapper (which carries their doc comments), and imported names sit
 * under `V2Import`, and edges reference all of them by name.
 */
export class V2ScopeComputation extends DefaultScopeComputation {
  override async computeExports(
    document: LangiumDocument,
  ): Promise<AstNodeDescription[]> {
    const exports: AstNodeDescription[] = [];
    for (const node of AstUtils.streamAllContents(document.parseResult.value)) {
      const name = this.nameProvider.getName(node as AstNode);
      if (name) {
        exports.push(
          this.descriptions.createDescription(node as AstNode, name, document),
        );
      }
    }
    return exports;
  }
}
