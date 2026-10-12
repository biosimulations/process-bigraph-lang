import type { Model } from "../language/generated/ast.js";
import chalk from "chalk";
import { Command } from "commander";
import {
  PblangV2LanguageMetaData,
  ProcessBigraphLanguageLanguageMetaData,
} from "../language/generated/module.js";
import { createProcessBigraphLanguageServices } from "../language/process-bigraph-language-module.js";
import { extractAstNode, extractDocument } from "./cli-util.js";
import { generateJson } from "./generator.js";
import { NodeFileSystem } from "langium/node";
import * as url from "node:url";
import * as fs from "node:fs/promises";
import * as path from "node:path";
import { URI } from "langium";

const __dirname = url.fileURLToPath(new URL(".", import.meta.url));

const packagePath = path.resolve(__dirname, "..", "..", "package.json");
const packageContent = await fs.readFile(packagePath, "utf-8");

/** The language services for a file: v2 for `.pbl`, v1 for `.pblang`. */
const servicesFor = (fileName: string) => {
  const all = createProcessBigraphLanguageServices(NodeFileSystem);
  return fileName.endsWith(".pbl") ? all.PblangV2 : all.ProcessBigraphLanguage;
};

export const generateAction = async (
  fileName: string,
  opts: GenerateOptions,
): Promise<void> => {
  const services = servicesFor(fileName);
  const model = await extractAstNode<Model>(fileName, services, opts.lenient);
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

/**
 * Statically check a .pbl file against header manifests; prints the `pblang-diagnostics/1` envelope with
 * `--json`, one line per finding otherwise. Exit 1 when there are errors.
 */
export const checkAction = async (
  fileName: string,
  opts: CheckOptions,
): Promise<void> => {
  const services =
    createProcessBigraphLanguageServices(NodeFileSystem).PblangV2;
  for (const manifest of opts.interfaces ?? []) {
    services.validation.V2Registry.addManifest(
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
    for (const d of diagnostics) {
      console.log(
        `${d.severity.padEnd(7)} ${d.code} ${d.slug.padEnd(24)} ${
          d.path || `line ${d.range.start.line + 1}`
        }: ${d.message}`,
      );
    }
    console.error(`${errors} error(s)`);
  }
  if (errors > 0) process.exit(1);
};

export default function (): void {
  const program = new Command();

  program.version(JSON.parse(packageContent).version);

  const fileExtensions = [
    ...ProcessBigraphLanguageLanguageMetaData.fileExtensions,
    ...PblangV2LanguageMetaData.fileExtensions,
  ].join(", ");
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
    .description(
      'generates JavaScript code that prints "Hello, {name}!" for each greeting in a source file',
    )
    .action(generateAction);
  program
    .command("check")
    .argument("<file>", "a .pbl file")
    .option(
      "-i, --interfaces <manifest...>",
      "header manifests (JSON) to resolve component addresses in",
    )
    .option("--json", "print the pblang-diagnostics/1 envelope")
    .description("statically check a v2 composite against header manifests")
    .action(checkAction);
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
