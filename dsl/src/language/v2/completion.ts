/**
 * Completion for v2: the names the headers and the composite tree make meaningful where the cursor stands.
 * Port names of the edge's header in `inputs { }` / `outputs { }`; the header's config fields in `config { }`;
 * stores and nodes of the enclosing scope in a wire path (and the keys below a store); interfaces from the
 * registry and the workspace at `process x : |`, inserting the `import` they need; emitter aliases after
 * `emit`. The keyword alternatives of a key (`every`, `process`, ...) are not offered in key positions.
 */
import {
  AstUtils,
  GrammarAST,
  type AstNode,
  type AstNodeDescription,
} from "langium";
import {
  type CompletionAcceptor,
  type CompletionContext,
  type CompletionValueItem,
  DefaultCompletionProvider,
  type NextFeature,
} from "langium/lsp";
import { CompletionItemKind, type TextEdit } from "vscode-languageserver";
import * as ast from "../generated/ast.js";
import type { PblangServices } from "../process-bigraph-language-module.js";
import { type InterfaceDecl, renderField } from "./headers.js";
import {
  declaredPorts,
  type DeclScope,
  EMITTER_ALIASES,
  importedAddress,
  isEdge,
  isEmitPath,
  keysBelow,
  locate,
  moduleContext,
  parentScope,
  resolveEdge,
  rootScope,
  wireSite,
} from "./resolve.js";
import { surface, unitsOf } from "./types.js";

export class PblangCompletionProvider extends DefaultCompletionProvider {
  constructor(private readonly v2: PblangServices) {
    super(v2);
  }

  protected override filterKeyword(
    context: CompletionContext,
    keyword: GrammarAST.Keyword,
  ): boolean {
    // `ast.Key` and `ast.TypeName` admit keywords so that `every = 2` is a legal config key; they are not proposals
    const rule = AstUtils.getContainerOfType(keyword, GrammarAST.isParserRule);
    if (rule?.name === "Keyword") return false;
    return super.filterKeyword(context, keyword);
  }

  protected override completionFor(
    context: CompletionContext,
    next: NextFeature,
    acceptor: CompletionAcceptor,
  ): void | Promise<void> {
    const feature = next.feature;
    if (GrammarAST.isRuleCall(feature) && feature.rule.ref?.name === "ID") {
      switch (next.property) {
        case "port":
          return this.ports(context, acceptor);
        case "key":
          return this.keys(context, acceptor);
        case "alias":
          return this.aliases(context, acceptor);
      }
    }
    // after a trailing comma Langium only proposes the closing brace; offer the block's items again
    if (
      GrammarAST.isKeyword(feature) &&
      feature.value === "}" &&
      afterComma(context)
    ) {
      if (ast.isWireBlock(context.node)) return this.ports(context, acceptor);
      if (ast.isDictLiteral(context.node)) return this.keys(context, acceptor);
    }
    if (GrammarAST.isCrossReference(feature) && next.property === "iface")
      return this.interfaces(context, next, acceptor);
    return super.completionFor(context, next, acceptor);
  }

  // --- ports -----------------------------------------------------------------------------------------------

  private ports(
    context: CompletionContext,
    acceptor: CompletionAcceptor,
  ): void {
    const site = context.node ? wireSite(context.node) : undefined;
    if (!site) return;
    // the chain holds the wire being completed when its port is partly typed; sub-ports of a map are unknown
    const depth = ast.isWire(context.node)
      ? site.chain.length - 1
      : site.chain.length;
    if (depth > 0) return;
    const ctx = moduleContext(moduleOf(context.node!));
    const resolution = resolveEdge(site.edge, ctx, this.registry());
    const decl =
      resolution.kind === "inline" || resolution.kind === "registry"
        ? resolution.decl
        : undefined;
    const ports = declaredPorts(site.edge, site.label, decl);
    if (!ports) return;
    const block = site.edge.items.find((item) =>
      site.label === "inputs"
        ? item.$type === "InputsBlock"
        : item.$type === "OutputsBlock",
    ) as { block: { wires: { port: string }[] } } | undefined;
    const wired = new Set(block?.block.wires.map((w) => w.port) ?? []);
    for (const [name, type] of Object.entries(ports)) {
      const units = unitsOf(type);
      acceptor(context, {
        label: name,
        insertText: keyText(name),
        kind: CompletionItemKind.Field,
        detail: surface(type),
        documentation: `${site.label.slice(0, -1)} port of ${
          decl?.name ?? site.edge.name
        }${units !== undefined ? ` (${units})` : ""}`,
        sortText: wired.has(name) ? `1${name}` : `0${name}`,
      });
    }
  }

