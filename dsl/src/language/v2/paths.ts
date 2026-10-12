/** Wire paths: the document's list form (`["..", "fields", "A", 0, 1]`) and the DSL's text form (`../fields.A[0][1]`). */
import {
  type Dict,
  isDict,
  isIdentifier,
  type Path,
  type Wire,
} from "./model.js";

/** A document wire: a list of steps, or a bare string (a one-step path). */
export function pathFromDocument(wire: unknown): Path {
  if (typeof wire === "string") return { steps: [wire] };
  if (Array.isArray(wire)) return { steps: wire.map(step) };
  throw new Error(`not a wire path: ${JSON.stringify(wire)}`);
}

export function pathToDocument(path: Path): (string | bigint)[] {
  return path.steps.map((s) => (typeof s === "number" ? BigInt(s) : s));
}

/** `../fields.A[0][1]`: `..` segments end with `/`, keys are joined by `.`, indices are `[i]`. */
export function pathToText(path: Path): string {
  let text = "";
  let previous: string | number | undefined;
  for (const s of path.steps) {
    if (typeof s === "number") text += `[${s}]`;
    else {
      const token =
        s === ".." || s === "*" || isIdentifier(s) ? s : JSON.stringify(s);
      if (previous === undefined) text += token;
      else if (previous === "..") text += `/${token}`;
      else text += `.${token}`;
    }
    previous = s;
  }
  return text;
}

/** `a/b/0`: the form `fill_sites` and CompositeSpec `emitters.paths` use. */
export function pathToSlash(path: Path): string {
  return path.steps.map(String).join("/");
}

/** The inverse of `pathToText` (used by tests). */
export function parsePath(text: string): Path {
  const steps: (string | number)[] = [];
  let rest = text.trim();
  while (rest.startsWith("../")) {
    steps.push("..");
    rest = rest.slice(3);
  }
  if (rest === "..") {
    steps.push("..");
    rest = "";
  }
  for (const segment of splitSegments(rest)) {
    let head: string;
    let indices: string;
    if (segment.startsWith('"')) {
      let end = segment.indexOf('"', 1);
      while (end !== -1 && segment[end - 1] === "\\")
        end = segment.indexOf('"', end + 1);
      head = segment.slice(0, end + 1);
      indices = segment.slice(end + 1);
    } else {
      const bracket = segment.indexOf("[");
      head = bracket < 0 ? segment : segment.slice(0, bracket);
      indices = bracket < 0 ? "" : segment.slice(bracket);
    }
    if (head) steps.push(unquote(head));
    for (const m of indices.matchAll(/\[(-?\d+)\]/g)) steps.push(Number(m[1]));
  }
  return { steps };
}

function splitSegments(text: string): string[] {
  const segments: string[] = [];
  let current = "";
  let quoted = false;
  for (const char of text) {
    if (char === '"') quoted = !quoted;
    if (char === "." && !quoted) {
      segments.push(current);
      current = "";
    } else current += char;
  }
  if (current || segments.length > 0) segments.push(current);
  return segments.filter((s) => s.length > 0);
}

function step(s: unknown): string | number {
  if (typeof s === "boolean") return String(s);
  if (typeof s === "bigint") return Number(s);
  if (typeof s === "number") return s;
  return String(s);
}

function unquote(key: string): string {
  if (key.length >= 2 && key.startsWith('"') && key.endsWith('"'))
    return key.slice(1, -1).replace(/\\"/g, '"').replace(/\\\\/g, "\\");
  return key;
}

/** A document wire: a path, or a dict of sub-port wires. */
export function wireFromDocument(wire: unknown): Wire {
  if (isDict(wire)) {
    const out = new Map<string, Wire>();
    for (const [k, v] of wire) out.set(k, wireFromDocument(v));
    return out;
  }
  return pathFromDocument(wire);
}

export function wireToDocument(wire: Wire): unknown {
  if (wire instanceof Map) {
    const out: Dict = new Map();
    for (const [k, v] of wire) out.set(k, wireToDocument(v));
    return out;
  }
  return pathToDocument(wire);
}

export function isPath(wire: Wire): wire is Path {
  return !(wire instanceof Map);
}
