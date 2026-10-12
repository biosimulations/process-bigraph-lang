/**
 * Documents -> the v2 model (the first half of `decompile`).
 *
 * `readDocument` walks the state and schema halves of a `{"schema", "state"}` document in parallel and
 * classifies every key as a site, an edge, a node (a subtree with edges or sites below it, or a struct-typed
 * subtree) or a store. It accepts both the authoring form and the form `Composite.save()` writes (`saved`,
 * auto-detected). `readCompositeSpec` reads a CompositeSpec mapping (`*.composite.yaml`): its `parameters`
 * become params, `${name}` strings become parameter references, and `emitters` become emit declarations.
 */
import {
  type Address,
  COMPOSITE_OPTION_KEYS,
  type Composite,
  containsEdgeOrSite,
  type Dict,
  type Document,
  type Edge,
  EDGE_KINDS,
  type EdgeKind,
  type Element,
  type Emitter,
  type Face,
  isCompositeAddr,
  isDict,
  isEdgeDict,
  isSiteDict,
  isTuple,
  MISSING,
  newComposite,
  newDocument,
  newEdge,
  type Node,
  type Param,
  PARAM_FULL,
  PARAM_INLINE,
  type ParamRef,
  parseAddress,
  RUNTIME_EDGE_KEYS,
  type Site,
  type Source,
  type Store,
  type Tuple,
} from "./model.js";
import { pathFromDocument, wireFromDocument } from "./paths.js";
import { parseType, toBigraph, type TypeExpr } from "./types.js";

const EDGE_KEYS = [
  "_type",
  "address",
  "config",
  "inputs",
  "outputs",
  "_inputs",
  "_outputs",
  "interval",
  "priority",
];
const NESTED_CONFIG_KEYS = ["state", "schema", "bridge", "interface"];

/** Read a `{"schema", "state"}` document. `source` is `authoring`, `saved` or `auto` (detect the saved form). */
export function readDocument(
  doc: Dict,
  source: Source | "auto" = "auto",
  params: Set<string> = new Set(),
): Document {
  const schema = doc.get("schema") ?? new Map();
  const state = doc.get("state") ?? new Map();
  const resolved: Source =
    source === "auto" ? (looksSaved(state) ? "saved" : "authoring") : source;
  const reader = new Reader(resolved === "saved", params);
  const document = newDocument(resolved);
  document.root = reader.composite(state, schema);
  for (const key of COMPOSITE_OPTION_KEYS)
    if (doc.has(key)) document.options.set(key, doc.get(key));
  for (const [key, value] of doc)
    if (
      key !== "schema" &&
      key !== "state" &&
      !COMPOSITE_OPTION_KEYS.includes(key)
    )
      document.extras.set(key, value);
  return document;
}

/** Read a CompositeSpec mapping (the content of a `*.composite.yaml`, or `CompositeSpec.to_dict()`). */
export function readCompositeSpec(spec: Dict): Document {
  const params: Param[] = [];
  const declared = spec.get("parameters");
  if (isDict(declared))
    for (const [name, decl] of declared) params.push(param(name, decl));
  const asDocument: Dict = new Map<string, unknown>([
    ["schema", spec.get("schema") ?? new Map()],
    ["state", spec.get("state") ?? new Map()],
  ]);
  for (const key of COMPOSITE_OPTION_KEYS)
    if (spec.has(key)) asDocument.set(key, spec.get(key));
  const doc = readDocument(
    asDocument,
    "composite_spec",
    new Set(params.map((p) => p.name)),
  );
  doc.params = params;
  doc.name = spec.has("name") ? String(spec.get("name")) : undefined;
  doc.description = String(spec.get("description") ?? "");
  doc.tags = [...((spec.get("tags") as unknown[] | null | undefined) ?? [])];
  const requires = spec.get("requires");
  doc.requires = isDict(requires) ? new Map(requires) : new Map();
  doc.emitters = (
    (spec.get("emitters") as unknown[] | null | undefined) ?? []
  ).map((e) => emitter(e as Dict));
  const known = new Set([
    "schema",
    "state",
    "parameters",
    "name",
    "description",
    "tags",
    "requires",
    "emitters",
    ...COMPOSITE_OPTION_KEYS,
  ]);
  doc.extras = new Map();
  for (const [key, value] of spec)
    if (!known.has(key)) doc.extras.set(key, value);
  return doc;
}

function param(name: string, decl: unknown): Param {
  if (!isDict(decl)) return { name, default: decl, description: "" };
  const typeText = decl.get("type");
  const out: Param = {
    name,
    type: typeText != null ? parseType(String(typeText)) : undefined,
    default: decl.has("default") ? decl.get("default") : MISSING,
    description: String(decl.get("description") ?? ""),
  };
  const choices = decl.get("choices");
  if (choices != null) out.choices = [...(choices as unknown[])];
  return out;
}

