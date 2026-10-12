import chalk from "chalk";
import { Command } from "commander";
import { PblangLanguageMetaData } from "../language/generated/module.js";
import { createProcessBigraphLanguageServices } from "../language/process-bigraph-language-module.js";
import { extractAstNode, extractDocument } from "./cli-util.js";
import { generateJson } from "./generator.js";
import { NodeFileSystem } from "langium/node";
import * as url from "node:url";
import * as fs from "node:fs/promises";
import * as fsSync from "node:fs";
import * as path from "node:path";
import { type LangiumDocument, URI } from "langium";
import * as ast from "../language/generated/ast.js";
import type { PblangServices } from "../language/process-bigraph-language-module.js";
import { assetLoader } from "../language/v2/assets.js";
import { bindModule } from "../language/v2/bind.js";
import { documentGraph } from "../language/v2/graph.js";
import { type InterfaceDecl, Registry } from "../language/v2/headers.js";
import { parseJson, stringifyJson, toPlain } from "../language/v2/json.js";
import { type Dict, isDict } from "../language/v2/model.js";
import {
  modelDeclFromHeader,
  type ModelHeaderJson,
  modelHeaderLead,
} from "../language/v2/modelheader.js";
import {
  printDocument,
  printInterfaces,
  printModel,
} from "../language/v2/printer.js";
import { readCompositeSpec, readDocument } from "../language/v2/reader.js";
import { writeCompositeSpec, writeDocument } from "../language/v2/writer.js";
import { dumpYaml, parseYaml } from "../language/v2/yaml.js";

const __dirname = url.fileURLToPath(new URL(".", import.meta.url));

const packagePath = path.resolve(__dirname, "..", "..", "package.json");
const packageContent = await fs.readFile(packagePath, "utf-8");

const servicesFor = (_fileName: string) =>
  createProcessBigraphLanguageServices(NodeFileSystem).Pblang;

export const generateAction = async (
  fileName: string,
  opts: GenerateOptions,
): Promise<void> => {
  const services = servicesFor(fileName);
  const model = await extractAstNode<ast.Module>(
    fileName,
    services,
    opts.lenient,
  );
  const generatedFilePath = generateJson(model, fileName, opts.destination);
  console.log(
    chalk.green(`JavaScript code generated successfully: ${generatedFilePath}`),
  );
};

/**
 * Parse and validate a program written in our language.
 * Verifies that no lexer or parser errors occur.
 * Implicitly also checks for validation errors while extracting the document
 *
 * @param fileName Program to validate
 */
export const parseAndValidate = async (fileName: string): Promise<void> => {
  // retrieve the services for the file's language
  const services = servicesFor(fileName);
  // extract a document for our program
  const document = await extractDocument(fileName, services);
  // extract the parse result details
  const parseResult = document.parseResult;
  // verify no lexer, parser, or general diagnostic errors show up
  if (
    parseResult.lexerErrors.length === 0 &&
    parseResult.parserErrors.length === 0
  ) {
    console.log(chalk.green(`Parsed and validated ${fileName} successfully!`));
  } else {
    console.log(chalk.red(`Failed to parse and validate ${fileName}!`));
  }
};

export type GenerateOptions = {
  destination?: string;
  lenient?: boolean;
};

export type CheckOptions = {
  interfaces?: string[];
  json?: boolean;
};

interface CliDiagnostic {
  code: string;
  slug: string;
  severity: string;
  file: string;
  range: {
    start: { line: number; character: number };
    end: { line: number; character: number };
  };
  path: string;
  message: string;
}

