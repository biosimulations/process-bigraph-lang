/**
 * A JSON codec for documents that keeps what `JSON.parse` loses: integer literals become `bigint` and float
 * literals `number` (so `1` and `1.0` survive a round trip, as Python's `json` keeps them apart), objects
 * become `Map`s in source order, and the tagged forms of `bigraph_schema.json_codec` (`__numpy__` arrays) and
 * of this package's Python side (`__tuple__`) become `NdArray` and `Tuple` values.
 */
import {
  type Dict,
  isDict,
  isNdArray,
  isTuple,
  type NdArray,
  type Tuple,
} from "./model.js";

export function parseJson(text: string): unknown {
  const parser = new JsonParser(text);
  const value = parser.value();
  parser.skip();
  if (parser.pos < text.length)
    throw new SyntaxError(`unexpected trailing input at ${parser.pos}`);
  return value;
}

class JsonParser {
  pos = 0;
  constructor(private readonly text: string) {}

  value(): unknown {
    this.skip();
    const c = this.text[this.pos];
    if (c === "{") return this.object();
    if (c === "[") return this.array();
    if (c === '"') return this.string();
    if (c === "t") return this.literal("true", true);
    if (c === "f") return this.literal("false", false);
    if (c === "n") return this.literal("null", null);
    return this.number();
  }

  private object(): unknown {
    this.pos++;
    const out: Dict = new Map();
    this.skip();
    if (this.text[this.pos] === "}") {
      this.pos++;
      return out;
    }
    for (;;) {
      this.skip();
      const key = this.string();
      this.skip();
      this.expect(":");
      out.set(key, this.value());
      this.skip();
      if (this.text[this.pos] === ",") {
        this.pos++;
        continue;
      }
      this.expect("}");
      return untag(out);
    }
  }

  private array(): unknown[] {
    this.pos++;
    const out: unknown[] = [];
    this.skip();
    if (this.text[this.pos] === "]") {
      this.pos++;
      return out;
    }
    for (;;) {
      out.push(this.value());
      this.skip();
      if (this.text[this.pos] === ",") {
        this.pos++;
        continue;
      }
      this.expect("]");
      return out;
    }
  }

  private string(): string {
    this.expect('"');
    let out = "";
    for (;;) {
      const c = this.text[this.pos];
      if (c === undefined) throw new SyntaxError("unterminated string");
      this.pos++;
      if (c === '"') return out;
      if (c !== "\\") {
        out += c;
        continue;
      }
      const e = this.text[this.pos++];
      switch (e) {
        case '"':
        case "\\":
        case "/":
          out += e;
          break;
        case "b":
          out += "\b";
          break;
        case "f":
          out += "\f";
          break;
        case "n":
          out += "\n";
          break;
        case "r":
          out += "\r";
          break;
        case "t":
          out += "\t";
          break;
        case "u": {
          out += String.fromCharCode(
            parseInt(this.text.slice(this.pos, this.pos + 4), 16),
          );
          this.pos += 4;
          break;
        }
        default:
          throw new SyntaxError(`bad escape \\${e} at ${this.pos}`);
      }
    }
  }

  private number(): number | bigint {
    const match = /^-?(0|[1-9]\d*)(\.\d+)?([eE][+-]?\d+)?/.exec(
      this.text.slice(this.pos, this.pos + 400),
    );
    if (!match) {
      // Python's json writes NaN and Infinity; accept them
      for (const [word, value] of [
        ["NaN", NaN],
        ["Infinity", Infinity],
        ["-Infinity", -Infinity],
      ] as const) {
        if (this.text.startsWith(word, this.pos)) {
          this.pos += word.length;
          return value;
        }
      }
      throw new SyntaxError(`unexpected token at ${this.pos}`);
    }
    this.pos += match[0].length;
    return match[2] === undefined && match[3] === undefined
      ? BigInt(match[0])
      : Number(match[0]);
  }

