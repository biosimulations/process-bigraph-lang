import { beforeAll, describe, expect, test } from "vitest";
import { EmptyFileSystem, type LangiumDocument } from "langium";
import { expandToString as s } from "langium/generate";
import { parseHelper } from "langium/test";
import { createProcessBigraphLanguageServices } from "../../src/language/process-bigraph-language-module.js";
import { Model, isModel } from "../../src/language/generated/ast.js";

let services: ReturnType<typeof createProcessBigraphLanguageServices>;
let parse: ReturnType<typeof parseHelper<Model>>;
let document: LangiumDocument<Model> | undefined;

beforeAll(async () => {
  services = createProcessBigraphLanguageServices(EmptyFileSystem);
  parse = parseHelper<Model>(services.ProcessBigraphLanguage);

  // activate the following if your linking test requires elements from a built-in library, for example
  // await services.shared.workspace.WorkspaceManager.initializeWorkspace([]);
});

describe("Parsing tests", () => {
  test("parse simple model", async () => {
    document = await parse(`
            type float builtin
            type Length = float
            struct Point { x: float; y: float = 0.0; }
            unit um: ["micrometer"]
            remote process Grow at "pkg.Grow" {
                inputs (size: float)
                outputs (size: float)
            }
            store origin: Point;
            init origin = { x = 1.0, y = 2.0 };
            let grow: Grow = Grow();
            connect grow inputs (size = origin.x) outputs (size = origin.x);
        `);

    // check for absence of parser errors the classic way:
    //  deactivated, find a much more human readable way below!
    // expect(document.parseResult.parserErrors).toHaveLength(0);

    expect(
      // here we use a (tagged) template expression to create a human readable representation
      //  of the AST part we are interested in and that is to be compared to our expectation;
      // prior to the tagged template expression we check for validity of the parsed document object
      //  by means of the reusable function 'checkDocumentValid()' to sort out (critical) typos first;
      checkDocumentValid(document) ||
        s`
                Elements:
                  ${document.parseResult.value?.elements
                    ?.map((e) => `${e.$type} ${"name" in e ? e.name : ""}`.trim())
                    ?.join("\n")}
            `,
    ).toBe(s`
        Elements:
          PrimitiveType float
          TypeAlias Length
          StructType Point
          Unit um
          RemoteCallableType Grow
          StoreDecl origin
          InitDecl
          VarDef grow
          ConnectStatement
        `);
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