/** Build and validate a `.pblang` file against header manifests (and the workspace); the findings as data. */
async function checkFile(
  fileName: string,
  manifests: string[],
): Promise<{
  services: PblangServices;
  document: LangiumDocument;
  diagnostics: CliDiagnostic[];
}> {
  const services = createProcessBigraphLanguageServices(NodeFileSystem).Pblang;
  for (const manifest of manifests) {
    services.validation.HeaderRegistry.addManifest(
      JSON.parse(await fs.readFile(manifest, "utf-8")),
    );
  }
  const document =
    await services.shared.workspace.LangiumDocuments.getOrCreateDocument(
      URI.file(path.resolve(fileName)),
    );
  await services.shared.workspace.DocumentBuilder.build([document], {
    validation: true,
  });
  const severities: Record<number, string> = {
    1: "error",
    2: "warning",
    3: "info",
    4: "hint",
  };
  const diagnostics = (document.diagnostics ?? []).map((d) => {
    const data = (d.data ?? {}) as { slug?: string; path?: string };
    return {
      code: typeof d.code === "string" ? d.code : "P001",
      slug: data.slug ?? "parse",
      severity: severities[d.severity ?? 1] ?? "error",
      file: fileName,
      range: d.range,
      path: data.path ?? "",
      message: d.message,
    };
  });
  return { services, document, diagnostics };
}

function diagnosticLine(d: CliDiagnostic): string {
  return `${d.severity.padEnd(7)} ${d.code} ${d.slug.padEnd(24)} ${
    d.path || `line ${d.range.start.line + 1}`
  }: ${d.message}`;
}

/**
 * Statically check a .pblang file against header manifests; prints the `pblang-diagnostics/1` envelope with
 * `--json`, one line per finding otherwise. Exit 1 when there are errors.
 */
export const checkAction = async (
  fileName: string,
  opts: CheckOptions,
): Promise<void> => {
  const { diagnostics } = await checkFile(fileName, opts.interfaces ?? []);
  const errors = diagnostics.filter((d) => d.severity === "error").length;
  if (opts.json) {
    console.log(
      JSON.stringify(
        {
          version: "pblang-diagnostics/1",
          file: fileName,
          ok: errors === 0,
          summary: {
            error: errors,
            warning: diagnostics.filter((d) => d.severity === "warning").length,
            info: diagnostics.filter((d) => d.severity === "info").length,
          },
          diagnostics,
        },
        null,
        2,
      ),
    );
  } else {
    for (const d of diagnostics) console.log(diagnosticLine(d));
    console.error(`${errors} error(s)`);
  }
  if (errors > 0) process.exit(1);
};

export type CompileOptions = {
  interfaces?: string[];
  to?: "document" | "spec";
  out?: string;
  strict?: boolean;
  force?: boolean;
};

/**
 * Parse and check a .pblang file, then write the document (JSON, `bigraph_schema.json_codec` encoding) or the
 * CompositeSpec (yaml). Findings go to stderr; an error (or, with `--strict`, a warning) stops the compile.
 */
export const compileAction = async (
  fileName: string,
  opts: CompileOptions,
): Promise<void> => {
  const { services, document, diagnostics } = await checkFile(
    fileName,
    opts.interfaces ?? [],
  );
  for (const d of diagnostics) console.error(diagnosticLine(d));
  const fatal = opts.force
    ? []
    : opts.strict
    ? ["error", "warning"]
    : ["error"];
  if (
    diagnostics.some((d) => fatal.includes(d.severity)) ||
    document.parseResult.parserErrors.length > 0
  ) {
    console.error("compile failed");
    process.exit(1);
  }
  const model = bindModule(
    document.parseResult.value as ast.Module,
    services.validation.HeaderRegistry,
  );
  const directory = path.dirname(path.resolve(fileName));
  const loader = assetLoader((p) =>
    fsSync.readFileSync(path.join(directory, p), "utf-8"),
  );
  const written =
    opts.to === "spec"
      ? writeCompositeSpec(model, loader)
      : writeDocument(model, loader);
  const text =
    opts.to === "spec" ? dumpYaml(written) : stringifyJson(written, 2) + "\n";
  await emit(text, opts.out);
};

export type DecompileOptions = {
  interfaces?: string[];
  name?: string;
  out?: string;
};

