/**
 * The Langium AST -> the v2 model (the first half of `compile`). Imports resolve against the registry (and
 * against the interfaces declared in the text); `${name}` strings become parameter references once the params
 * are known; emitter aliases become addresses.
 */
import type {
  V2Address,
  V2CompositeEdge,
  V2CompositeItem,
  V2DictLiteral,
  V2EdgeHead,
  V2Emit,
  V2Field,
  V2Interface,
  V2ModelDecl,
  V2Module,
  V2NodeDecl,
  V2Param,
  V2Path,
  V2PlainEdge,
  V2Scalar,
  V2SharedEdge,
  V2Store,
  V2Value,
  V2WireBlock,
} from "../generated/ast.js";
import {
  isV2ArrayLiteral,
  isV2BoolLiteral,
  isV2BridgeBlock,
  isV2Composite,
  isV2CompositeEdge,
  isV2ConfigBlock,
  isV2DictLiteral,
  isV2Emit,
  isV2ExtraBlock,
  isV2FileLiteral,
  isV2FloatLiteral,
  isV2Import,
  isV2Index,
  isV2InnerBlock,
  isV2InputsBlock,
  isV2Interface,
  isV2InterfaceBlock,
  isV2IntLiteral,
  isV2ListLiteral,
  isV2Meta,
  isV2ModelDecl,
  isV2ModelRef,
  isV2Node,
  isV2NullLiteral,
  isV2Options,
  isV2OptionsBlock,
  isV2OutputsBlock,
  isV2Param,
  isV2ParamRef,
  isV2PlainEdge,
  isV2PortsBlock,
  isV2SchemaBlock,
  isV2SharedEdge,
  isV2SiteValue,
  isV2Store,
  isV2StringLiteral,
  isV2TupleLiteral,
} from "../generated/ast.js";
import {
  docText,
  type InterfaceDecl,
  interfaceFromAst,
  modelFromAst,
  type Registry,
} from "./headers.js";
import {
  type Composite,
  type Dict,
  type Document,
  type Edge,
  type Element,
  type ExternalRef,
  type Face,
  isDict,
  isSite,
  MISSING,
  type NdArray,
  newComposite,
  newDocument,
  newEdge,
  type Node,
  PARAM_FULL,
  PARAM_INLINE,
  type ParamRef,
  parseAddress,
  type Path,
  type Site,
  type Store,
  type Wire,
} from "./model.js";
import { pathToDocument, wireToDocument } from "./paths.js";
import { EMITTER_ALIASES } from "./printer.js";
import {
  fromAst,
  type Named,
  type Raw,
  toBigraph,
  type TypeExpr,
} from "./types.js";

const ALIAS_ADDRESSES: Record<string, string> = Object.fromEntries(
  Object.entries(EMITTER_ALIASES).map(([name, alias]) => [
    alias,
    `local:${name}`,
  ]),
);

/** A `?` without `as`: the sort comes from the store's type, the edge's face, or defaults to `node`. */
const UNSORTED: Named = { kind: "named", name: "__unsorted__", args: [] };

export function bindModule(module: V2Module, registry?: Registry): Document {
  return new Binder(registry).module(module);
}

class Binder {
  private readonly document = newDocument();
  private readonly imports = new Map<string, string>(); // interface name -> module
  private readonly interfaces = new Map<string, InterfaceDecl>();
  private params = new Set<string>();

  constructor(private readonly registry: Registry | undefined) {}

  // --- module --------------------------------------------------------------------------------------------------

  module(ast: V2Module): Document {
    if (ast.name !== undefined) this.document.module = ast.name;
    for (const statement of ast.statements) {
      const body = statement.body;
      const doc = docText(statement.docs);
      if (isV2Import(body)) {
        if (body.modulePath !== undefined) {
          const module = body.modulePath.slice(0, -2); // strip the `.{`
          for (const imported of body.names)
            this.imports.set(imported.name, module);
        }
      } else if (isV2Param(body)) this.param(body, doc);
      else if (isV2Meta(body)) this.meta(this.dict(body.block));
      else if (isV2Options(body))
        for (const [k, v] of this.dict(body.block))
          this.document.options.set(k, v);
      else if (isV2Interface(body)) this.interface(body);
      else if (isV2ModelDecl(body)) this.model(body);
      else if (isV2Composite(body)) {
        if (body.name !== undefined) this.document.name = body.name;
        this.document.description = doc ?? "";
        this.document.root = this.composite(body.decls);
      } else if (isV2Emit(body)) this.emit(body);
    }
    this.params = new Set(this.document.params.map((p) => p.name));
    if (this.params.size > 0) this.substitute(this.document.root);
    return this.document;
  }

