/**
 * Static checks of a v2 module against interface declarations, with no process code involved.
 *
 * The port of `process_bigraph_lang/v2/check.py`, over the Langium AST: unknown ports, config keys the header
 * does not declare or requires, wires that name no declared store (process-bigraph would create one silently),
 * wire type mismatches against declared store types, paths that escape the root, an `interval` on a step,
 * unknown components, dynamic ports, untyped stores; the writers of each store (additive writers superpose,
 * an overwriting writer next to another is order-dependent, a step publishing an array additively usually
 * meant `overwrite`); units with unit variables bound from the wired stores; `emit` paths; and model sites
 * (a header admitted against a sort). Codes follow `docs/v2/registry-and-authoring.md`.
 */
import type { AstNode } from "langium";
import type {
  V2Composite,
  V2ConfigBlock,
  V2DictLiteral,
  V2Emit,
  V2InnerBlock,
  V2Module,
  V2Node,
  V2NodeDecl,
  V2Path,
  V2Store,
  V2Wire,
  V2WireBlock,
} from "../generated/ast.js";
import {
  isV2Composite,
  isV2CompositeEdge,
  isV2ConfigBlock,
  isV2Emit,
  isV2Index,
  isV2InnerBlock,
  isV2InputsBlock,
  isV2ModelRef,
  isV2Node,
  isV2OutputsBlock,
  isV2Param,
  isV2ParamRef,
  isV2PlainEdge,
  isV2SharedEdge,
  isV2SiteValue,
  isV2Store,
} from "../generated/ast.js";
import {
  type ConfigField,
  type InterfaceDecl,
  MODEL_BLOCKS,
  type ModelDecl,
  Registry,
} from "./headers.js";
import {
  declaredPorts,
  descend,
  type EdgeNode,
  edgeAddress,
  moduleContext,
  type ModuleContext,
  resolveEdge,
  type Step,
} from "./resolve.js";
import {
  containsArray,
  fromAst,
  mapValueType,
  sameType,
  semantics,
  stableJsonText,
  surface,
  type TypeExpr,
  unitsOf,
} from "./types.js";
import { checkUnits, type UnitObligation } from "./units.js";

export type Severity = "error" | "warning" | "info";

export interface Diagnostic {
  code: string;
  slug: string;
  severity: Severity;
  /** the document path, slash-joined, as `fill_sites` spells it */
  path: string;
  message: string;
  node: AstNode;
  property?: string;
}

type Entry =
  | { kind: "store"; node: V2Store }
  | { kind: "node"; node: V2Node }
  | { kind: "edge"; node: EdgeNode };

interface Target {
  absolute: Step[];
  type?: TypeExpr;
  declared: boolean;
}

interface Writer {
  path: Step[];
  node: AstNode;
  kind: string;
  portType?: TypeExpr;
  storeType?: TypeExpr;
}

const SEVERITY_ORDER: Record<Severity, number> = {
  error: 0,
  warning: 1,
  info: 2,
};

export function checkModule(
  module: V2Module,
  registry: Registry = new Registry(),
): Diagnostic[] {
  const checker = new Checker(module, registry);
  checker.run();
  return checker.diagnostics.sort(
    (a, b) =>
      SEVERITY_ORDER[a.severity] - SEVERITY_ORDER[b.severity] ||
      a.path.localeCompare(b.path) ||
      a.code.localeCompare(b.code),
  );
}

export function pathText(path: Step[]): string {
  return path.map(String).join("/");
}

class Checker {
  readonly diagnostics: Diagnostic[] = [];
  private readonly ctx: ModuleContext;
  private readonly paramUnits = new Map<string, string>();
  private index = new Map<string, Entry>();
  private writers = new Map<string, Writer[]>();
  private rootIndex = new Map<string, Entry>();
  private rootWriters = new Map<string, Writer[]>();
  private obligations: UnitObligation[] = [];

