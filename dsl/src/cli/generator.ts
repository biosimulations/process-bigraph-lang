import type { Model } from "../language/generated/ast.js";
import { expandToNode, joinToNode, toString } from "langium/generate";
import * as fs from "node:fs";
import * as path from "node:path";
import { extractDestinationAndName } from "./cli-util.js";
import { NodeFileSystem } from "langium/node";
import { createProcessBigraphLanguageServices } from "../language/process-bigraph-language-module.js";
import { AstNode } from "langium";

export function generateJavaScript(
  model: Model,
  filePath: string,
  destination: string | undefined,
): string {
  const data = extractDestinationAndName(filePath, destination);
  const generatedFilePath = `${path.join(data.destination, data.name)}.js`;

  const fileNode = expandToNode`
        "use strict";

        ${joinToNode(
          model.types,
          (type) => `console.log('Hello Type, ${type.name}!');`,
          { appendNewLineIfNotEmpty: true },
        )}
    `.appendNewLineIfNotEmpty();

  if (!fs.existsSync(data.destination)) {
    fs.mkdirSync(data.destination, { recursive: true });
  }
  fs.writeFileSync(generatedFilePath, toString(fileNode));
  return generatedFilePath;
}

export function generateJson(
  model: Model,
  filePath: string,
  destination: string | undefined,
): string {
  const data = extractDestinationAndName(filePath, destination);
  const generatedFilePath = `${path.join(data.destination, data.name)}.json`;

  if (!fs.existsSync(data.destination)) {
    fs.mkdirSync(data.destination, { recursive: true });
  }
  const json = generate(model);
  fs.writeFileSync(generatedFilePath, json);
  return generatedFilePath;
}

export function generate(model: AstNode): string {
  const services =
    createProcessBigraphLanguageServices(NodeFileSystem).ProcessBigraphLanguage;
  return services.serializer.JsonSerializer.serialize(model, {
    space: 2,
    sourceText: true,
  });
}
