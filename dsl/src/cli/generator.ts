import * as ast from "../language/generated/ast.js";
import * as fs from "node:fs";
import * as path from "node:path";
import { extractDestinationAndName } from "./cli-util.js";
import { NodeFileSystem } from "langium/node";
import { createProcessBigraphLanguageServices } from "../language/process-bigraph-language-module.js";

/** Write the linked AST of a module as JSON (a debugging aid; the Python side no longer reads it). */
export function generateJson(
  model: ast.Module,
  filePath: string,
  destination: string | undefined,
): string {
  const data = extractDestinationAndName(filePath, destination);
  const generatedFilePath = `${path.join(data.destination, data.name)}.json`;

  if (!fs.existsSync(data.destination)) {
    fs.mkdirSync(data.destination, { recursive: true });
  }
  fs.writeFileSync(generatedFilePath, generate(model));
  return generatedFilePath;
}

export function generate(model: ast.Module): string {
  const services = createProcessBigraphLanguageServices(NodeFileSystem).Pblang;
  return services.serializer.JsonSerializer.serialize(model, {
    space: 2,
    sourceText: true,
    refText: true,
  });
}