  constructor(
    private readonly module: V2Module,
    private readonly registry: Registry,
  ) {
    this.ctx = moduleContext(module);
  }

  run(): void {
    const composites: V2Composite[] = [];
    const emits: V2Emit[] = [];
    for (const statement of this.module.statements) {
      const body = statement.body;
      if (isV2Param(body)) {
        const units = unitsOf(fromAst(body.type));
        if (units !== undefined) this.paramUnits.set(body.name, units);
      } else if (isV2Composite(body)) composites.push(body);
      else if (isV2Emit(body)) emits.push(body);
    }
    for (const composite of composites) this.scope(composite.decls, []);
    this.emitters(emits);
  }

  private report(
    code: string,
    slug: string,
    severity: Severity,
    path: Step[],
    message: string,
    node: AstNode,
    property?: string,
  ): void {
    this.diagnostics.push({
      code,
      slug,
      severity,
      path: pathText(path),
      message,
      node,
      property,
    });
  }

  // --- scopes ----------------------------------------------------------------------------------------------

  private scope(decls: V2NodeDecl[], base: Step[]): void {
    const savedIndex = this.index;
    const savedWriters = this.writers;
    this.index = new Map();
    this.writers = new Map();
    this.indexDecls(decls, []);
    for (const [key, entry] of this.index) {
      const path = fromKey(key);
      if (entry.kind === "edge") this.edge(entry.node, path);
      else if (entry.kind === "store") this.modelSite(entry.node, path);
    }
    this.writerAnalysis();
    if (base.length === 0) {
      this.rootIndex = this.index;
      this.rootWriters = new Map(this.writers);
    }
    for (const [key, entry] of this.index) {
      if (entry.kind === "edge") {
        const inner = entry.node.items.find((item) => isV2InnerBlock(item)) as
          | V2InnerBlock
          | undefined;
        if (inner) this.scope(inner.decls, [...base, ...fromKey(key)]);
      }
    }
    this.index = savedIndex;
    this.writers = savedWriters;
  }

  private indexDecls(decls: V2NodeDecl[], path: Step[]): void {
    for (const decl of decls) {
      const body = decl.body;
      if (isV2Store(body))
        this.index.set(toKey([...path, body.name]), {
          kind: "store",
          node: body,
        });
      else if (isV2Node(body)) {
        this.index.set(toKey([...path, body.name]), {
          kind: "node",
          node: body,
        });
        this.indexDecls(body.decls, [...path, body.name]);
      } else if (
        isV2PlainEdge(body) ||
        isV2SharedEdge(body) ||
        isV2CompositeEdge(body)
      ) {
        this.index.set(toKey([...path, body.name]), {
          kind: "edge",
          node: body,
        });
      }
    }
  }

  // --- edges -----------------------------------------------------------------------------------------------

  private edge(edge: EdgeNode, path: Step[]): void {
    this.obligations = [];
    const kind = isV2PlainEdge(edge)
      ? edge.kind
      : isV2SharedEdge(edge)
      ? "shared_process"
      : "process";
    const decl = this.declaration(edge, path);
    if (
      isV2PlainEdge(edge) &&
      edge.kind === "step" &&
      edge.interval !== undefined
    ) {
      this.report(
        "T130",
        "interval-on-step",
        "error",
        path,
        "a step has no interval; only processes do",
        edge,
        "interval",
      );
    }
    const config = (
      edge.items.find((item) => isV2ConfigBlock(item)) as
        | V2ConfigBlock
        | undefined
    )?.block;
    if (decl) this.config(config, decl, path, edge);
    for (const [label, wires] of this.wireBlocks(edge)) {
      const declared = declaredPorts(edge, label, decl);
      for (const wire of wires.wires) {
        const portPath = [...path, label, wire.port];
        const portType = declared?.[wire.port];
        if (declared && !(wire.port in declared) && !decl?.dynamicPorts) {
          const known = Object.keys(declared).sort().join(", ") || "none";
          this.report(
            "S021",
            "unknown-port",
            "error",
            portPath,
            `${
              decl?.name ?? `'${edgeAddress(edge, this.ctx) ?? "?"}'`
            } has no ${label.slice(0, -1)} port '${
              wire.port
            }' (declared: ${known})`,
            wire,
            "port",
          );
        }
        this.wire(
          wire,
          portType,
          path.slice(0, -1),
          portPath,
          label === "outputs" ? kind : undefined,
          unitsOf(portType),
        );
      }
    }
    if (decl && config) {
      for (const entry of config.entries) {
        const field = decl.config[entry.key];
        if (!field || !isV2ParamRef(entry.value)) continue;
        const fieldUnits = unitsOf(field.type);
        const paramUnits = this.paramUnits.get(paramName(entry.value.value));
        if (fieldUnits !== undefined && paramUnits !== undefined) {
          this.obligations.push({
            path: [...path, "config", entry.key],
            node: entry,
            portUnits: fieldUnits,
            storeUnits: paramUnits,
            store: `param ${paramName(entry.value.value)}`,
          });
        }
      }
    }
    this.units();
  }

