/** Sidecar assets: the printer's `<name>.assets/*` files, decoded back into values for the writer. */
import type { ExternalRef, NdArray } from "./model.js";
import { parseJson } from "./json.js";
import type { AssetLoader } from "./writer.js";

/** A sidecar's value: text verbatim, arrays from `{dtype, shape, data}`, anything else as JSON. */
export function decodeAsset(ref: ExternalRef, content: string): unknown {
  if (ref.format === "text") return content;
  const payload = parseJson(content);
  if (ref.format === "array") {
    const map = payload as Map<string, unknown>;
    const array: NdArray = {
      $kind: "ndarray",
      dtype: String(map.get("dtype")),
      shape: (map.get("shape") as unknown[]).map((s) => Number(s)),
      data: map.get("data"),
    };
    return array;
  }
  return payload;
}

/** An asset loader over a `read(path)` function, such as a directory on disk or the printer's own assets. */
export function assetLoader(read: (path: string) => string): AssetLoader {
  return (ref) => decodeAsset(ref, read(ref.path));
}