  private meta(entries: Dict): void {
    const tags = entries.get("tags");
    this.document.tags = Array.isArray(tags) ? [...tags] : [];
    const requires = entries.get("requires");
    this.document.requires = isDict(requires) ? new Map(requires) : new Map();
    for (const [k, v] of entries)
      if (k !== "tags" && k !== "requires") this.document.extras.set(k, v);
  }

  private param(node: V2Param, doc: string | undefined): void {
    const defaultValue =
      node.default !== undefined ? this.value(node.default) : MISSING;
    this.document.params.push({
      name: node.name,
      type: fromAst(node.type),
      default: isSite(defaultValue) ? MISSING : defaultValue,
      description: doc ?? "",
      ...(node.choices !== undefined
        ? { choices: this.value(node.choices) as unknown[] }
        : {}),
    });
  }

  private emit(node: V2Emit): void {
    const address =
      node.address !== undefined
        ? parseAddress(node.address)
        : parseAddress(
            ALIAS_ADDRESSES[node.alias ?? ""] ?? `local:${node.alias}`,
          );
    this.document.emitters.push({
      address,
      paths: node.paths.map((p) => this.path(p)),
      config: node.config !== undefined ? this.dict(node.config) : new Map(),
    });
  }

  // --- interfaces and models ---------------------------------------------------------------------------------

  private interface(node: V2Interface): void {
    const decl = interfaceFromAst(node, undefined);
    this.interfaces.set(decl.name, decl);
    this.document.interfaces.push(decl);
  }

  private model(node: V2ModelDecl): void {
    this.document.models.push(modelFromAst(node));
  }

  private fieldType(field: V2Field): TypeExpr {
    return fromAst(field.type);
  }

  // --- tree ----------------------------------------------------------------------------------------------------

  private composite(decls: V2NodeDecl[]): Composite {
    const composite = newComposite();
    for (const decl of decls) {
      const body = decl.body;
      const doc = docText(decl.docs);
      let element: Element | undefined;
      if (isV2Store(body)) element = this.store(body, doc);
      else if (isV2Node(body)) {
        const node: Node = {
          $kind: "node",
          name: body.name,
          children: this.composite(body.decls).children,
        };
        if (body.type !== undefined) node.type = fromAst(body.type);
        if (doc !== undefined) node.doc = doc;
        element = node;
      } else if (
        isV2PlainEdge(body) ||
        isV2SharedEdge(body) ||
        isV2CompositeEdge(body)
      )
        element = this.edge(body, doc);
      else if (isV2SchemaBlock(body))
        for (const [k, v] of this.dict(body.block))
          composite.schemaExtras.set(k, v);
      if (element !== undefined) composite.children.set(element.name, element);
    }
    return composite;
  }

  private store(node: V2Store, doc: string | undefined): Store {
    const type = node.type !== undefined ? fromAst(node.type) : undefined;
    const value = node.value !== undefined ? this.value(node.value) : undefined;
    const store: Store = { $kind: "store", name: node.name, value: MISSING };
    if (type !== undefined) store.type = type;
    if (doc !== undefined) store.doc = doc;
    if (isSite(value)) {
      if (
        value.default === MISSING &&
        type !== undefined &&
        isUnsorted(value.sort)
      ) {
        store.site = { $kind: "site", sort: type, default: MISSING }; // `store m : ODEModel = ?;` is a model site
        return store;
      }
      const sort = !isUnsorted(value.sort)
        ? value.sort
        : type ?? { kind: "named", name: "node", args: [] };
      store.site = { $kind: "site", sort, default: value.default };
    } else if (value !== undefined) store.value = value;
    return store;
  }

