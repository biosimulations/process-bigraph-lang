/**
 * The v2 object model: what a `.pbl` module denotes (docs/v2/design.md, section 1). A tree of stores, plain
 * nodes and edges, plus the module-level params, interface and model declarations, emitters and options. It is
 * the pivot of `compile` (text -> model -> document) and `decompile` (document -> model -> text).
 *
 * Values are JSON-like trees with a few extra kinds: ints are `bigint` and floats are `number` (so `1` and
 * `1.0` survive), dicts are `Map`s (insertion order is source order, whatever the keys), and tagged objects
 * stand for numpy arrays, tuples, parameter references, sidecar assets, open sites and model references.
 */
import type { InterfaceDecl, ModelDecl } from "./headers.js";
import type { TypeExpr } from "./types.js";

/** The absence of a value (a store with no state, a type with no default), distinct from `null`. */
export const MISSING: unique symbol = Symbol("MISSING");
export type Missing = typeof MISSING;

export type Dict = Map<string, unknown>;

export interface NdArray {
  $kind: "ndarray";
  dtype: string;
  shape: number[];
  /** nested lists of numbers (`bigint` for integer dtypes, `number` for floats) */
  data: unknown;
}

export interface Tuple {
  $kind: "tuple";
  items: unknown[];
}

/** `${name}` on its own, or embedded in a string template. */
export interface ParamRef {
  $kind: "param";
  name: string;
  template?: string;
}

/** A large value kept in a sidecar file (`file("…")` / `array(file("…"))`). */
export interface ExternalRef {
  $kind: "external";
  path: string;
  format: "array" | "text" | "json";
  dtype?: string;
  shape?: number[];
}

/** An open value: `?`, `?(default)`, `? as sort`. */
export interface Site {
  $kind: "site";
  sort: TypeExpr;
  default: unknown | Missing;
}

/** The filler of a model site, by header name. */
export interface ModelRef {
  $kind: "model";
  name: string;
}

export interface Address {
  protocol: string;
  data: string;
}

export function isDict(value: unknown): value is Dict {
  return value instanceof Map;
}

export function dict(entries: Iterable<[string, unknown]> = []): Dict {
  return new Map(entries);
}

export function tagged<K extends string>(
  value: unknown,
  kind: K,
): value is { $kind: K } {
  return (
    typeof value === "object" &&
    value !== null &&
    !(value instanceof Map) &&
    (value as { $kind?: string }).$kind === kind
  );
}

export const isNdArray = (v: unknown): v is NdArray => tagged(v, "ndarray");
export const isTuple = (v: unknown): v is Tuple => tagged(v, "tuple");
export const isParamRef = (v: unknown): v is ParamRef => tagged(v, "param");
export const isExternalRef = (v: unknown): v is ExternalRef =>
  tagged(v, "external");
export const isSite = (v: unknown): v is Site => tagged(v, "site");
export const isModelRef = (v: unknown): v is ModelRef => tagged(v, "model");

// --- addresses -------------------------------------------------------------------------------------------------

export function parseAddress(address: unknown): Address {
  if (isDict(address))
    return {
      protocol: String(address.get("protocol")),
      data: String(address.get("data")),
    };
  if (typeof address === "object" && address !== null && "protocol" in address)
    return {
      protocol: String((address as Address).protocol),
      data: String((address as Address).data),
    };
  if (typeof address === "string") {
    const colon = address.indexOf(":");
    return colon < 0
      ? { protocol: "local", data: address }
      : { protocol: address.slice(0, colon), data: address.slice(colon + 1) };
  }
  throw new Error(`not an address: ${String(address)}`);
}

export function addressText(address: Address): string {
  return `${address.protocol}:${address.data}`;
}

export function isImportAddress(address: Address): boolean {
  return address.protocol === "local" && address.data.startsWith("!");
}

export function addressShortName(address: Address): string {
  const data = address.data.replace(/^!+/, "");
  return data.slice(data.lastIndexOf(".") + 1);
}

export function addressModule(address: Address): string | undefined {
  if (!isImportAddress(address) || !address.data.includes("."))
    return undefined;
  const data = address.data.slice(1);
  return data.slice(0, data.lastIndexOf("."));
}

export function isCompositeAddr(address: Address): boolean {
  return (
    address.protocol === "local" && addressShortName(address) === "Composite"
  );
}

// --- the tree --------------------------------------------------------------------------------------------------

export interface Face {
  inputs?: Record<string, TypeExpr>;
  outputs?: Record<string, TypeExpr>;
}

export interface Store {
  $kind: "store";
  name: string;
  type?: TypeExpr;
  value: unknown | Missing;
  site?: Site;
  doc?: string;
}

export interface Node {
  $kind: "node";
  name: string;
  children: Map<string, Element>;
  type?: TypeExpr;
  doc?: string;
}