  private declaration(edge: EdgeNode, path: Step[]): InterfaceDecl | undefined {
    const resolution = resolveEdge(edge, this.ctx, this.registry);
    switch (resolution.kind) {
      case "open":
        this.report(
          "I300",
          "open-address",
          "info",
          path,
          "the address is an open site; ports are checked against its sort later",
          (edge as { head: AstNode }).head,
        );
        return undefined;
      case "unknown":
        this.report(
          "S020",
          "unknown-component",
          "info",
          path,
          `'${resolution.address}' is not in the registry; its ports and config are not checked`,
          edge,
        );
        return undefined;
      case "inline":
      case "registry":
        if (resolution.decl.dynamicPorts)
          this.report(
            "I210",
            "dynamic-ports",
            "info",
            path,
            `${resolution.decl.name}: ports depend on an instance; only the declared ones are checked`,
            edge,
          );
        return resolution.decl;
      default:
        return undefined;
    }
  }

  private config(
    config: V2DictLiteral | undefined,
    decl: InterfaceDecl,
    path: Step[],
    edge: EdgeNode,
  ): void {
    if (Object.keys(decl.config).length === 0) return;
    const given = new Set((config?.entries ?? []).map((e) => e.key));
    for (const [key, field] of Object.entries(decl.config)) {
      if (!field.hasDefault && !given.has(key))
        this.report(
          "T121",
          "config-missing",
          "error",
          [...path, "config", key],
          `${decl.name} requires config '${key}'`,
          edge,
        );
    }
    for (const entry of config?.entries ?? []) {
      if (!(entry.key in decl.config)) {
        this.report(
          "S022",
          "config-unknown-key",
          "warning",
          [...path, "config", entry.key],
          `${decl.name} has no config '${entry.key}' (declared: ${Object.keys(
            decl.config,
          ).join(", ")})`,
          entry,
          "key",
        );
      }
    }
  }

  private wireBlocks(edge: EdgeNode): ["inputs" | "outputs", V2WireBlock][] {
    const out: ["inputs" | "outputs", V2WireBlock][] = [];
    for (const item of edge.items) {
      if (isV2InputsBlock(item)) out.push(["inputs", item.block]);
      else if (isV2OutputsBlock(item)) out.push(["outputs", item.block]);
    }
    return out;
  }

  // --- wires -----------------------------------------------------------------------------------------------

