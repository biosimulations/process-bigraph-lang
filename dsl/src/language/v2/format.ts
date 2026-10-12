/** Number and string spellings that match Python's `repr(float)` and `json.dumps`, so printed text and sidecar assets are byte-identical on both sides. */

/** Python's `repr(float)`: shortest round-trip digits, fixed notation for exponents in [-4, 16), else `1e-05` / `1e+16`. */
export function pyFloatRepr(value: number): string {
  if (Number.isNaN(value)) return "nan";
  if (!Number.isFinite(value)) return value > 0 ? "inf" : "-inf";
  if (value === 0) return Object.is(value, -0) ? "-0.0" : "0.0";
  const sign = value < 0 ? "-" : "";
  const magnitude = Math.abs(value);
  // the shortest digits that round-trip, from JS's own shortest representation
  const [mantissa, exponentText] = magnitude.toExponential().split("e");
  const digits = mantissa.replace(".", "");
  const exponent = Number(exponentText);
  if (exponent >= -4 && exponent < 16) {
    let text: string;
    if (exponent >= 0) {
      const intPart = digits.slice(0, exponent + 1).padEnd(exponent + 1, "0");
      const fracPart = digits.slice(exponent + 1);
      text = `${intPart}.${fracPart || "0"}`;
    } else {
      text = `0.${"0".repeat(-exponent - 1)}${digits}`;
    }
    return sign + text;
  }
  const frac = digits.slice(1);
  const expSign = exponent < 0 ? "-" : "+";
  const expDigits = String(Math.abs(exponent)).padStart(2, "0");
  return `${sign}${digits[0]}${frac ? `.${frac}` : ""}e${expSign}${expDigits}`;
}

/** The DSL's float literal: Python's repr with `.0` added to a bare mantissa (`1.0e-07`, never `1e-07`). */
export function floatLiteral(value: number): string {
  const text = pyFloatRepr(value);
  if (/[eE]/.test(text)) {
    const [mantissa, exponent] = text.toLowerCase().split("e");
    return `${mantissa.includes(".") ? mantissa : `${mantissa}.0`}e${exponent}`;
  }
  return text;
}

/** Python's `json.dumps(str)`: ASCII only, non-ASCII as `\uXXXX`. */
export function pyJsonString(text: string): string {
  let out = '"';
  for (const char of text) {
    const code = char.codePointAt(0) ?? 0;
    if (char === '"') out += '\\"';
    else if (char === "\\") out += "\\\\";
    else if (char === "\n") out += "\\n";
    else if (char === "\r") out += "\\r";
    else if (char === "\t") out += "\\t";
    else if (char === "\b") out += "\\b";
    else if (char === "\f") out += "\\f";
    else if (code < 0x20 || (code >= 0x7f && code < 0x10000))
      out += `\\u${code.toString(16).padStart(4, "0")}`;
    else if (code >= 0x10000) {
      const high = Math.floor((code - 0x10000) / 0x400) + 0xd800;
      const low = ((code - 0x10000) % 0x400) + 0xdc00;
      out += `\\u${high.toString(16)}\\u${low.toString(16)}`;
    } else out += char;
  }
  return out + '"';
}

/** `textwrap.wrap(text, width)` with its defaults: greedy on whitespace, hyphenated words may break after the hyphen. */
export function wrapText(text: string, width: number): string[] {
  const chunks: string[] = [];
  for (const word of text.replace(/\s+/g, " ").trim().split(" ")) {
    if (word.length === 0) continue;
    // textwrap splits "two-way" into "two-" and "way" (only for letters around the hyphen)
    const parts = word.split(/(?<=[A-Za-z]-)(?=[A-Za-z])/);
    chunks.push(...parts);
  }
  const lines: string[] = [];
  let current = "";
  const flush = () => {
    if (current.length > 0) lines.push(current);
    current = "";
  };
  for (let chunk of chunks) {
    const joinedWithSpace = current.length > 0 && !current.endsWith("-");
    const needed = chunk.length + (joinedWithSpace ? 1 : 0);
    if (current.length + needed <= width) {
      current += (joinedWithSpace ? " " : "") + chunk;
      continue;
    }
    if (current.length > 0) flush();
    while (chunk.length > width) {
      lines.push(chunk.slice(0, width));
      chunk = chunk.slice(width);
    }
    current = chunk;
  }
  flush();
  return lines;
}
