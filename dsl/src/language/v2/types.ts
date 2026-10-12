/**
 * Type expressions: the DSL's spelling (from the AST), bigraph-schema's string and dict forms (from header
 * manifests and documents), one canonical shape to compare them by, and the unit each carries. A type parsed
 * from a bigraph-schema form remembers it (`source`), so `toBigraph` is lossless.
 */
import * as ast from "../generated/ast.js";
import { literalValue } from "./headers.js";
import { parseJson } from "./json.js";

export type TypeExpr = Named | Struct | UnionType | Group | Raw;

export interface Named {
  kind: "named";
  name: string;
  args: TypeExpr[];
  units?: string;
  hasDefault?: boolean;
  /** the default as data, when known */
  default?: unknown;
  source?: unknown;
}

export interface Struct {
  kind: "struct";
  fields: Record<string, TypeExpr>;
  source?: unknown;
}

export interface UnionType {
  kind: "union";
  options: TypeExpr[];
  source?: unknown;
}

export interface Group {
  kind: "group";
  items: (number | string)[];
}

export interface Raw {
  kind: "raw";
  attrs: Record<string, unknown>;
  source?: unknown;
}

const SURFACE_NAMES: Record<string, string> = {
  integer: "int",
  boolean: "bool",
};
const BIGRAPH_NAMES: Record<string, string> = {
  int: "integer",
  bool: "boolean",
};
const PARAM_KEYS: Record<string, string[]> = {
  list: ["_element"],
  set: ["_element"],
  tree: ["_leaf"],
  map: ["_key", "_value"],
  tuple: ["_values"],
  enum: ["_values"],
  union: ["_options"],
  maybe: ["_value"],
  overwrite: ["_value"],
  const: ["_value"],
  quote: ["_value"],
};
const ARRAY_KEYS = ["_shape", "_data", "_units"];

// --- from the AST ---------------------------------------------------------------------------------------------

export function fromAst(expr: ast.TypeExpr): TypeExpr {
  const options = expr.options.map(fromPrimary);
  return options.length === 1 ? options[0] : { kind: "union", options };
}

function fromPrimary(node: ast.PrimaryType): TypeExpr {
  if (ast.isNamedType(node)) return fromNamed(node);
  if (ast.isLinkType(node)) {
    return {
      kind: "raw",
      attrs: {
        _type: "link",
        _inputs: toBigraph(fromStruct(node.inputs)),
        _outputs: toBigraph(fromStruct(node.outputs)),
      },
    };
  }
  if (ast.isStructType(node)) return fromStruct(node);
  try {
    const parsed: unknown = JSON.parse(node.raw);
    if (parsed && typeof parsed === "object")
      return { kind: "raw", attrs: parsed as Record<string, unknown> };
  } catch {
    // a raw string that is not JSON is a bigraph-schema type string
  }
  return parseTypeString(node.raw);
}

function fromNamed(node: ast.NamedType): Named {
  const args: TypeExpr[] = [];
  if (node.dims.length > 0) {
    args.push({
      kind: "group",
      items: node.dims.map((d) =>
        d.size !== undefined ? d.size : d.name ?? "_",
      ),
    });
  }
  for (const arg of node.args) {
    if (arg.type !== undefined) args.push(fromAst(arg.type));
    else
      args.push({
        kind: "named",
        name: String(arg.int ?? arg.float),
        args: [],
      });
  }
  const named: Named = { kind: "named", name: node.name, args };
  if (node.units !== undefined) named.units = node.units;
  if (node.default !== undefined) {
    named.hasDefault = true;
    named.default = literalValue(node.default);
  }
  return named;
}

function fromStruct(node: ast.StructType): Struct {
  const fields: Record<string, TypeExpr> = {};
  for (const field of node.fields) fields[field.name] = fromAst(field.type);
  return { kind: "struct", fields };
}

// --- from bigraph-schema (manifests) -------------------------------------------------------------------------

/**
 * A bigraph-schema type in string or dict form, as header manifests and documents carry them. Dict forms may be
 * `Map`s (from the document codec) or plain objects (from `JSON.parse`); the source is kept as given.
 */
export function parseType(spec: unknown): TypeExpr {
  if (typeof spec === "string") {
    const expr = parseTypeString(spec);
    if (expr.kind !== "group") expr.source = spec;
    return expr;
  }
  if (
    spec instanceof Map ||
    (spec && typeof spec === "object" && !Array.isArray(spec))
  ) {
    const expr = parseTypeDict(plainOf(spec) as Record<string, unknown>);
    if (expr.kind !== "group") expr.source = spec;
    return expr;
  }
  throw new Error(`not a type expression: ${String(spec)}`);
}

