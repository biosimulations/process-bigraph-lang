/**
 * The v2 model -> documents (the last half of `compile`).
 *
 * `writeDocument` produces the process-bigraph 1.x `{"schema", "state"}` document (plus composite options at
 * the top level); `writeCompositeSpec` produces a CompositeSpec mapping ready for yaml. Both are the exact
 * inverse of the reader for every form it accepts.
 */
import type { ModelDecl } from "./headers.js";
import {
  type Address,
  addressText,
  type Composite,
  type Dict,
  type Document,
  type Edge,
  type ExternalRef,
  isDict,
  isExternalRef,
  isModelRef,
  isParamRef,
  isSite,
  isTuple,
  MISSING,
  MODEL_BLOCKS,
  type Param,
  type ParamRef,
  type Site,
} from "./model.js";
import { pathToSlash, wireToDocument } from "./paths.js";
import { toBigraph } from "./types.js";

export type AssetLoader = (ref: ExternalRef) => unknown;

/** The `{"schema", "state", **options}` document. `assets` loads values the printer externalized. */
export function writeDocument(doc: Document, assets?: AssetLoader): Dict {
  const models = new Map(doc.models.map((m) => [m.name, m]));
  const [schema, state] = composite(doc.root, assets, models);
  const out: Dict = new Map<string, unknown>([
    ["schema", schema],
    ["state", state],
  ]);
  for (const [k, v] of doc.options) out.set(k, v);
  return out;
}

/** A CompositeSpec mapping: `name`, `description`, `tags`, `requires`, `parameters`, `emitters`, `schema`, `state`. */
export function writeCompositeSpec(doc: Document, assets?: AssetLoader): Dict {
  const out: Dict = new Map();
  if (doc.name) out.set("name", doc.name);
  if (doc.description) out.set("description", doc.description);
  if (doc.tags.length > 0) out.set("tags", [...doc.tags]);
  if (doc.requires.size > 0) out.set("requires", new Map(doc.requires));
  if (doc.params.length > 0)
    out.set("parameters", new Map(doc.params.map((p) => [p.name, param(p)])));
  if (doc.emitters.length > 0)
    out.set(
      "emitters",
      doc.emitters.map((e) => {
        const entry: Dict = new Map<string, unknown>([
          ["address", addressText(e.address)],
          ["paths", e.paths.map(pathToSlash)],
        ]);
        if (e.config.size > 0) entry.set("config", value(e.config, assets));
        return entry;
      }),
    );
  const document = writeDocument(doc, assets);
  const schema = document.get("schema") as Dict;
  if (schema.size > 0) out.set("schema", schema);
  out.set("state", document.get("state"));
  for (const [k, v] of doc.options) out.set(k, v);
  for (const [k, v] of doc.extras) out.set(k, v);
  return out;
}

function param(p: Param): Dict {
  const decl: Dict = new Map();
  if (p.type !== undefined) decl.set("type", toBigraph(p.type));
  if (p.default !== MISSING) decl.set("default", p.default);
  if (p.description) decl.set("description", p.description);
  if (p.choices !== undefined) decl.set("choices", [...p.choices]);
  return decl;
}

function composite(
  node: Composite,
  assets: AssetLoader | undefined,
  models: Map<string, ModelDecl>,
): [Dict, Dict] {
  const schema: Dict = new Map();
  const state: Dict = new Map();
  for (const [key, element] of node.children) {
    if (element.$kind === "store") {
      if (element.site !== undefined) {
        state.set(key, site(element.site, assets, models)); // an open store has no schema entry (#213)
        continue;
      }
      if (isModelRef(element.value) && models.has(element.value.name)) {
        const [modelSchema, modelState] = modelTree(
          models.get(element.value.name)!,
        );
        schema.set(key, modelSchema);
        state.set(key, modelState);
        continue;
      }
      if (element.type !== undefined) schema.set(key, toBigraph(element.type));
      if (element.value !== MISSING)
        state.set(key, value(element.value, assets));
    } else if (element.$kind === "node") {
      const [childSchema, childState] = composite(
        { children: element.children, schemaExtras: new Map() },
        assets,
        models,
      );
      if (element.type !== undefined) schema.set(key, toBigraph(element.type));
      else if (childSchema.size > 0) schema.set(key, childSchema);
      state.set(key, childState);
    } else {
      state.set(key, edge(element, assets, models));
    }
  }
  for (const [k, v] of node.schemaExtras) schema.set(k, v);
  return [schema, state];
}

