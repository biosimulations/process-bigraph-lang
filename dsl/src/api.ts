/**
 * The embeddable API: what an application (a web app, a Node script, a worker) calls to check, compile, decompile
 * and graph composites without the CLI. It is pure TypeScript with no file system: texts and documents come in
 * as strings or plain values and go out the same way, so it runs in a browser's main thread or a worker as well
 * as in Node. The editor services (diagnostics as you type, hover, completion) are the language server, which
 * the `./worker` export starts in a web worker; a `Pblang` session on the main thread is the application's side.
 *
 * ```ts
 * const pblang = new Pblang().addManifest(manifestJson);
 * const { text, assets } = pblang.decompile(documentJson, { name: "demo" });   // document -> .pblang text
 * const { diagnostics } = await pblang.check(text);                             // the checker's findings
 * const { text: json } = await pblang.compile(text, { assets });               // .pblang text -> document
 * const graph = await pblang.graph({ text });                                   // the wiring, for a viewer
 * ```
 */
import { EmptyFileSystem, type LangiumDocument, URI } from "langium";
import * as ast from "./language/generated/ast.js";
import {
  createProcessBigraphLanguageServices,
  type PblangServices,
} from "./language/process-bigraph-language-module.js";
import { assetLoader } from "./language/v2/assets.js";
import { bindModule } from "./language/v2/bind.js";
import { documentGraph, type Graph } from "./language/v2/graph.js";
import type { Registry } from "./language/v2/headers.js";
import { parseJson, stringifyJson, toPlain } from "./language/v2/json.js";
import { type Dict, isDict } from "./language/v2/model.js";
import { printDocument } from "./language/v2/printer.js";
import { readCompositeSpec, readDocument } from "./language/v2/reader.js";
import { writeCompositeSpec, writeDocument } from "./language/v2/writer.js";
import { dumpYaml, parseYaml } from "./language/v2/yaml.js";

export type {
  Graph,
  GraphEdge,
  GraphNode,
  GraphStore,
} from "./language/v2/graph.js";
export type { InterfaceDecl } from "./language/v2/headers.js";

export type Severity = "error" | "warning" | "info" | "hint";

export interface Position {
  line: number;
  character: number;
}

/** One finding of the checker (or a parse error), as the CLI's `pblang-diagnostics/1` envelope lists them. */
export interface Diagnostic {
  code: string;
  slug: string;
  severity: Severity;
  /** zero-based, as the Language Server Protocol spells it */
  range: { start: Position; end: Position };
  /** the document path, slash-joined (as `fill_sites` spells it); empty for a finding without one */
  path: string;
  message: string;
}

export interface CheckResult {
  /** no errors */
  ok: boolean;
  diagnostics: Diagnostic[];
}

export interface CompileOptions {
  /** `document` (the `{schema, state}` document as JSON) or `spec` (a CompositeSpec as YAML) */
  to?: "document" | "spec";
  /** warnings stop the compile too */
  strict?: boolean;
  /** nothing stops the compile (an existing document that relies on defaults the checker flags) */
  force?: boolean;
  /** the sidecar files `file("…")` references name, by path, as text */
  assets?: Record<string, string>;
}

export interface Compiled {
  text: string;
  format: "json" | "yaml";
  diagnostics: Diagnostic[];
}

/** The compile stopped on the checker's findings (or parse errors); `diagnostics` says why. */
export class CompileError extends Error {
  constructor(
    message: string,
    public readonly diagnostics: Diagnostic[],
  ) {
    super(message);
    this.name = "CompileError";
  }
}

export interface DecompileOptions {
  /** names the source in the header and the sidecar directory (`<name>.assets/`) */
  name?: string;
}

export interface Decompiled {
  text: string;
  /** sidecar assets by path, as text; `compile` takes them back through its `assets` option */
  assets: Record<string, string>;
}

/**
 * A document or CompositeSpec: JSON or YAML text (lossless: ints stay ints), or an already parsed value. A bare state
 * tree (no `schema`/`state` keys, as a prebuilt simulator image takes it) reads as the state of a document.
 */
export type DocumentSource = string | object;

export type GraphSource = { text: string } | { document: DocumentSource };

/** The keys that tell a CompositeSpec mapping from a `{schema, state}` document. */
const SPEC_KEYS = [
  "name",
  "description",
  "tags",
  "requires",
  "parameters",
  "emitters",
  "default_n_steps",
  "visualizations",
  "analyses",
  "id",
  "module",
];

export function isSpec(mapping: Dict): boolean {
  return SPEC_KEYS.some((k) => mapping.has(k));
}

/** A document or CompositeSpec from JSON or YAML text, or from a parsed value. */
export function loadDocument(source: DocumentSource): Dict {
  let loaded: unknown;
  if (typeof source === "string") {
    const trimmed = source.trimStart();
    loaded =
      trimmed.startsWith("{") || trimmed.startsWith("[")
        ? parseJson(source)
        : parseYaml(source);
  } else loaded = parseJson(JSON.stringify(source));
  if (!isDict(loaded)) throw new Error("not a document: expected a mapping");
  return loaded;
}