  private edge(
    node: V2PlainEdge | V2SharedEdge | V2CompositeEdge,
    doc: string | undefined,
  ): Edge {
    let edge: Edge;
    if (isV2CompositeEdge(node)) {
      edge = newEdge(node.name, "process");
      edge.address = parseAddress(node.address ?? "local:Composite");
      const interval = this.scalar(node.interval);
      if (interval !== undefined) edge.interval = interval;
      edge.inner = newComposite();
    } else {
      edge = newEdge(
        node.name,
        isV2SharedEdge(node) ? "shared_process" : node.kind,
      );
      this.applyHead(edge, node.head);
      if (isV2PlainEdge(node)) {
        const interval = this.scalar(node.interval);
        if (interval !== undefined) edge.interval = interval;
        const priority = this.scalar(node.priority);
        if (priority !== undefined && !isParamRefValue(priority))
          edge.priority = priority;
      }
    }
    if (doc !== undefined) edge.doc = doc;
    this.applyItems(edge, node.items);
    return edge;
  }

  private applyHead(edge: Edge, head: V2EdgeHead): void {
    if (head.sharedRef !== undefined) {
      edge.kind = "shared_process_ref";
      edge.extras.set("process_id", head.sharedRef);
      return;
    }
    const address = this.address(head.address);
    const name = head.iface?.$refText;
    if (name !== undefined) edge.ifaceName = name;
    let decl = name !== undefined ? this.interfaces.get(name) : undefined;
    if (name !== undefined && decl === undefined && this.imports.has(name)) {
      const imported = `local:!${this.imports.get(name)}.${name}`;
      decl = this.registry?.lookup(imported);
      if (decl === undefined)
        decl = {
          name,
          kind: edge.kind,
          address: imported,
          module: this.imports.get(name),
          config: {},
          dynamicPorts: false,
        };
    }
    if (address === undefined) {
      if (decl?.address !== undefined)
        edge.address = parseAddress(decl.address);
    } else if (isSite(address)) {
      const sort = !isUnsorted(address.sort) ? address.sort : faceSort(decl);
      edge.address = { $kind: "site", sort, default: address.default };
    } else edge.address = address;
    if (
      decl !== undefined &&
      decl.module === undefined &&
      (decl.inputs !== undefined || decl.outputs !== undefined)
    ) {
      const face: Face = {};
      if (decl.inputs !== undefined) face.inputs = { ...decl.inputs };
      if (decl.outputs !== undefined) face.outputs = { ...decl.outputs };
      edge.ports = face;
    }
  }

  private applyItems(edge: Edge, items: V2CompositeItem[]): void {
    for (const item of items) {
      if (isV2ConfigBlock(item))
        for (const [k, v] of this.dict(item.block))
          edge.config.set(k, plainSites(v));
      else if (isV2InputsBlock(item)) edge.inputs = this.wires(item.block);
      else if (isV2OutputsBlock(item)) edge.outputs = this.wires(item.block);
      else if (isV2PortsBlock(item)) {
        const face: Face = {};
        if (
          item.inputs.length > 0 ||
          (item.$cstNode?.text.includes("inputs") ?? false)
        )
          face.inputs = Object.fromEntries(
            item.inputs.map((f) => [f.name, this.fieldType(f)]),
          );
        if (
          item.outputs.length > 0 ||
          (item.$cstNode?.text.includes("outputs") ?? false)
        )
          face.outputs = Object.fromEntries(
            item.outputs.map((f) => [f.name, this.fieldType(f)]),
          );
        edge.ports = face;
      } else if (isV2ExtraBlock(item))
        for (const [k, v] of this.dict(item.block)) edge.extras.set(k, v);
      else if (isV2BridgeBlock(item)) {
        const bridge: Dict = new Map();
        for (const [k, v] of this.wires(item.block))
          bridge.set(k, wireToDocument(v));
        edge.bridge = bridge;
      } else if (isV2InterfaceBlock(item))
        edge.interface = this.dict(item.block);
      else if (isV2OptionsBlock(item))
        for (const [k, v] of this.dict(item.block)) edge.config.set(k, v);
      else if (isV2InnerBlock(item)) edge.inner = this.composite(item.decls);
    }
  }