function emitter(decl: Dict): Emitter {
  const paths = ((decl.get("paths") as unknown[] | null | undefined) ?? []).map(
    (path) => ({
      steps: String(path)
        .replace(/\./g, "/")
        .split("/")
        .filter((p) => p.length > 0),
    }),
  );
  const config = decl.get("config");
  return {
    address: parseAddress(decl.get("address") ?? "local:RAMEmitter"),
    paths,
    config: isDict(config) ? new Map(config) : new Map(),
  };
}

/** `Composite.save()` output: dict-form addresses, `_contract`/`instance` keys (a root `global_time` alone is not proof). */
function looksSaved(state: unknown): boolean {
  if (!isDict(state)) return false;
  for (const value of state.values()) if (hasSavedEdge(value)) return true;
  return false;
}

function hasSavedEdge(value: unknown): boolean {
  if (!isDict(value)) return false;
  if (isEdgeDict(value)) {
    const address = value.get("address");
    if (isDict(address) && address.has("protocol")) return true;
  }
  if (value.has("_contract") || value.has("instance")) return true;
  for (const v of value.values()) if (hasSavedEdge(v)) return true;
  return false;
}

class Reader {
  constructor(
    private readonly saved: boolean,
    private readonly params: Set<string>,
  ) {}

  // --- tree ----------------------------------------------------------------------------------------------------

  composite(state: unknown, schema: unknown): Composite {
    const composite = newComposite();
    let schemaDict: Dict = new Map();
    if (typeof schema === "string") {
      // a saved nested composite renders its schema as a string
      const parsed = parseType(schema);
      if (parsed.kind === "struct")
        for (const [k, v] of Object.entries(parsed.fields))
          schemaDict.set(k, toBigraph(v));
    } else if (isDict(schema)) schemaDict = schema;
    const stateDict: Dict = isDict(state) ? state : new Map();
    const keys = [...stateDict.keys()];
    for (const key of schemaDict.keys())
      if (!stateDict.has(key)) keys.push(key);
    for (const key of keys) {
      if (key === "global_time" && this.saved) continue;
      const element = this.element(
        key,
        stateDict.has(key) ? stateDict.get(key) : MISSING,
        schemaDict.has(key) ? schemaDict.get(key) : MISSING,
      );
      if (element === undefined)
        composite.schemaExtras.set(key, schemaDict.get(key));
      else composite.children.set(key, element);
    }
    return composite;
  }

  element(key: string, state: unknown, schema: unknown): Element | undefined {
    if (isSiteDict(state)) {
      const store: Store = {
        $kind: "store",
        name: key,
        value: MISSING,
        site: this.site(state),
      };
      const type = this.typeOf(schema);
      if (type) store.type = type;
      return store;
    }
    if (isEdgeDict(state) || (schemaIsEdge(schema) && isDict(state)))
      return this.edge(key, isDict(state) ? state : new Map(), schema);
    if (
      isDict(state) &&
      (containsEdgeOrSite(state) || schemaIsStruct(schema))
    ) {
      const node: Node = { $kind: "node", name: key, children: new Map() };
      if (schemaIsEdgeMap(schema)) node.type = parseType(schema);
      const childSchema = schemaIsStruct(schema) ? schema : new Map();
      node.children = this.composite(state, childSchema).children;
      return node;
    }
    if (state === MISSING) {
      if (schemaIsEdge(schema)) return this.edge(key, new Map(), schema);
      if (schema === MISSING) return undefined;
      const store: Store = { $kind: "store", name: key, value: MISSING };
      const type = this.typeOf(schema);
      if (type) store.type = type;
      return store;
    }
    const store: Store = {
      $kind: "store",
      name: key,
      value: this.value(state),
    };
    const type = this.typeOf(schema);
    if (type) store.type = type;
    return store;
  }

  typeOf(schema: unknown): TypeExpr | undefined {
    if (schema === MISSING || schema === null || schema === undefined)
      return undefined;
    return parseType(schema);
  }

  site(site: Dict): Site {
    const sort = site.has("_sort") ? site.get("_sort") : "node";
    return {
      $kind: "site",
      sort: parseType(sort),
      default: site.has("_default")
        ? this.value(site.get("_default"))
        : MISSING,
    };
  }

  // --- edges ---------------------------------------------------------------------------------------------------

