import { beforeAll, describe, expect, test } from "vitest";
import { EmptyFileSystem, type LangiumDocument } from "langium";
import { expandToString as s } from "langium/generate";
import { parseHelper } from "langium/test";
import type { Diagnostic } from "vscode-languageserver-types";
import { createProcessBigraphLanguageServices } from "../../src/language/process-bigraph-language-module.js";
import { Model, isModel } from "../../src/language/generated/ast.js";

let services: ReturnType<typeof createProcessBigraphLanguageServices>;
let parse: ReturnType<typeof parseHelper<Model>>;
let document: LangiumDocument<Model> | undefined;

beforeAll(async () => {
  services = createProcessBigraphLanguageServices(EmptyFileSystem);
  const doParse = parseHelper<Model>(services.ProcessBigraphLanguage);
  parse = (input: string) => doParse(input, { validation: true });

  // activate the following if your linking test requires elements from a built-in library, for example
  // await services.shared.workspace.WorkspaceManager.initializeWorkspace([]);
});

const model = `
            type float builtin
            struct Point { x: float; y: float; }
            remote process Grow at "pkg.Grow" {
                inputs (size: float)
                outputs (size: float)
            }
            store origin: Point;
            init origin = { x = 1.0, y = 2.0 };
            let grow: Grow = Grow();`;

describe("Validating", () => {
  test("check no errors", async () => {
    document = await parse(`${model}
            connect grow inputs (size = origin.x) outputs (size = origin.y);
        `);

    expect(
      // here we first check for validity of the parsed document object by means of the reusable function
      //  'checkDocumentValid()' to sort out (critical) typos first,
      // and then evaluate the diagnostics by converting them into human readable strings;
      // note that 'toHaveLength()' works for arrays and strings alike ;-)
      checkDocumentValid(document) ||
        document?.diagnostics?.map(diagnosticToString)?.join("\n"),
    ).toHaveLength(0);
  });

  test("check unresolved member reference", async () => {
    document = await parse(`${model}
            connect grow inputs (size = origin.z) outputs (size = origin.y);
        `);

    expect(
      checkDocumentValid(document) ||
        document?.diagnostics?.map(diagnosticToString)?.join("\n"),
    ).toEqual(
      // 'expect.stringContaining()' makes our test robust against future additions of further validation rules
      expect.stringContaining(s`
                [10:47..10:48]: Could not resolve reference to NamedElement named 'z'.
            `),
    );
  });
});

function checkDocumentValid(document: LangiumDocument): string | undefined {
  return (
    (document.parseResult.parserErrors.length &&
      s`
        Parser errors:
          ${document.parseResult.parserErrors
            .map((e) => e.message)
            .join("\n  ")}
    `) ||
    (document.parseResult.value === undefined &&
      `ParseResult is 'undefined'.`) ||
    (!isModel(document.parseResult.value) &&
      `Root AST object is a ${document.parseResult.value.$type}, expected a '${Model}'.`) ||
    undefined
  );
}

function diagnosticToString(d: Diagnostic) {
  return `[${d.range.start.line}:${d.range.start.character}..${d.range.end.line}:${d.range.end.character}]: ${d.message}`;
}