  private address(
    node: V2Address | undefined,
  ): Site | ParamRef | ReturnType<typeof parseAddress> | undefined {
    if (node === undefined) return undefined;
    if (node.site !== undefined) return this.value(node.site) as Site;
    if (node.param !== undefined)
      return { $kind: "param", name: node.param.slice(2, -1) };
    return parseAddress(node.literal);
  }

  private scalar(
    node: V2Scalar | undefined,
  ): number | bigint | ParamRef | undefined {
    if (node === undefined) return undefined;
    if (node.param !== undefined)
      return { $kind: "param", name: node.param.slice(2, -1) };
    if (node.float !== undefined) return node.float;
    return BigInt(node.$cstNode?.text.trim() ?? String(node.int));
  }

  private wires(block: V2WireBlock): Map<string, Wire> {
    const out = new Map<string, Wire>();
    for (const wire of block.wires)
      out.set(
        wire.port,
        wire.path !== undefined
          ? this.path(wire.path)
          : this.wires(wire.block!),
      );
    return out;
  }

  private path(node: V2Path): Path {
    const steps: (string | number)[] = [];
    for (const segment of node.segments) {
      if (isV2Index(segment)) steps.push(segment.index);
      else if (segment.up) steps.push("..");
      else if (segment.star) steps.push("*");
      else steps.push(segment.key ?? "");
    }
    return { steps };
  }

  // --- values --------------------------------------------------------------------------------------------------

  private dict(block: V2DictLiteral): Dict {
    const out: Dict = new Map();
    for (const entry of block.entries)
      out.set(entry.key, this.value(entry.value));
    return out;
  }

  private value(node: V2Value): unknown {
    if (isV2IntLiteral(node))
      return BigInt(node.$cstNode?.text.trim() ?? String(node.value));
    if (isV2FloatLiteral(node)) return node.value;
    if (isV2StringLiteral(node)) return node.value;
    if (isV2BoolLiteral(node)) return node.value === "true";
    if (isV2NullLiteral(node)) return null;
    if (isV2ParamRef(node))
      return {
        $kind: "param",
        name: node.value.slice(2, -1),
      } satisfies ParamRef;
    if (isV2SiteValue(node)) {
      const site: Site = {
        $kind: "site",
        sort: node.sort !== undefined ? fromAst(node.sort) : UNSORTED,
        default:
          node.default !== undefined ? this.value(node.default) : MISSING,
      };
      return site;
    }
    if (isV2DictLiteral(node)) return this.dict(node);
    if (isV2ListLiteral(node)) return node.items.map((v) => this.value(v));
    if (isV2TupleLiteral(node))
      return { $kind: "tuple", items: node.items.map((v) => this.value(v)) };
    if (isV2ArrayLiteral(node)) {
      const options: Dict = new Map();
      for (const entry of node.options)
        options.set(entry.key, this.value(entry.value));
      const data = this.value(node.data);
      const dtype = options.has("dtype")
        ? String(options.get("dtype"))
        : undefined;
      if (isExternal(data)) {
        const shape = options.get("shape");
        const ref: ExternalRef = {
          $kind: "external",
          path: data.path,
          format: "array",
        };
        if (dtype !== undefined) ref.dtype = dtype;
        if (Array.isArray(shape) && shape.length > 0)
          ref.shape = shape.map((s) => Number(s));
        return ref;
      }
      return ndarray(data, dtype);
    }
    if (isV2FileLiteral(node)) {
      const ref: ExternalRef = {
        $kind: "external",
        path: node.path,
        format: node.path.endsWith(".json") ? "json" : "text",
      };
      return ref;
    }
    if (isV2ModelRef(node))
      return { $kind: "model", name: node.model.$refText };
    throw new Error(`unexpected value ${(node as { $type: string }).$type}`);
  }

