/**
 * Hover for v2: what a name means where it stands. An edge shows its header; a port shows its declared type
 * and the store it is wired to; a path segment shows the store or node it names; a config key shows the
 * header's field; stores, nodes, params, models and emit aliases show their declaration and docs.
 */
import { AstUtils, CstUtils, GrammarAST, type LangiumDocument } from "langium";
import type { AstNode, LeafCstNode } from "langium";
import { AstNodeHoverProvider } from "langium/lsp";
import type { Hover, HoverParams } from "vscode-languageserver";
import type {
  V2Emit,
  V2Module,
  V2NodeDecl,
  V2Path,
  V2Store,
  V2Wire,
} from "../generated/ast.js";
import {
  isV2CompositeEdge,
  isV2ConfigBlock,
  isV2DictLiteral,
  isV2EdgeHead,
  isV2Emit,
  isV2Entry,
  isV2Field,
  isV2ImportedName,
  isV2Interface,
  isV2ModelDecl,
  isV2ModelRef,
  isV2Node,
  isV2NodeDecl,
  isV2Param,
  isV2ParamRef,
  isV2Path,
  isV2PlainEdge,
  isV2Segment,
  isV2Store,
  isV2Wire,
} from "../generated/ast.js";
import type { PblangV2Services } from "../process-bigraph-language-module.js";
import {
  docText,
  type InterfaceDecl,
  type ModelDecl,
  modelFromAst,
  renderField,
  renderInterface,
} from "./headers.js";
import {
  declaredPorts,
  descend,
  type DeclScope,
  type EdgeNode,
  edgeAddress,
  edgeKind,
  EMITTER_ALIASES,
  isEdge,
  isEmitPath,
  locate,
  type Located,
  moduleContext,
  type ModuleContext,
  parentScope,
  resolveEdge,
  rootScope,
  wireSite,
} from "./resolve.js";
import { mapValueType, surface, type TypeExpr, unitsOf } from "./types.js";

export class V2HoverProvider extends AstNodeHoverProvider {
  constructor(private readonly services: PblangV2Services) {
    super(services);
  }

  override getHoverContent(
    document: LangiumDocument,
    params: HoverParams,
  ): Hover | undefined {
    const root = document.parseResult.value.$cstNode;
    if (!root) return undefined;
    const offset = document.textDocument.offsetAt(params.position);
    const leaf = CstUtils.findLeafNodeAtOffset(root, offset);
    if (!leaf || leaf.hidden) return undefined;
    const value = this.hoverAt(leaf);
    return value
      ? { contents: { kind: "markdown", value }, range: leaf.range }
      : undefined;
  }

  protected getAstNodeHoverContent(node: AstNode): Hover | undefined {
    const value = this.describe(node, undefined);
    return value ? { contents: { kind: "markdown", value } } : undefined;
  }

  private hoverAt(leaf: LeafCstNode): string | undefined {
    const node = leaf.astNode;
    return this.describe(node, propertyOf(leaf), leaf);
  }

