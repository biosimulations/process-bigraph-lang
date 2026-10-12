/**
 * YAML for CompositeSpec files, with the same value model as the JSON codec: integer scalars become `bigint`,
 * floats `number`, mappings `Map`s in source order.
 */
import yaml from "js-yaml";
import { type Dict, isDict, isNdArray, isTuple } from "./model.js";
import { pyFloatRepr } from "./format.js";

const INT = /^[-+]?(0|[1-9][0-9_]*)$/;
const INT_OTHER = /^0[box][0-9a-fA-F_]+$/;

const bigIntType = new yaml.Type("tag:yaml.org,2002:int", {
  kind: "scalar",
  resolve: (data: string) => INT.test(data) || INT_OTHER.test(data),
  construct: (data: string) => {
    const text = data.replace(/_/g, "");
    if (/^0b/.test(text)) return BigInt(parseInt(text.slice(2), 2));
    if (/^0o/.test(text)) return BigInt(parseInt(text.slice(2), 8));
    return BigInt(text);
  },
  predicate: (value: unknown) => typeof value === "bigint",
  represent: (value: unknown) => (value as bigint).toString(),
});

const floatType = new yaml.Type("tag:yaml.org,2002:float", {
  kind: "scalar",
  resolve: (data: string) =>
    (/^[-+]?(\.[0-9]+|[0-9][0-9_]*(\.[0-9_]*)?)([eE][-+]?[0-9]+)?$/.test(
      data,
    ) &&
      !INT.test(data)) ||
    /^[-+]?\.(inf|Inf|INF)$/.test(data) ||
    /^\.(nan|NaN|NAN)$/.test(data),
  construct: (data: string) => {
    const text = data.replace(/_/g, "");
    if (/inf/i.test(text)) return text.startsWith("-") ? -Infinity : Infinity;
    if (/nan/i.test(text)) return NaN;
    return Number(text);
  },
  predicate: (value: unknown) => typeof value === "number",
  represent: (value: unknown) => {
    const n = value as number;
    if (Number.isNaN(n)) return ".nan";
    if (!Number.isFinite(n)) return n > 0 ? ".inf" : "-.inf";
    return pyFloatRepr(n);
  },
});

const SCHEMA = yaml.DEFAULT_SCHEMA.extend({
  implicit: [bigIntType, floatType],
});

export function parseYaml(text: string): unknown {
  return toModel(yaml.load(text, { schema: SCHEMA }));
}

function toModel(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(toModel);
  if (value && typeof value === "object" && !(value instanceof Map)) {
    const out: Dict = new Map();
    for (const [k, v] of Object.entries(value as Record<string, unknown>))
      out.set(k, toModel(v));
    return out;
  }
  return value;
}

/** YAML text in insertion order; arrays and tuples as lists. */
export function dumpYaml(value: unknown): string {
  return yaml.dump(toYamlValue(value), {
    schema: SCHEMA,
    sortKeys: false,
    lineWidth: -1,
    noRefs: true,
  });
}

function toYamlValue(value: unknown): unknown {
  if (isDict(value)) {
    const out: Record<string, unknown> = {};
    for (const [k, v] of value) out[k] = toYamlValue(v);
    return out;
  }
  if (Array.isArray(value)) return value.map(toYamlValue);
  if (isTuple(value)) return value.items.map(toYamlValue);
  if (isNdArray(value)) return toYamlValue(value.data);
  return value;
}