  private wire(
    wire: V2Wire,
    portType: TypeExpr | undefined,
    parent: Step[],
    portPath: Step[],
    writer: string | undefined,
    units: string | undefined,
  ): void {
    if (wire.block) {
      const element = mapValueType(portType);
      for (const sub of wire.block.wires)
        this.wire(sub, element, parent, [...portPath, sub.port], writer, units);
      return;
    }
    if (!wire.path) return;
    const target = this.resolve(wire.path, parent, portPath, wire);
    if (!target) return;
    const storeText = pathText(target.absolute);
    if (writer !== undefined) {
      const key = toKey(target.absolute);
      const list = this.writers.get(key) ?? [];
      list.push({
        path: portPath,
        node: wire,
        kind: writer,
        portType,
        storeType: target.type,
      });
      this.writers.set(key, list);
    }
    const storeUnits = unitsOf(target.type);
    if (units !== undefined && storeUnits !== undefined) {
      this.obligations.push({
        path: portPath,
        node: wire,
        portUnits: units,
        storeUnits,
        store: storeText,
      });
    }
    if (!target.declared) {
      this.report(
        "W211",
        "store-not-declared",
        "warning",
        portPath,
        `wire names no declared store '${storeText}'; process-bigraph would create it from the port`,
        wire,
        "path",
      );
      return;
    }
    if (!target.type) {
      this.report(
        "I220",
        "store-untyped",
        "info",
        portPath,
        `store '${storeText}' has no declared type; the port type cannot be checked`,
        wire,
        "path",
      );
      return;
    }
    if (portType && !sameType(portType, target.type)) {
      this.report(
        "W200",
        "wire-type-mismatch",
        "warning",
        portPath,
        `port type '${surface(
          portType,
        )}' but store '${storeText}' is declared '${surface(target.type)}'`,
        wire,
        "path",
      );
    }
  }

  private resolve(
    path: V2Path,
    parent: Step[],
    at: Step[],
    node: AstNode,
  ): Target | undefined {
    const absolute: Step[] = [...parent];
    let aboveRoot = false;
    for (const segment of path.segments) {
      if (isV2Index(segment)) absolute.push(segment.index);
      else if (segment.up) {
        if (absolute.length === 0) aboveRoot = true;
        // process-bigraph clamps `..` at the root to the root
        else absolute.pop();
      } else if (segment.star) return undefined;
      else absolute.push(segment.key ?? "");
    }
    if (aboveRoot) {
      this.report(
        "W110",
        "path-above-root",
        "warning",
        at,
        `'${pathSource(
          path,
        )}' goes above the composite root; process-bigraph resolves it from the root`,
        node,
      );
    }
    if (absolute.length === 0) return undefined; // the root itself (`-> ..` from a root edge): nothing to check
    for (let cut = absolute.length; cut > 0; cut--) {
      const entry = this.index.get(toKey(absolute.slice(0, cut)));
      if (!entry) continue;
      const rest = absolute.slice(cut);
      if (entry.kind === "edge") return undefined;
      if (entry.kind === "node") {
        return rest.length === 0
          ? {
              absolute,
              type: entry.node.type ? fromAst(entry.node.type) : undefined,
              declared: true,
            }
          : { absolute, declared: false };
      }
      return { absolute, ...descend(entry.node, rest) };
    }
    return { absolute, declared: false };
  }

  // --- model sites -----------------------------------------------------------------------------------------

  private modelSite(store: V2Store, path: Step[]): void {
    const typeName =
      store.type &&
      store.type.options.length === 1 &&
      store.type.options[0].$type === "V2NamedType"
        ? (store.type.options[0] as { name: string }).name
        : undefined;
    const sort =
      typeName !== undefined ? this.ctx.models.get(typeName) : undefined;
    if (!sort || !sort.isSort) return;
    if (store.value && isV2SiteValue(store.value)) {
      this.report(
        "I301",
        "open-model-site",
        "info",
        path,
        `open model site sorted by ${sort.name}; a model header fills it`,
        store,
        "value",
      );
      return;
    }
    if (!store.value || !isV2ModelRef(store.value)) return;
    const name = store.value.model.$refText;
    const header = this.ctx.models.get(name);
    if (!header || header.isSort) {
      this.report(
        "G300",
        "model-missing",
        "error",
        path,
        `no model header named '${name}'`,
        store,
        "value",
      );
      return;
    }
    this.admitModel(sort, header, path, store);
  }