  private describe(
    node: AstNode,
    property: string | undefined,
    leaf?: LeafCstNode,
  ): string | undefined {
    const ctx = moduleContext(
      AstUtils.getDocument(node).parseResult.value as V2Module,
    );
    if (isV2EdgeHead(node)) {
      if (property === "sharedRef") return undefined;
      return this.edge(node.$container as EdgeNode, ctx);
    }
    if (isEdge(node)) return this.edge(node, ctx);
    if (isV2Wire(node) && property === "port") return this.port(node, ctx);
    if (isV2Segment(node) && property === "key" && leaf)
      return this.segment(node.$container as V2Path, node.$containerIndex ?? 0);
    if (isV2Path(node) && leaf) return this.pathLeaf(node, leaf);
    if (isV2Entry(node) && property === "key") return this.configKey(node, ctx);
    if (isV2Store(node) || isV2Node(node)) return this.declaration(node);
    if (isV2Interface(node))
      return this.interface(ctx.interfaces.get(node.name));
    if (isV2ImportedName(node)) return this.imported(node.name, ctx);
    if (isV2ModelDecl(node)) return this.model(modelFromAst(node));
    if (isV2ModelRef(node)) {
      const decl = node.model.ref;
      return decl ? this.model(modelFromAst(decl)) : undefined;
    }
    if (isV2Param(node)) return this.param(node.name, ctx);
    if (isV2ParamRef(node)) return this.param(node.value.slice(2, -1), ctx);
    if (isV2Emit(node) && property === "alias") return this.emit(node);
    if (isV2Field(node)) {
      const doc = docText(node.docs);
      return (
        code(
          renderField(node.name, {
            type: undefined,
            hasDefault: node.default !== undefined,
          }).replace("any", node.type.$cstNode?.text ?? "any"),
        ) + (doc ? `\n\n${doc}` : "")
      );
    }
    return undefined;
  }

  // --- edges and headers -----------------------------------------------------------------------------------

  private edge(edge: EdgeNode, ctx: ModuleContext): string {
    const head = edgeHeadText(edge);
    const docs = docsOf(edge);
    const parts = [`**${edgeKind(edge)}** \`${edge.name}\`${head}`];
    const resolution = resolveEdge(edge, ctx, this.registry());
    const address = edgeAddress(edge, ctx);
    switch (resolution.kind) {
      case "inline":
      case "registry":
        parts.push(this.interface(resolution.decl) ?? "");
        break;
      case "unknown":
        parts.push(
          `\`${resolution.address}\` is not in the registry: ports and config are not checked`,
        );
        break;
      case "open":
        parts.push("open address site: filled by a template binding");
        break;
      case "shared":
        parts.push(
          `shares the process \`${
            (edge as { head: { sharedRef?: string } }).head.sharedRef ?? ""
          }\``,
        );
        break;
      default:
        if (address !== undefined) parts.push(`address \`${address}\``);
    }
    if (docs) parts.push(docs);
    return parts.filter((p) => p.length > 0).join("\n\n");
  }

  private interface(decl: InterfaceDecl | undefined): string | undefined {
    if (!decl) return undefined;
    const parts = [code(renderInterface(decl))];
    if (decl.module !== undefined) parts.push(`from \`${decl.module}\``);
    if (decl.dynamicPorts)
      parts.push(
        "ports depend on the instance: only the declared ones are checked",
      );
    if (decl.doc) parts.push(decl.doc);
    return parts.join("\n\n");
  }

  private imported(name: string, ctx: ModuleContext): string | undefined {
    const module = ctx.imports.get(name);
    if (module === undefined) return undefined;
    const decl = this.registry().lookup(`local:!${module}.${name}`);
    return (
      this.interface(decl) ??
      `\`${name}\` from \`${module}\`: not in the registry, so its ports and config are not checked`
    );
  }

  private configKey(
    entry: { key: string; $container: AstNode },
    ctx: ModuleContext,
  ): string | undefined {
    const dict = entry.$container;
    if (!isV2DictLiteral(dict) || !isV2ConfigBlock(dict.$container))
      return undefined;
    const edge = dict.$container.$container;
    if (!isEdge(edge)) return undefined;
    const resolution = resolveEdge(edge, ctx, this.registry());
    if (resolution.kind !== "inline" && resolution.kind !== "registry")
      return undefined;
    const field = resolution.decl.config[entry.key];
    if (!field)
      return `\`${entry.key}\` is not a config field of ${resolution.decl.name}`;
    const parts = [
      `**config** ${code(renderField(entry.key, field))}`,
      `of ${resolution.decl.name}`,
    ];
    if (field.doc) parts.push(field.doc);
    return parts.join("\n\n");
  }

  // --- wires -----------------------------------------------------------------------------------------------