/** Print a document (JSON) or a CompositeSpec (yaml) as `.pblang` text; sidecar assets go next to `--out`. */
export const decompileAction = async (
  fileName: string,
  opts: DecompileOptions,
): Promise<void> => {
  const text = await fs.readFile(fileName, "utf-8");
  const isYaml = /\.ya?ml$/.test(fileName);
  const loaded = isYaml ? parseYaml(text) : parseJson(text);
  if (!isDict(loaded)) {
    console.error(chalk.red(`${fileName}: not a document`));
    process.exit(2);
  }
  const model =
    isYaml || isSpec(loaded) ? readCompositeSpec(loaded) : readDocument(loaded);
  const registry = await registryFrom(opts.interfaces ?? []);
  const name =
    opts.name ??
    path
      .basename(fileName)
      .replace(/\.(json|ya?ml)$/, "")
      .replace(/\.composite$/, "");
  const printed = printDocument(model, { name, registry });
  if (opts.out !== undefined) {
    await fs.writeFile(opts.out, printed.text, "utf-8");
    const base = path.dirname(path.resolve(opts.out));
    for (const [asset, content] of printed.assets) {
      const target = path.join(base, asset);
      await fs.mkdir(path.dirname(target), { recursive: true });
      await fs.writeFile(target, content, "utf-8");
    }
    console.error(`wrote ${opts.out} and ${printed.assets.size} asset(s)`);
  } else {
    process.stdout.write(printed.text);
    for (const asset of printed.assets.keys())
      console.error(`asset (not written): ${asset}`);
  }
};

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

function isSpec(mapping: Dict): boolean {
  return SPEC_KEYS.some((k) => mapping.has(k));
}

async function registryFrom(manifests: string[]): Promise<Registry> {
  const registry = new Registry();
  for (const manifest of manifests)
    registry.addManifest(JSON.parse(await fs.readFile(manifest, "utf-8")));
  return registry;
}

async function emit(text: string, out: string | undefined): Promise<void> {
  if (out !== undefined) {
    await fs.writeFile(out, text, "utf-8");
    console.error(`wrote ${out}`);
  } else process.stdout.write(text);
}

/** Header files (`module …;` plus one declaration per component) from a manifest, one per module. */
export const headersAction = async (
  manifestFile: string,
  opts: { out?: string },
): Promise<void> => {
  const registry = await registryFrom([manifestFile]);
  const byModule = new Map<string, InterfaceDecl[]>();
  for (const decl of registry.decls) {
    const module = decl.module ?? "";
    if (!byModule.has(module)) byModule.set(module, []);
    byModule.get(module)!.push(decl);
  }
  const files = new Map(
    [...byModule].map(([m, decls]) => [m, printInterfaces(decls, m)]),
  );
  if (
    opts.out !== undefined &&
    (files.size > 1 ||
      (fsSync.existsSync(opts.out) && fsSync.statSync(opts.out).isDirectory()))
  ) {
    await fs.mkdir(opts.out, { recursive: true });
    for (const [module, content] of files)
      await fs.writeFile(
        path.join(opts.out, `${module}.pbl`),
        content,
        "utf-8",
      );
    console.error(`wrote ${files.size} interface file(s) to ${opts.out}`);
  } else await emit([...files.values()].join(""), opts.out);
};

/** A `.pblang` model header from the JSON `describe-model` writes. */
export const modelHeaderAction = async (
  headerFile: string,
  opts: { out?: string },
): Promise<void> => {
  const header = JSON.parse(
    await fs.readFile(headerFile, "utf-8"),
  ) as ModelHeaderJson;
  await emit(
    modelHeaderLead(header) + printModel(modelDeclFromHeader(header)),
    opts.out,
  );
};