const SEVERITIES: Record<number, Severity> = {
  1: "error",
  2: "warning",
  3: "info",
  4: "hint",
};

/** The findings of a built document as data. */
export function toDiagnostics(document: LangiumDocument): Diagnostic[] {
  return (document.diagnostics ?? []).map((d) => {
    const data = (d.data ?? {}) as { slug?: string; path?: string };
    return {
      code: typeof d.code === "string" ? d.code : "P001",
      slug: data.slug ?? "parse",
      severity: SEVERITIES[d.severity ?? 1] ?? "error",
      range: d.range,
      path: data.path ?? "",
      message: d.message,
    };
  });
}

/**
 * A session of the language: a header registry plus the parser and checker. Manifests and header texts added to
 * it answer the imports of every text it checks, compiles or graphs.
 */
export class Pblang {
  private readonly services: PblangServices;
  private counter = 0;

  constructor() {
    this.services =
      createProcessBigraphLanguageServices(EmptyFileSystem).Pblang;
  }

  /** The header registry: interface declarations by address or unique short name. */
  get registry(): Registry {
    return this.services.validation.HeaderRegistry;
  }

  /** Add a header manifest (`pblang-manifest/0`, as JSON text or parsed). */
  addManifest(manifest: string | object): this {
    this.registry.addManifest(
      typeof manifest === "string" ? JSON.parse(manifest) : manifest,
    );
    return this;
  }

  /**
   * Add a header file (`module a.b;` plus interface and model declarations) to the session's workspace, so its
   * declarations answer imports the way header files open in an editor do.
   */
  async addHeader(
    text: string,
    name = `header-${++this.counter}`,
  ): Promise<this> {
    await this.build(text, `memory:///headers/${name}.pblang`);
    return this;
  }

  /** Parse and check a text against the session's headers. */
  async check(text: string): Promise<CheckResult> {
    const document = await this.build(text);
    try {
      const diagnostics = toDiagnostics(document);
      return {
        ok: !diagnostics.some((d) => d.severity === "error"),
        diagnostics,
      };
    } finally {
      await this.discard(document);
    }
  }

  /**
   * Check a text, then write the document it denotes (JSON in `bigraph_schema.json_codec`'s encoding) or the
   * CompositeSpec (YAML). Throws `CompileError` when the findings stop the compile.
   */
  async compile(text: string, options: CompileOptions = {}): Promise<Compiled> {
    const document = await this.build(text);
    try {
      const diagnostics = toDiagnostics(document);
      const fatal: Severity[] = options.force
        ? []
        : options.strict
        ? ["error", "warning"]
        : ["error"];
      if (
        document.parseResult.parserErrors.length > 0 ||
        diagnostics.some((d) => fatal.includes(d.severity))
      )
        throw new CompileError("compile failed", diagnostics);
      const model = bindModule(document.parseResult.value, this.registry);
      const assets = options.assets ?? {};
      const loader = assetLoader((p) => {
        const content = assets[p];
        if (content === undefined) throw new Error(`missing asset: ${p}`);
        return content;
      });
      if (options.to === "spec")
        return {
          text: dumpYaml(writeCompositeSpec(model, loader)),
          format: "yaml",
          diagnostics,
        };
      return {
        text: stringifyJson(writeDocument(model, loader), 2) + "\n",
        format: "json",
        diagnostics,
      };
    } finally {
      await this.discard(document);
    }
  }

  /** Print a document or CompositeSpec as `.pblang` text; addresses the session's headers know print as imports. */
  decompile(
    source: DocumentSource,
    options: DecompileOptions = {},
  ): Decompiled {
    const loaded = loadDocument(source);
    const model = isSpec(loaded)
      ? readCompositeSpec(loaded)
      : readDocument(loaded);
    const printed = printDocument(model, {
      name: options.name,
      registry: this.registry,
    });
    return { text: printed.text, assets: Object.fromEntries(printed.assets) };
  }

  /** The wiring graph of a text or a document, as plain JSON for a viewer. */
  async graph(source: GraphSource): Promise<Graph> {
    if ("text" in source) {
      const document = await this.build(source.text);
      try {
        const model = bindModule(document.parseResult.value, this.registry);
        return toPlain(documentGraph(model.root, this.registry)) as Graph;
      } finally {
        await this.discard(document);
      }
    }
    const loaded = loadDocument(source.document);
    const model = isSpec(loaded)
      ? readCompositeSpec(loaded)
      : readDocument(loaded);
    return toPlain(documentGraph(model.root, this.registry)) as Graph;
  }

  private async build(
    text: string,
    uri = `memory:///pblang-${++this.counter}.pblang`,
  ): Promise<LangiumDocument<ast.Module>> {
    const workspace = this.services.shared.workspace;
    const document = workspace.LangiumDocumentFactory.fromString<ast.Module>(
      text,
      URI.parse(uri),
    );
    workspace.LangiumDocuments.addDocument(document);
    await workspace.DocumentBuilder.build([document], { validation: true });
    return document;
  }

  private async discard(document: LangiumDocument): Promise<void> {
    await this.services.shared.workspace.DocumentBuilder.update(
      [],
      [document.uri],
    );
  }
}