  private port(wire: V2Wire, ctx: ModuleContext): string | undefined {
    const site = wireSite(wire);
    if (!site) return undefined;
    const resolution = resolveEdge(site.edge, ctx, this.registry());
    const decl =
      resolution.kind === "inline" || resolution.kind === "registry"
        ? resolution.decl
        : undefined;
    const ports = declaredPorts(site.edge, site.label, decl);
    let type: TypeExpr | undefined = ports?.[site.chain[0]];
    for (const _ of site.chain.slice(1)) type = mapValueType(type);
    const label = site.label.slice(0, -1);
    const typeText = type ? `: \`${surface(type)}\`` : "";
    const parts = [
      `**${label} port** \`${site.chain.join(".")}\`${typeText} of \`${
        decl?.name ?? site.edge.name
      }\``,
    ];
    if (
      type === undefined &&
      ports &&
      !decl?.dynamicPorts &&
      site.chain.length === 1
    )
      parts.push(`not a declared ${label} port`);
    if (wire.path) {
      const target = this.target(wire.path, parentScope(site.edge));
      if (target) parts.push(`wired to ${target}`);
    }
    return parts.join("\n\n");
  }

  private segment(path: V2Path, index: number): string | undefined {
    const scope = isEmitPath(path)
      ? rootScope(path.$container as V2Emit)
      : scopeOfPath(path);
    return this.target(path, scope, index + 1);
  }

  private pathLeaf(path: V2Path, leaf: LeafCstNode): string | undefined {
    // an index `[0]` or a separator: describe the path up to and including this token
    let upto = 0;
    for (const segment of path.segments) {
      const cst = segment.$cstNode;
      if (cst && cst.offset + cst.length <= leaf.offset + leaf.length) upto++;
    }
    const scope = isEmitPath(path)
      ? rootScope(path.$container as V2Emit)
      : scopeOfPath(path);
    return this.target(path, scope, upto);
  }

  private target(
    path: V2Path,
    scope: DeclScope | undefined,
    upto?: number,
  ): string | undefined {
    const located: Located = locate(path, scope, upto);
    if (isV2Node(located.node))
      return `**node** \`${located.node.name}\`${
        located.node.type ? `: \`${located.node.type.$cstNode?.text}\`` : ""
      }`;
    if (isV2Store(located.node)) {
      const store = located.node;
      const below = located.rest;
      const { type, declared } = descend(store, below);
      const name = [store.name, ...below.map(String)].join("/");
      if (!declared) return `\`${name}\`: not a key of store \`${store.name}\``;
      const typeText = type ? `: \`${surface(type)}\`` : " (untyped)";
      const units = unitsOf(type);
      const parts = [`**store** \`${name}\`${typeText}`];
      if (units !== undefined) parts.push(`units \`${units}\``);
      if (below.length === 0) parts.push(declarationLine(store));
      const docs = docsOf(store);
      if (docs) parts.push(docs);
      return parts.join("\n\n");
    }
    if (located.rest.length === 0 && located.scope)
      return isV2Node(located.scope)
        ? `**node** \`${located.scope.name}\``
        : "the composite root";
    return `\`${located.rest
      .map(String)
      .join(
        "/",
      )}\`: no declared store; process-bigraph would create it from the port`;
  }

  // --- declarations ----------------------------------------------------------------------------------------

  private declaration(
    node: V2Store | ({ name: string; type?: AstNode } & AstNode),
  ): string {
    const parts: string[] = [];
    if (isV2Store(node)) {
      const type = node.type?.$cstNode?.text;
      parts.push(
        `**store** \`${node.name}\`${type ? `: \`${type}\`` : " (untyped)"}`,
      );
      parts.push(declarationLine(node));
    } else {
      const type = (node as { type?: AstNode }).type?.$cstNode?.text;
      parts.push(`**node** \`${node.name}\`${type ? `: \`${type}\`` : ""}`);
    }
    const docs = docsOf(node);
    if (docs) parts.push(docs);
    return parts.join("\n\n");
  }

  private param(name: string, ctx: ModuleContext): string | undefined {
    const param = ctx.params.get(name);
    if (!param) return `\`\${${name}}\`: no \`param ${name}\` is declared`;
    const parts = [code(param.$cstNode?.text ?? `param ${name};`)];
    const docs = docsOf(param);
    if (docs) parts.push(docs);
    return parts.join("\n\n");
  }

  private model(decl: ModelDecl): string {
    const kind = decl.isSort ? "model sort" : "model header";
    const parts = [
      `**${kind}** \`${decl.name}\`${
        decl.source !== undefined ? ` from \`${decl.source}\`` : ""
      }`,
    ];
    const summary: string[] = [];
    if (decl.timeUnits !== undefined)
      summary.push(`time in \`${decl.timeUnits}\``);
    for (const block of ["compartments", "species", "parameters"] as const) {
      const names = Object.keys(decl.blocks[block]).filter((n) => n !== "_");
      const open = decl.openBlocks.has(block) || "_" in decl.blocks[block];
      if (names.length > 0 || open)
        summary.push(`${names.length}${open ? "+" : ""} ${block}`);
    }
    if (summary.length > 0) parts.push(summary.join(", "));
    return parts.join("\n\n");
  }

  private emit(emit: V2Emit): string | undefined {
    if (emit.alias === undefined) return undefined;
    const address = EMITTER_ALIASES[emit.alias];
    return address
      ? `**emitter** \`${emit.alias}\` is \`${address}\``
      : `unknown emitter alias \`${emit.alias}\` (known: ${Object.keys(
          EMITTER_ALIASES,
        ).join(", ")})`;
  }

  private registry() {
    return this.services.validation.V2Registry;
  }
}