  private admitModel(
    sort: ModelDecl,
    header: ModelDecl,
    path: Step[],
    node: AstNode,
  ): void {
    this.obligations = [];
    const who = `${header.name} (for sort ${sort.name})`;
    if (sort.timeUnits !== undefined) {
      if (header.timeUnits !== undefined)
        this.obligations.push({
          path: [...path, "time"],
          node,
          portUnits: sort.timeUnits,
          storeUnits: header.timeUnits,
          store: `${header.name}.time`,
        });
      else
        this.report(
          "G301",
          "model-not-admitted",
          "error",
          [...path, "time"],
          `${who}: the sort requires a time unit; the header declares none`,
          node,
        );
    }
    for (const block of MODEL_BLOCKS) {
      const required = sort.blocks[block];
      const provided = header.blocks[block];
      const wildcard = required._;
      for (const [name, field] of Object.entries(required)) {
        if (name === "_") continue;
        if (!(name in provided)) {
          this.report(
            "G301",
            "model-not-admitted",
            "error",
            [...path, block, name],
            `${who}: the sort requires ${block.slice(
              0,
              -1,
            )} '${name}', which the header lacks`,
            node,
          );
          continue;
        }
        this.obligation(
          [...path, block, name],
          field,
          provided[name],
          `${header.name}.${block}.${name}`,
          node,
        );
      }
      if (wildcard)
        for (const [name, field] of Object.entries(provided))
          this.obligation(
            [...path, block, name],
            wildcard,
            field,
            `${header.name}.${block}.${name}`,
            node,
          );
      const extra = Object.keys(provided)
        .filter((k) => !(k in required))
        .sort();
      if (
        Object.keys(required).length > 0 &&
        !wildcard &&
        !sort.openBlocks.has(block) &&
        extra.length > 0
      ) {
        this.report(
          "G301",
          "model-not-admitted",
          "error",
          [...path, block],
          `${who}: the sort admits exactly [${Object.keys(required)
            .sort()
            .join(", ")}]; the header also has [${extra.join(", ")}]`,
          node,
        );
      }
    }
    for (const [key, wanted] of Object.entries(sort.meta)) {
      if (stableJsonText(header.meta[key]) !== stableJsonText(wanted)) {
        this.report(
          "G301",
          "model-not-admitted",
          "error",
          [...path, "meta", key],
          `${who}: the sort requires ${key} = ${stableJsonText(
            wanted,
          )}; the header has ${stableJsonText(header.meta[key])}`,
          node,
        );
      }
    }
    this.units();
  }

  private obligation(
    at: Step[],
    required: ConfigField,
    provided: ConfigField,
    label: string,
    node: AstNode,
  ): void {
    const requiredUnits = unitsOf(required.type);
    const providedUnits = unitsOf(provided.type);
    if (requiredUnits !== undefined && providedUnits !== undefined)
      this.obligations.push({
        path: at,
        node,
        portUnits: requiredUnits,
        storeUnits: providedUnits,
        store: label,
      });
    else if (requiredUnits !== undefined)
      this.report(
        "I232",
        "units-undeclared",
        "info",
        at,
        `${label} declares no units; '${requiredUnits}' cannot be checked`,
        node,
      );
  }

  // --- units -----------------------------------------------------------------------------------------------

  private units(): void {
    for (const finding of checkUnits(this.obligations)) {
      this.report(
        finding.code,
        finding.slug,
        finding.severity,
        finding.obligation.path,
        finding.message,
        finding.obligation.node as AstNode,
      );
    }
    this.obligations = [];
  }

  // --- emit declarations -----------------------------------------------------------------------------------

