/**
 * What the checker, hover and completion share: the module's declarations (imports, inline headers, models,
 * params), which header an edge is declared by, and how a wire path walks the composite tree.
 */
import type { AstNode } from "langium";
import * as ast from "../generated/ast.js";
import {
  type InterfaceDecl,
  interfaceFromAst,
  isCompositeAddress,
  type ModelDecl,
  modelFromAst,
  normalizeAddress,
  type Registry,
} from "./headers.js";
import {
  arrayDataType,
  fromAst,
  mapValueType,
  type TypeExpr,
} from "./types.js";

export type EdgeNode = ast.PlainEdge | ast.SharedEdge | ast.CompositeEdge;
export type Step = string | number;
/** A scope that holds node declarations: the root composite, a `node`, or a nested composite's body. */
export type DeclScope = ast.Composite | ast.Node | { decls: ast.NodeDecl[] };

export interface ModuleContext {
  module?: string;
  interfaces: Map<string, InterfaceDecl>;
  /** imported name -> module path */
  imports: Map<string, string>;
  models: Map<string, ModelDecl>;
  params: Map<string, ast.Param>;
}

export function moduleContext(module: ast.Module): ModuleContext {
  const ctx: ModuleContext = {
    module: module.name,
    interfaces: new Map(),
    imports: new Map(),
    models: new Map(),
    params: new Map(),
  };
  for (const statement of module.statements) {
    const body = statement.body;
    if (ast.isImport(body)) {
      const path =
        body.modulePath !== undefined
          ? body.modulePath.slice(0, -2)
          : body.module ?? "";
      for (const imported of body.names) ctx.imports.set(imported.name, path);
    } else if (ast.isInterface(body))
      ctx.interfaces.set(body.name, interfaceFromAst(body, module.name));
    else if (ast.isModelDecl(body))
      ctx.models.set(body.name, modelFromAst(body));
    else if (ast.isParam(body)) ctx.params.set(body.name, body);
  }
  return ctx;
}

export function isEdge(node: AstNode | undefined): node is EdgeNode {
  return (
    ast.isPlainEdge(node) || ast.isSharedEdge(node) || ast.isCompositeEdge(node)
  );
}

export function edgeKind(edge: EdgeNode): string {
  return ast.isPlainEdge(edge)
    ? edge.kind
    : ast.isSharedEdge(edge)
    ? "shared process"
    : "composite";
}

export type Resolution =
  | { kind: "inline" | "registry"; decl: InterfaceDecl; address?: string }
  | { kind: "unknown"; address: string }
  | { kind: "open" | "shared" | "composite" | "none" };

/** The header an edge is declared by: an inline interface, an import or a literal address looked up in the registry. */
export function resolveEdge(
  edge: EdgeNode,
  ctx: ModuleContext,
  registry: Registry,
): Resolution {
  if (ast.isCompositeEdge(edge)) return { kind: "composite" };
  const head = edge.head;
  if (head.sharedRef !== undefined) return { kind: "shared" };
  if (head.address?.site) return { kind: "open" };
  const name = head.iface?.$refText;
  if (name !== undefined && ctx.interfaces.has(name))
    return { kind: "inline", decl: ctx.interfaces.get(name)! };
  const address = edgeAddress(edge, ctx);
  if (address === undefined || isCompositeAddress(address))
    return { kind: "none" };
  const decl = registry.lookup(address);
  return decl
    ? { kind: "registry", decl, address }
    : { kind: "unknown", address };
}

/** The normalized address an edge names, through its import or its literal. */
export function edgeAddress(
  edge: EdgeNode,
  ctx: ModuleContext,
): string | undefined {
  if (ast.isCompositeEdge(edge))
    return edge.address !== undefined
      ? normalizeAddress(edge.address)
      : "local:Composite";
  const head = edge.head;
  const name = head.iface?.$refText;
  if (name !== undefined && ctx.interfaces.has(name))
    return ctx.interfaces.get(name)!.address;
  if (name !== undefined && ctx.imports.has(name))
    return importedAddress(name, ctx.imports.get(name)!);
  if (head.address?.literal !== undefined)
    return normalizeAddress(head.address.literal);
  return undefined;
}

export function importedAddress(name: string, module: string): string {
  return `local:!${module}.${name}`;
}

/** The ports an edge's `inputs`/`outputs` block is checked against: its own `ports { }` override, else the header's. */
export function declaredPorts(
  edge: EdgeNode,
  label: "inputs" | "outputs",
  decl: InterfaceDecl | undefined,
): Record<string, TypeExpr> | undefined {
  const ports = edge.items.find((item) => ast.isPortsBlock(item)) as
    | ast.PortsBlock
    | undefined;
  const own = ports ? ports[label] : [];
  if (own.length > 0) {
    const out: Record<string, TypeExpr> = {};
    for (const field of own) out[field.name] = fromAst(field.type);
    return out;
  }
  return decl?.[label];
}

// --- the composite tree ----------------------------------------------------------------------------------------

/** The scope whose declarations a wire path of this edge is relative to (the edge's parent). */
export function parentScope(edge: EdgeNode): DeclScope | undefined {
  return scopeOf(edge.$container);
}

export function scopeOf(node: AstNode | undefined): DeclScope | undefined {
  for (let n: AstNode | undefined = node; n; n = n.$container) {
    if (ast.isComposite(n) || ast.isNode(n) || ast.isInnerBlock(n)) return n;
  }
  return undefined;
}