// --- helpers --------------------------------------------------------------------------------------------------

/** The assignment property the leaf's token belongs to (`port` for a wire's port, `name` for a store's name). */
export function propertyOf(leaf: LeafCstNode): string | undefined {
  const node = leaf.astNode;
  for (
    let cst: LeafCstNode | import("langium").CompositeCstNode | undefined =
      leaf;
    cst;
    cst = cst.container
  ) {
    if (cst.astNode !== node) break;
    const assignment = AstUtils.getContainerOfType(
      cst.grammarSource,
      GrammarAST.isAssignment,
    );
    if (assignment) return assignment.feature;
  }
  return undefined;
}

function scopeOfPath(path: V2Path): DeclScope | undefined {
  const site = wireSite(path);
  return site ? parentScope(site.edge) : undefined;
}

function docsOf(node: AstNode): string | undefined {
  const container = node.$container;
  if (isV2NodeDecl(container)) return docText((container as V2NodeDecl).docs);
  if (container && "docs" in container)
    return docText((container as { docs: string[] }).docs);
  return undefined;
}

function declarationLine(store: V2Store): string {
  const text = store.$cstNode?.text ?? `store ${store.name};`;
  const first = text.split("\n")[0];
  return code(first.length < text.length ? `${first} ...` : first);
}

function edgeHeadText(edge: EdgeNode): string {
  if (isV2CompositeEdge(edge)) return "";
  const head = edge.head;
  const parts: string[] = [];
  if (head.sharedRef !== undefined) parts.push(`: shared ${head.sharedRef}`);
  else if (head.iface) parts.push(`: ${head.iface.$refText}`);
  if (head.address?.literal !== undefined)
    parts.push(`at ${JSON.stringify(head.address.literal)}`);
  if (isV2PlainEdge(edge) && edge.interval)
    parts.push(`every ${edge.interval.$cstNode?.text ?? ""}`);
  return parts.length > 0 ? ` ${parts.join(" ")}` : "";
}

function code(text: string): string {
  return `\`\`\`pblang\n${text}\n\`\`\``;
}
