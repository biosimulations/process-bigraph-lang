/**
 * A wiring graph from a model and interface declarations alone: what a viewer like loom needs, without importing
 * any process code.
 *
 * `documentGraph` returns plain JSON: `nodes` (edges of the composite with their interface, config keys, port
 * types and docs), `stores` (declared or merely wired), `edges` (one per wired port, resolved to an absolute store
 * path) and, for nested composites, the inner graph under `children`. Port types come from the node's own
 * `_inputs`/`_outputs` when present, else from the registry's declaration for its address.
 */
import type { InterfaceDecl, Registry } from "./headers.js";
import {
  addressText,
  type Composite,
  type Edge,
  edgeIsComposite,
  type Element,
  isParamRef,
  isSite,
  type Path,
  type Wire,
} from "./model.js";
import { surface, type TypeExpr } from "./types.js";

export interface GraphNode {
  id: string;
  kind: string;
  interface: string | null;
  address: string | null;
  interval: number | null;
  config_keys: string[];
  ports: {
    inputs: Record<string, string> | null;
    outputs: Record<string, string> | null;
  };
  dynamic_ports: boolean;
  doc: string | null;
  children?: Graph;
}

export interface GraphStore {
  id: string;
  type: string | null;
  declared: boolean;
  open: boolean;
}

export interface GraphEdge {
  node: string;
  port: string;
  store: string | null;
  direction: "input" | "output";
  type: string | null;
}

export interface Graph {
  nodes: GraphNode[];
  stores: GraphStore[];
  edges: GraphEdge[];
}

export function documentGraph(
  composite: Composite,
  registry?: Registry,
): Graph {
  return new Grapher(registry).composite(composite);
}

class Grapher {
  constructor(private readonly registry: Registry | undefined) {}

  composite(composite: Composite): Graph {
    const index = new Map<string, Element>();
    this.index(composite, [], index);
    const stores = new Map<string, GraphStore>();
    const nodes: GraphNode[] = [];
    const edges: GraphEdge[] = [];
    for (const [path, element] of index) {
      if (element.$kind === "store")
        stores.set(path, {
          id: path,
          type: typeText(element.type ?? element.site?.sort),
          declared: true,
          open: element.site !== undefined,
        });
      else if (
        element.$kind === "node" &&
        ![...element.children.values()].some((c) => c.$kind === "edge")
      )
        if (!stores.has(path))
          stores.set(path, {
            id: path,
            type: typeText(element.type),
            declared: true,
            open: false,
          });
    }
    for (const [path, element] of index) {
      if (element.$kind !== "edge") continue;
      const decl = this.declaration(element);
      const node = this.node(path, element, decl);
      nodes.push(node);
      const parent = path.includes("/")
        ? path.slice(0, path.lastIndexOf("/"))
        : "";
      for (const [direction, wires] of [
        ["input", element.inputs],
        ["output", element.outputs],
      ] as const) {
        const ports = node.ports[`${direction}s`];
        for (const [port, wire] of wires) {
          for (const [subPort, target] of flatten(port, wire)) {
            const storeId = resolve(parent, target);
            if (storeId !== null && !stores.has(storeId))
              stores.set(storeId, {
                id: storeId,
                type: null,
                declared: false,
                open: false,
              });
            edges.push({
              node: path,
              port: subPort,
              store: storeId,
              direction,
              type: ports?.[port] ?? null,
            });
          }
        }
      }
      if (element.inner !== undefined)
        node.children = this.composite(element.inner);
    }
    return { nodes, stores: [...stores.values()], edges };
  }

  private index(
    composite: Composite,
    path: string[],
    index: Map<string, Element>,
  ): void {
    for (const [key, element] of composite.children) {
      const here = [...path, key];
      index.set(here.join("/"), element);
      if (element.$kind === "node")
        this.index(
          { children: element.children, schemaExtras: new Map() },
          here,
          index,
        );
    }
  }

  private declaration(edge: Edge): InterfaceDecl | undefined {
    if (
      this.registry === undefined ||
      edge.address === undefined ||
      isSite(edge.address) ||
      isParamRef(edge.address) ||
      edgeIsComposite(edge)
    )
      return undefined;
    return this.registry.lookup(addressText(edge.address));
  }

  private node(
    path: string,
    edge: Edge,
    decl: InterfaceDecl | undefined,
  ): GraphNode {
    const inputs = edge.ports?.inputs ?? decl?.inputs;
    const outputs = edge.ports?.outputs ?? decl?.outputs;
    const address =
      edge.address === undefined
        ? null
        : isSite(edge.address)
        ? "?"
        : isParamRef(edge.address)
        ? null
        : addressText(edge.address);
    const interval =
      typeof edge.interval === "number"
        ? edge.interval
        : typeof edge.interval === "bigint"
        ? Number(edge.interval)
        : null;
    return {
      id: path,
      kind: edgeIsComposite(edge) ? "composite" : edge.kind,
      interface: decl?.name ?? null,
      address,
      interval,
      config_keys: [...edge.config.keys()].sort(),
      ports: { inputs: portsText(inputs), outputs: portsText(outputs) },
      dynamic_ports: decl?.dynamicPorts ?? false,
      doc: decl?.doc ?? null,
    };
  }
}

function flatten(port: string, wire: Wire): [string, Path][] {
  if (wire instanceof Map) {
    const out: [string, Path][] = [];
    for (const [subPort, subWire] of wire)
      for (const [sub, target] of flatten(subPort, subWire))
        out.push([`${port}/${sub}`, target]);
    return out;
  }
  return [[port, wire]];
}

function resolve(parent: string, path: Path): string | null {
  const absolute = parent.split("/").filter((p) => p.length > 0);
  for (const step of path.steps) {
    if (step === "..") {
      if (absolute.length === 0) return null;
      absolute.pop();
    } else if (step === "*") return null;
    else if (typeof step === "number") absolute.push(`[${step}]`);
    else absolute.push(step);
  }
  return absolute.join("/");
}

function portsText(
  ports: Record<string, TypeExpr> | undefined,
): Record<string, string> | null {
  if (ports === undefined) return null;
  return Object.fromEntries(
    Object.entries(ports).map(([k, v]) => [k, surface(v)]),
  );
}

function typeText(expr: TypeExpr | undefined): string | null {
  return expr !== undefined ? surface(expr) : null;
}