export type EdgeKind =
  | "process"
  | "step"
  | "shared_process"
  | "shared_process_ref";

export interface Edge {
  $kind: "edge";
  name: string;
  kind: EdgeKind;
  address?: Address | Site | ParamRef;
  /** the interface the text named (`process p : Name …`) */
  ifaceName?: string;
  config: Dict;
  inputs: Map<string, Wire>;
  outputs: Map<string, Wire>;
  interval?: number | bigint | ParamRef;
  priority?: number | bigint;
  ports?: Face;
  /** a nested composite's `config.state` / `config.schema` */
  inner?: Composite;
  bridge?: Dict;
  interface?: Dict;
  /** any other node keys, verbatim */
  extras: Dict;
  doc?: string;
}

export type Element = Store | Node | Edge;

export interface Composite {
  children: Map<string, Element>;
  /** schema entries that classify as nothing */
  schemaExtras: Dict;
}

export interface Path {
  steps: (string | number)[];
}

export type Wire = Path | Map<string, Wire>;

export interface Param {
  name: string;
  type?: TypeExpr;
  default: unknown | Missing;
  description: string;
  choices?: unknown[];
}

export interface Emitter {
  address: Address;
  paths: Path[];
  config: Dict;
}

export type Source = "authoring" | "saved" | "composite_spec";

export interface Document {
  root: Composite;
  module?: string;
  name?: string;
  description: string;
  tags: unknown[];
  requires: Dict;
  params: Param[];
  /** declared inline in the text */
  interfaces: InterfaceDecl[];
  models: ModelDecl[];
  emitters: Emitter[];
  options: Dict;
  source: Source;
  /** unknown top-level / CompositeSpec keys */
  extras: Dict;
}

export function newComposite(): Composite {
  return { children: new Map(), schemaExtras: new Map() };
}

export function newDocument(source: Source = "authoring"): Document {
  return {
    root: newComposite(),
    description: "",
    tags: [],
    requires: new Map(),
    params: [],
    interfaces: [],
    models: [],
    emitters: [],
    options: new Map(),
    source,
    extras: new Map(),
  };
}

export function newEdge(name: string, kind: EdgeKind): Edge {
  return {
    $kind: "edge",
    name,
    kind,
    config: new Map(),
    inputs: new Map(),
    outputs: new Map(),
    extras: new Map(),
  };
}

export function edgeIsComposite(edge: Edge): boolean {
  return (
    edge.address !== undefined &&
    !isSite(edge.address) &&
    !isParamRef(edge.address) &&
    isCompositeAddr(edge.address)
  );
}

export const EDGE_KINDS: readonly string[] = [
  "process",
  "step",
  "shared_process",
  "shared_process_ref",
];
export const RUNTIME_EDGE_KEYS: readonly string[] = ["instance", "_contract"];
export const COMPOSITE_OPTION_KEYS: readonly string[] = [
  "global_time_precision",
  "run_steps_on_init",
  "parallel_steps",
  "parallel_processes",
  "parallel_workers",
  "skip_process_state",
  "contract_strict",
];
export const MODEL_BLOCKS = ["compartments", "species", "parameters"] as const;

export const IDENTIFIER = /^[A-Za-z_][A-Za-z0-9_]*$/;
export const PARAM_FULL = /^\$\{([A-Za-z_][A-Za-z0-9_]*)\}$/;
export const PARAM_INLINE = /\$\{([A-Za-z_][A-Za-z0-9_]*)\}/;

export function isIdentifier(key: unknown): key is string {
  return typeof key === "string" && IDENTIFIER.test(key);
}

/** A template site in document form: `{"_type": "site", "_sort": ..., "_default"?: ...}`. */
export function isSiteDict(value: unknown): value is Dict {
  return isDict(value) && value.get("_type") === "site";
}

/** A step/process node in the state half (its `_type` says so, or it carries an `address`). */
export function isEdgeDict(value: unknown): value is Dict {
  return (
    isDict(value) &&
    (EDGE_KINDS.includes(String(value.get("_type"))) || value.has("address"))
  );
}

/** Whether a state subtree holds an edge or a site anywhere below (such a dict is a `node`, not a store value). */
export function containsEdgeOrSite(value: unknown): boolean {
  if (isEdgeDict(value) || isSiteDict(value)) return true;
  if (isDict(value))
    for (const v of value.values()) if (containsEdgeOrSite(v)) return true;
  return false;
}

/** The number of scalar leaves in an array or (nested) list. */
export function elementCount(value: unknown): number {
  if (isNdArray(value)) return value.shape.reduce((a, b) => a * b, 1);
  if (Array.isArray(value))
    return value.reduce<number>((sum, v) => sum + elementCount(v), 0);
  if (isTuple(value)) return elementCount(value.items);
  return 1;
}

export function isNumber(value: unknown): value is number | bigint {
  return typeof value === "number" || typeof value === "bigint";
}