  // --- keys: config fields, path segments ------------------------------------------------------------------

  private keys(context: CompletionContext, acceptor: CompletionAcceptor): void {
    const node = context.node;
    if (!node) return;
    if (ast.isDictLiteral(node)) {
      if (ast.isConfigBlock(node.$container))
        this.configKeys(node, context, acceptor);
      return;
    }
    if (ast.isWire(node)) {
      // the first segment of this wire's path
      const site = wireSite(node);
      if (site) this.pathStart(parentScope(site.edge), context, acceptor);
      return;
    }
    if (ast.isEmit(node)) {
      this.pathStart(rootScope(node), context, acceptor);
      return;
    }
    const path = ast.isPath(node)
      ? node
      : ast.isSegment(node)
      ? (node.$container as ast.Path)
      : undefined;
    if (!path) return;
    const scope = isEmitPath(path)
      ? rootScope(path.$container as ast.Emit)
      : pathScope(path);
    // segments that start at or after the token being completed are the one being typed
    const upto = path.segments.filter(
      (s) =>
        s.$cstNode !== undefined && s.$cstNode.offset < context.tokenOffset,
    ).length;
    const located = locate(path, scope, upto);
    if (ast.isStore(located.node)) {
      for (const key of keysBelow(located.node, located.rest))
        acceptor(
          context,
          this.keyItem(key, "key", CompletionItemKind.Property),
        );
    } else if (ast.isNode(located.node))
      this.pathStart(located.node, context, acceptor);
    else if (located.rest.length === 0 && located.scope)
      this.pathStart(located.scope, context, acceptor);
  }

  private pathStart(
    scope: DeclScope | undefined,
    context: CompletionContext,
    acceptor: CompletionAcceptor,
  ): void {
    if (!scope) return;
    for (const decl of scope.decls) {
      const body = decl.body;
      if (ast.isStore(body))
        acceptor(
          context,
          this.keyItem(
            body.name,
            body.type ? `store: ${body.type.$cstNode?.text ?? ""}` : "store",
            CompletionItemKind.Variable,
          ),
        );
      else if (ast.isNode(body))
        acceptor(
          context,
          this.keyItem(body.name, "node", CompletionItemKind.Module),
        );
    }
  }

  private configKeys(
    dict: { entries: { key: string }[]; $container: AstNode },
    context: CompletionContext,
    acceptor: CompletionAcceptor,
  ): void {
    const edge = dict.$container.$container;
    if (!isEdge(edge)) return;
    const ctx = moduleContext(moduleOf(edge));
    const resolution = resolveEdge(edge, ctx, this.registry());
    if (resolution.kind !== "inline" && resolution.kind !== "registry") return;
    const given = new Set(dict.entries.map((e) => e.key));
    for (const [name, field] of Object.entries(resolution.decl.config)) {
      if (given.has(name)) continue;
      acceptor(context, {
        label: name,
        insertText: `${keyText(name)} = `,
        kind: CompletionItemKind.Property,
        detail: renderField(name, field).replace(/;$/, ""),
        documentation:
          field.doc ?? (field.hasDefault ? "optional" : "required"),
        sortText: field.hasDefault ? `1${name}` : `0${name}`,
      });
    }
  }

  private keyItem(
    key: string,
    detail: string,
    kind: CompletionItemKind,
  ): CompletionValueItem {
    return { label: key, insertText: keyText(key), kind, detail };
  }

  // --- interfaces ------------------------------------------------------------------------------------------