/** The wiring graph (JSON) of a `.pblang` file or a document, for viewers. */
export const graphAction = async (
  fileName: string,
  opts: { interfaces?: string[] },
): Promise<void> => {
  let model;
  let registry: Registry;
  if (/\.pbl(ang)?$/.test(fileName)) {
    const { services, document } = await checkFile(
      fileName,
      opts.interfaces ?? [],
    );
    registry = services.validation.HeaderRegistry;
    model = bindModule(document.parseResult.value as ast.Module, registry);
  } else {
    const loaded = parseJson(await fs.readFile(fileName, "utf-8"));
    if (!isDict(loaded)) {
      console.error(chalk.red(`${fileName}: not a document`));
      process.exit(2);
    }
    model = isSpec(loaded) ? readCompositeSpec(loaded) : readDocument(loaded);
    registry = await registryFrom(opts.interfaces ?? []);
  }
  console.log(
    JSON.stringify(toPlain(documentGraph(model.root, registry)), null, 2),
  );
};

export default function (): void {
  const program = new Command();

  program.version(JSON.parse(packageContent).version);

  const fileExtensions = PblangLanguageMetaData.fileExtensions.join(", ");
  program
    .command("generate")
    .argument(
      "<file>",
      `source file (possible file extensions: ${fileExtensions})`,
    )
    .option("-d, --destination <dir>", "destination directory of generating")
    .option(
      "--lenient",
      "fail only on lexer/parser errors; leave semantic findings to `check`",
    )
    .description("write the linked AST of a composite as JSON")
    .action(generateAction);
  program
    .command("check")
    .argument("<file>", "a .pblang file")
    .option(
      "-i, --interfaces <manifest...>",
      "header manifests (JSON) to resolve component addresses in",
    )
    .option("--json", "print the pblang-diagnostics/1 envelope")
    .description("statically check a v2 composite against header manifests")
    .action(checkAction);
  program
    .command("compile")
    .argument(
      "<file>",
      "a .pblang file (file(...) references resolve next to it)",
    )
    .option("-i, --interfaces <manifest...>", "header manifests (JSON)")
    .option(
      "--to <form>",
      "document (JSON) or spec (CompositeSpec yaml)",
      "document",
    )
    .option("--strict", "warnings fail the compile too")
    .option(
      "--force",
      "compile despite the checker's errors (parse errors still stop it)",
    )
    .option("-o, --out <file>", "write the result here instead of stdout")
    .description(
      "parse and check a v2 composite, then write the document it denotes",
    )
    .action(compileAction);
  program
    .command("decompile")
    .argument(
      "<file>",
      "a document (.json, bigraph_schema.json_codec encoding) or a CompositeSpec (.yaml)",
    )
    .option(
      "-i, --interfaces <manifest...>",
      "header manifests (JSON); matching addresses print as imports",
    )
    .option(
      "--name <name>",
      "the name in the header and of the sidecar directory",
    )
    .option(
      "-o, --out <file>",
      "write the text here (sidecar assets go next to it)",
    )
    .description("print a document or CompositeSpec as .pblang text")
    .action(decompileAction);
  program
    .command("headers")
    .argument("<manifest>", "a header manifest (JSON)")
    .option(
      "-o, --out <path>",
      "a .pbl file (one module) or a directory (one file per module)",
    )
    .description("print .pblang interface files from a manifest")
    .action(headersAction);
  program
    .command("model-header")
    .argument("<header>", "a model header (JSON, pblang-model/0)")
    .option("-o, --out <file>", "write the .pblang model header here")
    .description("print a .pblang model header from describe-model's JSON")
    .action(modelHeaderAction);
  program
    .command("graph")
    .argument("<file>", "a .pblang file or a document (.json)")
    .option("-i, --interfaces <manifest...>", "header manifests (JSON)")
    .description("print the wiring graph (JSON) for viewers")
    .action(graphAction);
  program
    .command("parseAndValidate")
    .argument(
      "<file>",
      `source file (possible file extensions: ${fileExtensions})`,
    )
    .description(
      "Indicates where a program parses & validates successfully, but produces no output code",
    )
    .action(parseAndValidate);

  program.parse(process.argv);
}