  edge(key: string, node: Dict, schema: unknown): Edge {
    const kind =
      node.get("_type") ??
      (isDict(schema) ? schema.get("_type") : undefined) ??
      guessKind(key, node);
    const edge = newEdge(key, String(kind) as EdgeKind);
    const address = this.address(node.get("address"));
    if (address !== undefined) edge.address = address;
    let config = node.get("config");
    if (
      isDict(config) &&
      address !== undefined &&
      "protocol" in address &&
      isCompositeAddr(address as Address)
    ) {
      edge.inner = this.composite(
        config.get("state") ?? new Map(),
        config.get("schema") ?? new Map(),
      );
      if (config.has("bridge")) edge.bridge = config.get("bridge") as Dict;
      if (config.has("interface"))
        edge.interface = config.get("interface") as Dict;
      const rest: Dict = new Map();
      for (const [k, v] of config)
        if (!NESTED_CONFIG_KEYS.includes(k)) rest.set(k, v);
      config = rest;
    }
    edge.config = isDict(config) ? (this.value(config) as Dict) : new Map();
    for (const [label, target] of [
      ["inputs", edge.inputs],
      ["outputs", edge.outputs],
    ] as const) {
      const wires = node.get(label);
      if (isDict(wires))
        for (const [k, v] of wires) target.set(k, wireFromDocument(v));
    }
    const interval = node.get("interval");
    if (interval !== null && interval !== undefined)
      edge.interval = this.value(interval) as Edge["interval"];
    const priority = node.get("priority");
    if (priority !== null && priority !== undefined)
      edge.priority = priority as Edge["priority"];
    const ports = this.ports(node, schema);
    if (ports) edge.ports = ports;
    for (const [k, v] of node)
      if (!EDGE_KEYS.includes(k) && !RUNTIME_EDGE_KEYS.includes(k))
        edge.extras.set(k, this.value(v));
    return edge;
  }

  address(address: unknown): Address | Site | ParamRef | undefined {
    if (address === null || address === undefined) return undefined;
    if (isSiteDict(address)) return this.site(address);
    if (typeof address === "string" && this.params.size > 0) {
      const full = PARAM_FULL.exec(address);
      if (full) return { $kind: "param", name: full[1] };
    }
    return parseAddress(address);
  }

  ports(node: Dict, schema: unknown): Face | undefined {
    const face: Face = {};
    let found = false;
    for (const [key, attr] of [
      ["_inputs", "inputs"],
      ["_outputs", "outputs"],
    ] as const) {
      const ports = node.has(key)
        ? node.get(key)
        : isDict(schema)
        ? schema.get(key)
        : undefined;
      if (ports === null || ports === undefined) continue;
      found = true;
      face[attr] = portTypes(ports);
    }
    return found ? face : undefined;
  }

  // --- values --------------------------------------------------------------------------------------------------

  value(value: unknown): unknown {
    if (typeof value === "string" && this.params.size > 0) {
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
      for (const [k, v] of value) out.set(k, this.value(v));
      return out;
    }
    if (Array.isArray(value)) return value.map((v) => this.value(v));
    if (isTuple(value))
      return {
        $kind: "tuple",
        items: value.items.map((v) => this.value(v)),
      } satisfies Tuple;
    return value;
  }
}

export function portTypes(ports: unknown): Record<string, TypeExpr> {
  if (typeof ports === "string") {
    const parsed = parseType(ports);
    if (parsed.kind === "struct") return { ...parsed.fields };
    return ports.trim() === "" ? {} : { _: parsed };
  }
  if (isDict(ports)) {
    const out: Record<string, TypeExpr> = {};
    for (const [k, v] of ports) out[k] = parseType(v);
    return out;
  }
  if (ports && typeof ports === "object") {
    const out: Record<string, TypeExpr> = {};
    for (const [k, v] of Object.entries(ports as Record<string, unknown>))
      out[k] = parseType(v);
    return out;
  }
  return {};
}

function schemaIsEdge(schema: unknown): boolean {
  return isDict(schema) && EDGE_KINDS.includes(String(schema.get("_type")));
}

function schemaIsEdgeMap(schema: unknown): boolean {
  return (
    isDict(schema) &&
    schema.get("_type") === "map" &&
    schemaIsEdge(schema.get("_value"))
  );
}

function schemaIsStruct(schema: unknown): schema is Dict {
  return (
    isDict(schema) &&
    schema.size > 0 &&
    ![...schema.keys()].some((k) => k.startsWith("_"))
  );
}

function guessKind(key: string, node: Dict): string {
  if (node.has("interval")) return "process";
  if (node.has("priority") || node.has("_triggers")) return "step";
  throw new Error(
    `edge '${key}' has neither a _type nor a schema entry saying whether it is a step or a process`,
  );
}

export { pathFromDocument };