  /** `${name}` strings become parameter references once the params are known (the reader's rule). */
  private substitute(composite: Composite): void {
    for (const element of composite.children.values()) {
      if (element.$kind === "store" && element.value !== MISSING)
        element.value = this.paramValue(element.value);
      else if (element.$kind === "node")
        this.substitute({
          children: element.children,
          schemaExtras: new Map(),
        });
      else if (element.$kind === "edge") {
        element.config = this.paramValue(element.config) as Dict;
        if (typeof element.interval === "string")
          element.interval = this.paramValue(
            element.interval,
          ) as Edge["interval"];
        if (element.inner !== undefined) this.substitute(element.inner);
      }
    }
  }

  private paramValue(value: unknown): unknown {
    if (typeof value === "string") {
      const full = PARAM_FULL.exec(value);
      if (full) return { $kind: "param", name: full[1] } satisfies ParamRef;
      const inline = PARAM_INLINE.exec(value);
      if (inline)
        return {
          $kind: "param",
          name: inline[1],
          template: value,
        } satisfies ParamRef;
      return value;
    }
    if (isDict(value)) {
      const out: Dict = new Map();
      for (const [k, v] of value) out.set(k, this.paramValue(v));
      return out;
    }
    if (Array.isArray(value)) return value.map((v) => this.paramValue(v));
    return value;
  }
}

// --- helpers --------------------------------------------------------------------------------------------------

function isUnsorted(sort: TypeExpr): boolean {
  return sort.kind === "named" && sort.name === "__unsorted__";
}

function isParamRefValue(value: unknown): value is ParamRef {
  return (
    typeof value === "object" &&
    value !== null &&
    (value as { $kind?: string }).$kind === "param"
  );
}

function isExternal(value: unknown): value is ExternalRef {
  return (
    typeof value === "object" &&
    value !== null &&
    (value as { $kind?: string }).$kind === "external"
  );
}

/** Config values keep sites as plain dicts, as the reader does. */
function plainSites(value: unknown): unknown {
  if (isSite(value)) {
    const sort = !isUnsorted(value.sort)
      ? value.sort
      : ({ kind: "named", name: "node", args: [] } as Named);
    const node: Dict = new Map<string, unknown>([
      ["_type", "site"],
      ["_sort", toBigraph(sort)],
    ]);
    if (value.default !== MISSING)
      node.set("_default", plainSites(value.default));
    return node;
  }
  if (isDict(value)) {
    const out: Dict = new Map();
    for (const [k, v] of value) out.set(k, plainSites(v));
    return out;
  }
  if (Array.isArray(value)) return value.map(plainSites);
  return value;
}

function faceSort(decl: InterfaceDecl | undefined): TypeExpr {
  const face: Record<string, unknown> = { _type: "link" };
  if (decl?.inputs !== undefined)
    face._inputs = Object.fromEntries(
      Object.entries(decl.inputs).map(([k, v]) => [k, toBigraph(v)]),
    );
  if (decl?.outputs !== undefined)
    face._outputs = Object.fromEntries(
      Object.entries(decl.outputs).map(([k, v]) => [k, toBigraph(v)]),
    );
  const raw: Raw = { kind: "raw", attrs: face };
  return raw;
}

/** An `array(...)` literal: the shape from the nesting, the dtype as given or inferred as numpy would. */
function ndarray(data: unknown, dtype: string | undefined): NdArray {
  const shape: number[] = [];
  let cursor: unknown = data;
  while (Array.isArray(cursor)) {
    shape.push(cursor.length);
    cursor = cursor[0];
  }
  let inferred = dtype;
  if (inferred === undefined) {
    const leaves = flatten(data);
    if (leaves.every((v) => typeof v === "boolean")) inferred = "bool";
    else if (leaves.every((v) => typeof v === "bigint")) inferred = "int64";
    else inferred = "float64";
  }
  const isFloat = /float/.test(inferred);
  const converted = isFloat
    ? mapLeaves(data, (v) => (typeof v === "bigint" ? Number(v) : v))
    : data;
  return { $kind: "ndarray", dtype: inferred, shape, data: converted };
}

function flatten(value: unknown): unknown[] {
  return Array.isArray(value) ? value.flatMap(flatten) : [value];
}

function mapLeaves(value: unknown, f: (leaf: unknown) => unknown): unknown {
  return Array.isArray(value) ? value.map((v) => mapLeaves(v, f)) : f(value);
}

export { pathToDocument };