  private literal<T>(word: string, value: T): T {
    if (!this.text.startsWith(word, this.pos))
      throw new SyntaxError(`unexpected token at ${this.pos}`);
    this.pos += word.length;
    return value;
  }

  skip(): void {
    while (this.pos < this.text.length && /\s/.test(this.text[this.pos]))
      this.pos++;
  }

  private expect(char: string): void {
    if (this.text[this.pos] !== char)
      throw new SyntaxError(
        `expected '${char}' at ${this.pos}, got '${
          this.text[this.pos] ?? "EOF"
        }'`,
      );
    this.pos++;
  }
}

function untag(object: Dict): unknown {
  if (object.get("__numpy__") === true) {
    const array: NdArray = {
      $kind: "ndarray",
      dtype: String(object.get("dtype")),
      shape: (object.get("shape") as unknown[]).map((s) => Number(s)),
      data: object.get("data"),
    };
    return array;
  }
  if (object.get("__tuple__") === true) {
    const tuple: Tuple = {
      $kind: "tuple",
      items: object.get("data") as unknown[],
    };
    return tuple;
  }
  return object;
}

// --- writing ---------------------------------------------------------------------------------------------------

/** JSON text: ints as integers, floats always with a fraction or exponent, arrays and tuples tagged. */
export function stringifyJson(value: unknown, indent = 0): string {
  return write(value, indent, 0);
}

function write(value: unknown, indent: number, depth: number): string {
  if (value === null || value === undefined) return "null";
  if (typeof value === "boolean") return value ? "true" : "false";
  if (typeof value === "bigint") return value.toString();
  if (typeof value === "number") return floatJson(value);
  if (typeof value === "string") return JSON.stringify(value);
  if (isNdArray(value)) {
    const tagged: Dict = new Map<string, unknown>([
      ["__numpy__", true],
      ["dtype", value.dtype],
      ["shape", value.shape.map((s) => BigInt(s))],
      ["data", value.data],
    ]);
    return write(tagged, indent, depth);
  }
  if (isTuple(value)) {
    const tagged: Dict = new Map<string, unknown>([
      ["__tuple__", true],
      ["data", value.items],
    ]);
    return write(tagged, indent, depth);
  }
  const pad = indent > 0 ? "\n" + " ".repeat(indent * (depth + 1)) : "";
  const end = indent > 0 ? "\n" + " ".repeat(indent * depth) : "";
  const sep = indent > 0 ? "," : ",";
  if (Array.isArray(value)) {
    if (value.length === 0) return "[]";
    return (
      "[" +
      value.map((v) => pad + write(v, indent, depth + 1)).join(sep) +
      end +
      "]"
    );
  }
  const entries: [string, unknown][] = isDict(value)
    ? [...value.entries()]
    : Object.entries(value as Record<string, unknown>);
  if (entries.length === 0) return "{}";
  return (
    "{" +
    entries
      .map(
        ([k, v]) =>
          pad +
          JSON.stringify(k) +
          (indent > 0 ? ": " : ":") +
          write(v, indent, depth + 1),
      )
      .join(sep) +
    end +
    "}"
  );
}

export function floatJson(value: number): string {
  if (Number.isNaN(value)) return "NaN";
  if (!Number.isFinite(value)) return value > 0 ? "Infinity" : "-Infinity";
  const text = String(value);
  return /[.eE]/.test(text) ? text : `${text}.0`;
}

/** Plain JS data (objects, arrays, numbers) from a model value, for `JSON.stringify` consumers such as the graph. */
export function toPlain(value: unknown): unknown {
  if (typeof value === "bigint") return Number(value);
  if (isDict(value)) {
    const out: Record<string, unknown> = {};
    for (const [k, v] of value) out[k] = toPlain(v);
    return out;
  }
  if (Array.isArray(value)) return value.map(toPlain);
  if (isTuple(value)) return value.items.map(toPlain);
  if (isNdArray(value)) return toPlain(value.data);
  return value;
}