  private emitters(emits: V2Emit[]): void {
    const saved = this.index;
    this.index = this.rootIndex;
    emits.forEach((emit, index) => {
      for (const path of emit.paths) {
        const at: Step[] = ["emit", index, pathSlash(path)];
        const target = this.resolve(path, [], at, path);
        if (!target) continue;
        if (
          target.absolute.length === 1 &&
          target.absolute[0] === "global_time"
        )
          continue;
        if (!target.declared)
          this.report(
            "W240",
            "emit-path-unknown",
            "warning",
            at,
            `emit path '${pathSource(
              path,
            )}' names no declared store; the emitter would record an empty value`,
            path,
          );
        else if (!this.written(target.absolute))
          this.report(
            "W241",
            "observable-never-written",
            "info",
            at,
            `'${pathSource(
              path,
            )}' is emitted but no edge writes it: it is a constant`,
            path,
          );
      }
    });
    this.index = saved;
  }

  private written(path: Step[]): boolean {
    for (const key of this.rootWriters.keys()) {
      const target = fromKey(key);
      const [shorter, longer] =
        path.length <= target.length ? [path, target] : [target, path];
      if (shorter.every((s, i) => String(longer[i]) === String(s))) return true;
    }
    return false;
  }

  // --- writers ---------------------------------------------------------------------------------------------

  private writerAnalysis(): void {
    for (const key of [...this.writers.keys()].sort()) {
      const writers = this.writers.get(key)!;
      const store = fromKey(key);
      const storeText = pathText(store);
      const storeOverwrite = writers.some(
        (w) => w.storeType && semantics(w.storeType) === "overwrite",
      );
      const kinds = writers.map((w) =>
        storeOverwrite ? "overwrite" : semantics(w.portType),
      );
      writers.forEach((w, i) => {
        if (
          w.kind === "step" &&
          kinds[i] === "accumulate" &&
          w.portType &&
          containsArray(w.portType)
        ) {
          this.report(
            "W223",
            "step-array-accumulates",
            "warning",
            w.path,
            `a step publishes array-typed '${surface(
              w.portType,
            )}' into '${storeText}' with accumulate semantics; a step usually computes a whole value: did you mean overwrite<...>?`,
            w.node,
          );
        }
      });
      if (writers.length < 2) continue;
      const names = writers.map((w) => pathText(w.path)).join(", ");
      if (kinds.includes("overwrite")) {
        this.report(
          "W221",
          "overwrite-conflict",
          "warning",
          store,
          `'${storeText}' is overwritten by one writer and also written by another (${names}): the last update applied wins, so the result depends on scheduling order`,
          writers[0].node,
        );
      } else if (kinds.every((k) => k === "accumulate")) {
        this.report(
          "W220",
          "additive-writers",
          "info",
          store,
          `'${storeText}' is written additively by ${writers.length} processes (${names}): their contributions are summed each tick (simultaneous splitting)`,
          writers[0].node,
        );
      }
    }
  }
}

// --- helpers --------------------------------------------------------------------------------------------------

function toKey(path: Step[]): string {
  return JSON.stringify(path);
}

function fromKey(key: string): Step[] {
  return JSON.parse(key) as Step[];
}

function paramName(text: string): string {
  return text.slice(2, -1);
}

/** `a/b/0`: the form `fill_sites` and CompositeSpec `emitters.paths` use. */
export function pathSlash(path: V2Path): string {
  return path.segments
    .map((s) =>
      isV2Index(s) ? String(s.index) : s.up ? ".." : s.star ? "*" : s.key ?? "",
    )
    .join("/");
}

export function pathSource(path: V2Path): string {
  let text = "";
  let previous: Step | undefined;
  for (const segment of path.segments) {
    if (isV2Index(segment)) text += `[${segment.index}]`;
    else {
      const token = segment.up ? ".." : segment.star ? "*" : segment.key ?? "";
      if (previous === undefined) text += token;
      else if (previous === "..") text += `/${token}`;
      else text += `.${token}`;
      previous = token;
    }
    if (isV2Index(segment)) previous = segment.index;
  }
  return text;
}