/** The root composite an `emit` declaration's paths are relative to: the module's first composite. */
export function rootScope(emit: ast.Emit): DeclScope | undefined {
  const module = emit.$container.$container as ast.Module;
  for (const statement of module.statements)
    if (ast.isComposite(statement.body)) return statement.body;
  return undefined;
}

export interface Located {
  /** the store or node the path reaches, when it names a declared one */
  node?: ast.Store | ast.Node;
  /** the remaining steps below that store (dict keys, indices), or the whole path when nothing was declared */
  rest: Step[];
  scope?: DeclScope;
}

/**
 * Walk a path from a scope: `..` climbs to the enclosing scope (clamped at a composite body, as process-bigraph
 * clamps at the root), keys descend into `node` bodies, and the first `store` reached ends the walk.
 */
export function locate(
  path: ast.Path,
  scope: DeclScope | undefined,
  upto: number = path.segments.length,
): Located {
  let current = scope;
  const steps: Step[] = [];
  for (const segment of path.segments.slice(0, upto)) {
    if (ast.isIndex(segment)) steps.push(segment.index);
    else if (segment.up) {
      if (steps.length > 0) steps.pop();
      else current = enclosingScope(current);
    } else if (segment.star) return { rest: [] };
    else steps.push(segment.key ?? "");
  }
  return descendScope(current, steps);
}

export function descendScope(
  scope: DeclScope | undefined,
  steps: Step[],
): Located {
  let current = scope;
  for (let i = 0; i < steps.length; i++) {
    const step = steps[i];
    if (!current || typeof step === "number") return { rest: steps, scope };
    const decl = declIn(current, step);
    if (ast.isNode(decl)) current = decl;
    else if (ast.isStore(decl))
      return { node: decl, rest: steps.slice(i + 1), scope };
    else return { rest: steps, scope };
  }
  return ast.isNode(current)
    ? { node: current, rest: [], scope }
    : { rest: steps, scope };
}

function enclosingScope(scope: DeclScope | undefined): DeclScope | undefined {
  if (!scope || !ast.isNode(scope)) return scope; // a composite body is a root: `..` stays there
  return scopeOf(scope.$container) ?? scope;
}

export function declIn(
  scope: DeclScope,
  key: string,
): ast.Store | ast.Node | EdgeNode | undefined {
  for (const decl of scope.decls) {
    const body = decl.body;
    if (
      (ast.isStore(body) || ast.isNode(body) || isEdge(body)) &&
      body.name === key
    )
      return body;
  }
  return undefined;
}

/** The type at the end of a path into a store: through dict entries of its value and the type's fields. */
export function descend(
  store: ast.Store,
  rest: Step[],
): { type?: TypeExpr; declared: boolean } {
  let type: TypeExpr | undefined = store.type ? fromAst(store.type) : undefined;
  if (!type && store.value && ast.isSiteValue(store.value) && store.value.sort)
    type = fromAst(store.value.sort);
  let value: ast.Value | undefined = store.value;
  for (const step of rest) {
    if (typeof step === "number") {
      type = arrayDataType(type);
      value = undefined;
      continue;
    }
    if (value && ast.isDictLiteral(value)) {
      const entry = value.entries.find((e) => e.key === step);
      if (!entry) return { declared: false };
      value = entry.value;
    } else if (
      value &&
      !ast.isArrayLiteral(value) &&
      !ast.isListLiteral(value)
    ) {
      return { declared: false };
    }
    type =
      type && type.kind === "struct" ? type.fields[step] : mapValueType(type);
  }
  return { type, declared: true };
}

/** The keys a path may continue with below a store: its dict value's keys, else its struct type's fields. */
export function keysBelow(store: ast.Store, rest: Step[]): string[] {
  let value: ast.Value | undefined = store.value;
  let type: TypeExpr | undefined = store.type ? fromAst(store.type) : undefined;
  for (const step of rest) {
    if (typeof step === "number") {
      value = undefined;
      type = arrayDataType(type);
      continue;
    }
    value =
      value && ast.isDictLiteral(value)
        ? value.entries.find((e) => e.key === step)?.value
        : undefined;
    type =
      type && type.kind === "struct" ? type.fields[step] : mapValueType(type);
  }
  if (value && ast.isDictLiteral(value)) return value.entries.map((e) => e.key);
  if (type && type.kind === "struct") return Object.keys(type.fields);
  return [];
}

export function isEmitPath(path: ast.Path): boolean {
  return ast.isEmit(path.$container);
}

export const EMITTER_ALIASES: Record<string, string> = {
  ram: "local:RAMEmitter",
  parquet: "local:ParquetEmitter",
  sqlite: "local:SQLiteEmitter",
  xarray: "local:XarrayEmitter",
  console: "local:ConsoleEmitter",
  json: "local:JSONEmitter",
};

/** The `inputs`/`outputs` block a wire sits in, its edge, and the wire's nesting (ports of ports below a map). */
export function wireSite(
  node: AstNode,
):
  | { edge: EdgeNode; label: "inputs" | "outputs"; chain: string[] }
  | undefined {
  const chain: string[] = [];
  for (let n: AstNode | undefined = node; n; n = n.$container) {
    if (ast.isWire(n)) chain.unshift(n.port);
    else if (ast.isInputsBlock(n) || ast.isOutputsBlock(n)) {
      const edge = n.$container;
      if (!isEdge(edge)) return undefined;
      return {
        edge,
        label: ast.isInputsBlock(n) ? "inputs" : "outputs",
        chain,
      };
    }
  }
  return undefined;
}