  private interfaces(
    context: CompletionContext,
    next: NextFeature,
    acceptor: CompletionAcceptor,
  ): void {
    const module = moduleOf(context.node!);
    const ctx = moduleContext(module);
    const offered = new Set<string>();
    // the names in scope: this module's own interfaces and imports (other documents' exports need an import)
    const documentUri = context.document.uri.toString();
    const local = (candidate: AstNodeDescription): boolean =>
      candidate.documentUri.toString() === documentUri;
    super.completionFor(context, next, (ctx2, item) => {
      if ("nodeDescription" in item && !local(item.nodeDescription)) return;
      if ("nodeDescription" in item) offered.add(item.nodeDescription.name);
      acceptor(ctx2, item);
    });
    for (const decl of this.candidates()) {
      if (offered.has(decl.name) || decl.module === undefined) continue;
      offered.add(decl.name);
      acceptor(context, {
        label: decl.name,
        kind: CompletionItemKind.Class,
        detail: `${decl.kind} from ${decl.module}`,
        documentation: decl.doc,
        additionalTextEdits: importEdit(
          module,
          decl.name,
          decl.module,
          ctx.imports,
        ),
      });
    }
  }

  /** Registry headers (manifests) and the workspace's header files, by module. */
  private candidates(): InterfaceDecl[] {
    const registry = this.registry();
    const out = new Map<string, InterfaceDecl>();
    for (const decl of [...registry.decls, ...registry.workspaceInterfaces()]) {
      if (decl.module === undefined) continue;
      const address = decl.address ?? importedAddress(decl.name, decl.module);
      if (!out.has(address)) out.set(address, decl);
    }
    return [...out.values()];
  }

  // --- emit aliases ----------------------------------------------------------------------------------------

  private aliases(
    context: CompletionContext,
    acceptor: CompletionAcceptor,
  ): void {
    for (const [alias, address] of Object.entries(EMITTER_ALIASES))
      acceptor(context, {
        label: alias,
        kind: CompletionItemKind.EnumMember,
        detail: address,
      });
  }

  private registry() {
    return this.v2.validation.HeaderRegistry;
  }
}

// --- helpers --------------------------------------------------------------------------------------------------

function moduleOf(node: AstNode): ast.Module {
  return AstUtils.getDocument(node).parseResult.value as ast.Module;
}

function pathScope(path: ast.Path): DeclScope | undefined {
  const site = wireSite(path);
  return site ? parentScope(site.edge) : undefined;
}

/** A key that is not an identifier is written as a string. */
function keyText(key: string): string {
  return /^[_a-zA-Z]\w*$/.test(key) ? key : JSON.stringify(key);
}

function afterComma(context: CompletionContext): boolean {
  const before = context.textDocument.getText().slice(0, context.tokenOffset);
  return before.trimEnd().endsWith(",");
}

/** The edit that imports `name` from `module`: into an existing `import module.{...}`, else a new line. */
function importEdit(
  root: ast.Module,
  name: string,
  module: string,
  imports: Map<string, string>,
): TextEdit[] | undefined {
  if (imports.get(name) === module) return undefined;
  const document = AstUtils.getDocument(root).textDocument;
  const existing = root.statements
    .map((s) => s.body)
    .filter((b): b is ast.Import => ast.isImport(b));
  const same = existing.find(
    (i) => i.modulePath !== undefined && i.modulePath.slice(0, -2) === module,
  );
  if (same && same.names.length > 0) {
    const last = same.names[same.names.length - 1].$cstNode;
    if (last) {
      const position = document.positionAt(last.offset + last.length);
      return [
        { range: { start: position, end: position }, newText: `, ${name}` },
      ];
    }
  }
  const line = `import ${module}.{${name}};`;
  const lastImport = existing[existing.length - 1]?.$container.$cstNode;
  if (lastImport) {
    const position = document.positionAt(lastImport.offset + lastImport.length);
    return [
      { range: { start: position, end: position }, newText: `\n${line}` },
    ];
  }
  const start = { line: 0, character: 0 };
  const afterModule =
    root.name !== undefined ? root.$cstNode?.text.indexOf(";") : undefined;
  if (afterModule !== undefined && afterModule >= 0 && root.$cstNode) {
    const position = document.positionAt(
      root.$cstNode.offset + afterModule + 1,
    );
    return [
      { range: { start: position, end: position }, newText: `\n\n${line}` },
    ];
  }
  return [{ range: { start, end: start }, newText: `${line}\n\n` }];
}