/** A model header as a subtree: one block per member kind, typed with units, valued with the model's values. */
function modelTree(decl: ModelDecl): [Dict, Dict] {
  const schema: Dict = new Map();
  const state: Dict = new Map();
  for (const block of MODEL_BLOCKS) {
    const fields = Object.entries(decl.blocks[block]);
    if (fields.length === 0) continue;
    schema.set(
      block,
      new Map(
        fields.map(([k, f]) => [
          k,
          f.type !== undefined ? toBigraph(f.type) : "float",
        ]),
      ),
    );
    state.set(
      block,
      new Map(
        fields
          .filter(([, f]) => f.hasDefault && f.default !== undefined)
          .map(([k, f]) => [k, f.default]),
      ),
    );
  }
  return [schema, state];
}

/** The schema a model sort admits: named members as a struct, `_` or an open block as a map. */
function sortSchema(sort: ModelDecl): Dict {
  const schema: Dict = new Map();
  for (const block of MODEL_BLOCKS) {
    const fields = sort.blocks[block];
    const names = Object.keys(fields);
    if (names.length === 0 && !sort.openBlocks.has(block)) continue;
    const wildcard = fields._;
    if (wildcard !== undefined || sort.openBlocks.has(block)) {
      const element =
        wildcard !== undefined && wildcard.type !== undefined
          ? toBigraph(wildcard.type)
          : "float";
      schema.set(
        block,
        new Map<string, unknown>([
          ["_type", "map"],
          ["_value", element],
        ]),
      );
    } else {
      schema.set(
        block,
        new Map(
          names.map((k) => [
            k,
            fields[k].type !== undefined ? toBigraph(fields[k].type!) : "float",
          ]),
        ),
      );
    }
  }
  return schema;
}

function edge(
  e: Edge,
  assets: AssetLoader | undefined,
  models: Map<string, ModelDecl>,
): Dict {
  const node: Dict = new Map<string, unknown>([["_type", e.kind]]);
  if (e.ports !== undefined) {
    if (e.ports.inputs !== undefined)
      node.set(
        "_inputs",
        new Map(
          Object.entries(e.ports.inputs).map(([k, v]) => [k, toBigraph(v)]),
        ),
      );
    if (e.ports.outputs !== undefined)
      node.set(
        "_outputs",
        new Map(
          Object.entries(e.ports.outputs).map(([k, v]) => [k, toBigraph(v)]),
        ),
      );
  }
  if (e.address !== undefined) node.set("address", address(e.address, assets));
  const config: Dict = new Map();
  if (e.inner !== undefined) {
    const [innerSchema, innerState] = composite(e.inner, assets, models);
    config.set("state", innerState);
    if (innerSchema.size > 0) config.set("schema", innerSchema);
  }
  if (e.bridge !== undefined) config.set("bridge", e.bridge);
  if (e.interface !== undefined) config.set("interface", e.interface);
  for (const [k, v] of e.config) config.set(k, v);
  if (config.size > 0) node.set("config", value(config, assets));
  if (e.inputs.size > 0)
    node.set(
      "inputs",
      new Map([...e.inputs].map(([k, w]) => [k, wireToDocument(w)])),
    );
  if (e.outputs.size > 0)
    node.set(
      "outputs",
      new Map([...e.outputs].map(([k, w]) => [k, wireToDocument(w)])),
    );
  if (e.interval !== undefined) node.set("interval", value(e.interval, assets));
  if (e.priority !== undefined) node.set("priority", e.priority);
  for (const [k, v] of e.extras) node.set(k, value(v, assets));
  return node;
}

function address(
  a: Address | Site | ParamRef,
  assets: AssetLoader | undefined,
): unknown {
  if (isSite(a)) return site(a, assets);
  if (isParamRef(a)) return value(a, assets);
  return addressText(a);
}

export function site(
  s: Site,
  assets: AssetLoader | undefined,
  models?: Map<string, ModelDecl>,
): Dict {
  let sort: unknown = toBigraph(s.sort);
  if (
    s.sort.kind === "named" &&
    models !== undefined &&
    models.has(s.sort.name) &&
    models.get(s.sort.name)!.isSort
  )
    sort = sortSchema(models.get(s.sort.name)!);
  const node: Dict = new Map<string, unknown>([
    ["_type", "site"],
    ["_sort", sort],
  ]);
  if (s.default !== MISSING) node.set("_default", value(s.default, assets));
  return node;
}

export function value(v: unknown, assets: AssetLoader | undefined): unknown {
  if (isParamRef(v))
    return v.template !== undefined ? v.template : `\${${v.name}}`;
  if (isExternalRef(v)) {
    if (assets === undefined)
      throw new Error(
        `value kept in sidecar '${v.path}' but no asset loader was given`,
      );
    return assets(v);
  }
  if (isSite(v)) return site(v, assets);
  if (isDict(v)) {
    const out: Dict = new Map();
    for (const [k, x] of v) out.set(k, value(x, assets));
    return out;
  }
  if (Array.isArray(v)) return v.map((x) => value(x, assets));
  if (isTuple(v))
    return { $kind: "tuple", items: v.items.map((x) => value(x, assets)) };
  return v;
}