/** Objects for `Map`s and lists for tuples, recursively (keys stay in order; numbers are kept as they are). */
export function plainOf(value: unknown): unknown {
  if (value instanceof Map) {
    const out: Record<string, unknown> = {};
    for (const [k, v] of value) out[k] = plainOf(v);
    return out;
  }
  if (Array.isArray(value)) return value.map(plainOf);
  if (
    value &&
    typeof value === "object" &&
    (value as { $kind?: string }).$kind === "tuple"
  )
    return (value as { items: unknown[] }).items.map(plainOf);
  return value;
}

function parseTypeDict(spec: Record<string, unknown>): TypeExpr {
  if (!("_type" in spec)) {
    if (Object.keys(spec).some((k) => k.startsWith("_")))
      return { kind: "raw", attrs: spec };
    const fields: Record<string, TypeExpr> = {};
    for (const [k, v] of Object.entries(spec)) fields[k] = parseType(v);
    return { kind: "struct", fields };
  }
  const name = spec._type;
  if (typeof name !== "string") return { kind: "raw", attrs: spec };
  const keys = Object.keys(spec).filter(
    (k) => !["_type", "_default", "_units"].includes(k),
  );
  if (/[[{|~]/.test(name) && keys.length === 0) {
    const inner = parseTypeString(name);
    if (inner.kind === "named") {
      if ("_default" in spec) {
        inner.hasDefault = true;
        inner.default = spec._default;
      }
      if (typeof spec._units === "string") inner.units = spec._units;
    }
    return inner;
  }
  const args: TypeExpr[] = [];
  const paramKeys = PARAM_KEYS[name];
  if (paramKeys && keys.every((k) => paramKeys.includes(k))) {
    for (const key of paramKeys) {
      if (!(key in spec)) continue;
      const value = spec[key];
      if (key === "_values" || key === "_options") {
        for (const v of value as unknown[])
          args.push(
            name === "enum"
              ? { kind: "named", name: String(v), args: [] }
              : parseType(v),
          );
      } else {
        args.push(parseType(value));
      }
    }
  } else if (keys.length > 0 && keys.every((k) => ARRAY_KEYS.includes(k))) {
    if (Array.isArray(spec._shape))
      args.push({ kind: "group", items: (spec._shape as unknown[]).map(dim) });
    if ("_data" in spec) args.push(parseType(spec._data));
  } else if (keys.length > 0) {
    return { kind: "raw", attrs: spec };
  }
  const named: Named = { kind: "named", name, args };
  if ("_default" in spec) {
    named.hasDefault = true;
    named.default = spec._default;
  }
  if (typeof spec._units === "string") named.units = spec._units;
  return named;
}

function dim(value: unknown): number | string {
  if (typeof value === "number") return Math.trunc(value);
  const text = String(value);
  return /^-?\d+$/.test(text) ? Number(text) : text;
}

/** bigraph-schema's string grammar: `name[args]{default}`, `a:T|b:U`, `A~B`, `(…)`. */
export function parseTypeString(text: string): TypeExpr {
  let stripped = text.trim();
  let defaultText: string | undefined;
  const trailing = /^([^{}]*)\{(.*)\}$/.exec(stripped);
  if (trailing) {
    stripped = trailing[1];
    defaultText = trailing[2];
  }
  const parser = new TypeStringParser(stripped);
  const expr = parser.expression();
  if (defaultText !== undefined && expr.kind === "named") {
    expr.hasDefault = true;
    try {
      expr.default = parseJson(defaultText);
    } catch {
      expr.default = defaultText;
    }
  }
  return expr;
}

class TypeStringParser {
  private pos = 0;
  constructor(private readonly text: string) {}

  expression(): TypeExpr {
    const items: (TypeExpr | FieldItem)[] = [this.item()];
    let union = false;
    let struct = false;
    while (this.peek() === "|" || this.peek() === "~") {
      if (this.text[this.pos] === "~") union = true;
      else struct = true;
      this.pos++;
      items.push(this.item());
    }
    if (union && !struct)
      return { kind: "union", options: items.map(unwrapField) };
    if (struct || items.every(isField)) {
      if (items.every(isField)) {
        const fields: Record<string, TypeExpr> = {};
        for (const f of items as unknown as FieldItem[])
          fields[f.fieldName] = f.fieldType;
        return { kind: "struct", fields };
      }
    }
    return unwrapField(items[0]);
  }

  private item(): TypeExpr | FieldItem {
    this.skip();
    if (this.peek() === "(") {
      this.pos++;
      const inner = this.expression();
      this.expect(")");
      return inner;
    }
    const name = this.name();
    this.skip();
    if (this.peek() === ":") {
      this.pos++;
      const fieldType = this.item();
      return { fieldName: name, fieldType: unwrapField(fieldType) };
    }
    const named: Named = { kind: "named", name, args: [] };
    if (this.peek() === "[") {
      this.pos++;
      named.args = this.args();
      this.expect("]");
    }
    this.skip();
    if (this.peek() === "{") {
      let depth = 0;
      do {
        if (this.text[this.pos] === "{") depth++;
        if (this.text[this.pos] === "}") depth--;
        this.pos++;
      } while (depth > 0 && this.pos < this.text.length);
      named.hasDefault = true;
    }
    return named;
  }

  private args(): TypeExpr[] {
    const out: TypeExpr[] = [];
    for (;;) {
      this.skip();
      if (this.peek() === "(") {
        // a shape group `(3|4)`
        this.pos++;
        const items: (number | string)[] = [];
        let current = "";
        while (this.pos < this.text.length && this.text[this.pos] !== ")") {
          if (this.text[this.pos] === "|") {
            items.push(dim(current.trim()));
            current = "";
          } else current += this.text[this.pos];
          this.pos++;
        }
        items.push(dim(current.trim()));
        this.expect(")");
        out.push({ kind: "group", items });
      } else {
        out.push(unwrapField(this.item()));
      }
      this.skip();
      if (this.peek() === ",") {
        this.pos++;
        continue;
      }
      return out;
    }
  }

  private name(): string {
    const start = this.pos;
    while (
      this.pos < this.text.length &&
      /[^[\]{}()|~:,\s]/.test(this.text[this.pos])
    )
      this.pos++;
    return this.text.slice(start, this.pos);
  }

  private peek(): string {
    this.skip();
    return this.text[this.pos] ?? "";
  }

  private skip(): void {
    while (this.pos < this.text.length && /\s/.test(this.text[this.pos]))
      this.pos++;
  }

  private expect(char: string): void {
    this.skip();
    if (this.text[this.pos] !== char)
      throw new Error(
        `expected '${char}' in type '${this.text}' at ${this.pos}`,
      );
    this.pos++;
  }
}

interface FieldItem {
  fieldName: string;
  fieldType: TypeExpr;
}

function isField(item: TypeExpr | FieldItem): item is FieldItem {
  return "fieldName" in item;
}

function unwrapField(item: TypeExpr | FieldItem): TypeExpr {
  return isField(item)
    ? { kind: "struct", fields: { [item.fieldName]: item.fieldType } }
    : item;
}

// --- rendering ------------------------------------------------------------------------------------------------

/** The bigraph-schema form: the source it was parsed from, else a string when possible. */
export function toBigraph(expr: TypeExpr): unknown {
  if (expr.kind !== "group" && expr.source !== undefined) return expr.source;
  switch (expr.kind) {
    case "named": {
      const name = BIGRAPH_NAMES[expr.name] ?? expr.name;
      const shape = expr.args.find((a): a is Group => a.kind === "group");
      const others = expr.args.filter((a) => a.kind !== "group").map(toBigraph);
      let rendered: unknown;
      if (expr.args.length === 0) rendered = name;
      else if (shape) {
        const dict: Record<string, unknown> = {
          _type: name,
          _shape: shape.items.map((i) =>
            typeof i === "number" ? BigInt(i) : i,
          ),
        };
        if (others.length > 0) dict._data = others[0];
        rendered = dict;
      } else if (others.every((o) => typeof o === "string"))
        rendered = `${name}[${others.join(",")}]`;
      else if (name === "list" || name === "set")
        rendered = { _type: name, _element: others[0] };
      else if (name === "tree") rendered = { _type: name, _leaf: others[0] };
      else if (name === "map") {
        const dict: Record<string, unknown> = {
          _type: name,
          _value: others[others.length - 1],
        };
        if (others.length === 2) dict._key = others[0];
        rendered = dict;
      } else if (name === "tuple" || name === "enum")
        rendered = { _type: name, _values: others };
      else if (name === "union") rendered = { _type: name, _options: others };
      else rendered = { _type: name, _value: others[0] };
      if (expr.units !== undefined)
        rendered =
          typeof rendered === "string"
            ? { _type: rendered, _units: expr.units }
            : { ...(rendered as object), _units: expr.units };
      if (expr.hasDefault)
        rendered =
          typeof rendered === "string"
            ? { _type: rendered, _default: expr.default }
            : { ...(rendered as object), _default: expr.default };
      return rendered;
    }
    case "struct": {
      const out: Record<string, unknown> = {};
      for (const [k, v] of Object.entries(expr.fields)) out[k] = toBigraph(v);
      return out;
    }
    case "union": {
      const rendered = expr.options.map(toBigraph);
      return rendered.every((r) => typeof r === "string")
        ? rendered.join("~")
        : { _type: "union", _options: rendered };
    }
    case "group":
      return `(${expr.items.join("|")})`;
    case "raw":
      return expr.attrs;
  }
}

/** The DSL spelling (what the grammar parses back), for the printer and for messages. */
export function surface(expr: TypeExpr): string {
  switch (expr.kind) {
    case "named": {
      const base = SURFACE_NAMES[expr.name] ?? expr.name;
      const shape = expr.args.find((a): a is Group => a.kind === "group");
      const others = expr.args.filter((a) => a.kind !== "group").map(surface);
      let text: string;
      if (shape)
        text = `${base}<${others[0] ?? "float"}>[${shape.items.join(", ")}]`;
      else if (expr.name === "map" && others.length === 1)
        text = `map<string, ${others[0]}>`;
      else if (others.length > 0) text = `${base}<${others.join(", ")}>`;
      else text = base;
      if (expr.units !== undefined) text += ` @ ${JSON.stringify(expr.units)}`;
      if (expr.hasDefault) text += `{${defaultText(expr.default)}}`;
      return text;
    }
    case "struct":
      return `{ ${Object.entries(expr.fields)
        .map(([k, v]) => `${keyText(k)}: ${surface(v)};`)
        .join(" ")} }`;
    case "union":
      return expr.options.map(surface).join(" | ");
    case "group":
      return `[${expr.items.join(", ")}]`;
    case "raw": {
      const kind = expr.attrs._type;
      if (kind === "link")
        return `link<${faceFields(expr.attrs._inputs)}, ${faceFields(
          expr.attrs._outputs,
        )}>`;
      if (kind === "process" || kind === "step") return kind;
      return JSON.stringify(stableJsonText(plainOf(expr.attrs)));
    }
  }
}

function faceFields(ports: unknown): string {
  const plain = plainOf(ports);
  if (!plain || typeof plain !== "object" || Array.isArray(plain))
    return JSON.stringify(String(plain));
  return `{ ${Object.entries(plain as Record<string, unknown>)
    .map(([k, v]) => `${keyText(k)}: ${surface(parseType(v))};`)
    .join(" ")} }`;
}

function keyText(key: string): string {
  return /^[A-Za-z_][A-Za-z0-9_]*$/.test(key) ? key : JSON.stringify(key);
}

/** A default inside a type (`float{0.5}`): JSON, with ints and floats kept apart. */
export function defaultText(value: unknown): string {
  return stableJsonText(value);
}

/** JSON text of plain data or model values in insertion order (bigint ints, floats with a fraction). */
export function stableJsonText(value: unknown): string {
  if (value === null || value === undefined) return "null";
  if (typeof value === "bigint") return value.toString();
  if (typeof value === "number") {
    const text = String(value);
    return /[.eE]/.test(text) || !Number.isFinite(value) ? text : `${text}.0`;
  }
  if (typeof value === "string" || typeof value === "boolean")
    return JSON.stringify(value);
  if (Array.isArray(value)) return `[${value.map(stableJsonText).join(", ")}]`;
  if (value instanceof Map)
    return `{${[...value]
      .map(([k, v]) => `${JSON.stringify(k)}: ${stableJsonText(v)}`)
      .join(", ")}}`;
  if (typeof value === "object")
    return `{${Object.entries(value as Record<string, unknown>)
      .map(([k, v]) => `${JSON.stringify(k)}: ${stableJsonText(v)}`)
      .join(", ")}}`;
  return JSON.stringify(String(value));
}

// --- canonical comparison --------------------------------------------------------------------------------------

/** One canonical shape for every spelling of a type, without units (units are checked separately). */
export function canon(expr: TypeExpr): unknown {
  switch (expr.kind) {
    case "named": {
      const name = BIGRAPH_NAMES[expr.name] ?? expr.name;
      const groups = expr.args.filter((a): a is Group => a.kind === "group");
      let others = expr.args.filter((a) => a.kind !== "group");
      if (
        name === "map" &&
        others.length === 2 &&
        others[0].kind === "named" &&
        others[0].name === "string"
      )
        others = others.slice(1);
      const numeric = others.filter(
        (a) => a.kind === "named" && /^-?\d+$/.test(a.name),
      );
      let out: unknown;
      if (name === "array" || groups.length > 0 || expr.units !== undefined) {
        const dims =
          groups.length > 0
            ? groups[0].items
            : numeric.map((a) => Number((a as Named).name));
        const data = others.filter((a) => !numeric.includes(a));
        out = {
          _type: name,
          _shape: dims.length > 0 ? dims : [1],
          _data: data.length > 0 ? canon(data[data.length - 1]) : "float",
        };
      } else if (others.length > 0)
        out = { _type: name, _args: others.map(canon) };
      else out = name;
      if (expr.hasDefault)
        out =
          typeof out === "string"
            ? { _type: out, _default: true }
            : { ...(out as object), _default: true };
      return out;
    }
    case "struct": {
      const out: Record<string, unknown> = {};
      for (const key of Object.keys(expr.fields).sort())
        out[key] = canon(expr.fields[key]);
      return out;
    }
    case "union":
      return { _type: "union", _options: expr.options.map(canon) };
    case "group":
      return expr.items;
    case "raw": {
      const out: Record<string, unknown> = {};
      for (const key of Object.keys(expr.attrs).sort()) {
        const value = expr.attrs[key];
        if (key === "_units") continue;
        if (key === "_inputs" || key === "_outputs")
          out[key] = canonPorts(value);
        else if (
          ["_value", "_element", "_data", "_sort", "_key", "_leaf"].includes(
            key,
          ) &&
          (typeof value === "string" || (value && typeof value === "object"))
        )
          out[key] = canon(parseType(value));
        else out[key] = value;
      }
      return out;
    }
  }
}

function canonPorts(ports: unknown): unknown {
  if (typeof ports === "string") {
    const parsed = parseTypeString(ports);
    return parsed.kind === "struct" ? canon(parsed) : {};
  }
  if (ports && typeof ports === "object") {
    const out: Record<string, unknown> = {};
    for (const key of Object.keys(ports as object).sort())
      out[key] = canon(parseType((ports as Record<string, unknown>)[key]));
    return out;
  }
  return ports;
}

export function sameType(a: TypeExpr, b: TypeExpr): boolean {
  return stableJson(canon(a)) === stableJson(canon(b));
}

export function stableJson(value: unknown): string {
  if (Array.isArray(value)) return `[${value.map(stableJson).join(",")}]`;
  if (value && typeof value === "object") {
    return `{${Object.keys(value as object)
      .sort()
      .map(
        (k) =>
          `${JSON.stringify(k)}:${stableJson(
            (value as Record<string, unknown>)[k],
          )}`,
      )
      .join(",")}}`;
  }
  return JSON.stringify(value);
}

// --- structure helpers -----------------------------------------------------------------------------------------

/** The units a type carries, on itself or on the value type below a map/list/overwrite. */
export function unitsOf(expr: TypeExpr | undefined): string | undefined {
  if (!expr || expr.kind !== "named") return undefined;
  if (expr.units !== undefined) return expr.units;
  for (let i = expr.args.length - 1; i >= 0; i--) {
    if (expr.args[i].kind !== "group") return unitsOf(expr.args[i]);
  }
  return undefined;
}

export function mapValueType(expr: TypeExpr | undefined): TypeExpr | undefined {
  if (
    expr &&
    expr.kind === "named" &&
    expr.name === "map" &&
    expr.args.length > 0
  )
    return expr.args[expr.args.length - 1];
  return undefined;
}

export function arrayDataType(
  expr: TypeExpr | undefined,
): TypeExpr | undefined {
  if (!expr || expr.kind !== "named") return undefined;
  if (expr.name === "array" || expr.name === "list") {
    for (let i = expr.args.length - 1; i >= 0; i--)
      if (expr.args[i].kind !== "group") return expr.args[i];
    return undefined;
  }
  if (expr.args.length === 2) return expr.args[1]; // positive_array<float>[n, m]
  return undefined;
}

/** `overwrite` when the written value replaces the store (also per key of `map<overwrite<T>>`), else `accumulate`. */
export function semantics(
  expr: TypeExpr | undefined,
): "overwrite" | "accumulate" | "unknown" {
  if (!expr) return "unknown";
  if (expr.kind === "named") {
    if (expr.name === "overwrite") return "overwrite";
    if (["map", "list", "maybe"].includes(expr.name) && expr.args.length > 0)
      return semantics(expr.args[expr.args.length - 1]);
  }
  return "accumulate";
}

export function containsArray(expr: TypeExpr | undefined): boolean {
  if (!expr || expr.kind !== "named") return false;
  return (
    expr.name.includes("array") ||
    expr.args.some((a) => a.kind !== "group" && containsArray(a))
  );
}
