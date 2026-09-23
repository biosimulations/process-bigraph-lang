import { afterEach, beforeAll, describe, expect, test } from "vitest";
import { EmptyFileSystem, type LangiumDocument } from "langium";
import { expandToString as s } from "langium/generate";
import { clearDocuments, parseHelper } from "langium/test";
import { createProcessBigraphLanguageServices } from "../../src/language/process-bigraph-language-module.js";
import {
  Model,
  MemberCall,
  TypeRef,
  isCallableLiteral,
  isConnectStatement,
  isInitDecl,
  isMemberCall,
  isModel,
  isSimpleTypeRef,
  isStoreDecl,
  isVarDef,
} from "../../src/language/generated/ast.js";

let services: ReturnType<typeof createProcessBigraphLanguageServices>;
let parse: ReturnType<typeof parseHelper<Model>>;
let document: LangiumDocument<Model> | undefined;

beforeAll(async () => {
  services = createProcessBigraphLanguageServices(EmptyFileSystem);
  parse = parseHelper<Model>(services.ProcessBigraphLanguage);

  // activate the following if your linking test requires elements from a built-in library, for example
  // await services.shared.workspace.WorkspaceManager.initializeWorkspace([]);
});

afterEach(async () => {
  document && clearDocuments(services.shared, [document]);
});

describe("Linking tests", () => {
  test("linking of types, stores, instances and members", async () => {
    document = await parse(`
            type float builtin
            struct Point { x: float; y: float; }
            remote process Grow at "pkg.Grow" {
                inputs (size: float)
                outputs (size: float)
            }
            store origin: Point;
            init origin = { x = 1.0, y = 2.0 };
            let grow: Grow = Grow();
            let x0: float = origin.x;
            connect grow inputs (size = origin.x) outputs (size = origin.y);
        `);

    const model = document.parseResult.value;
    const typeName = (t: TypeRef) =>
      isSimpleTypeRef(t) ? t.type.ref?.name : undefined;
    const chain = (m: MemberCall): string =>
      (m.previous ? `${chain(m.previous)}.` : "") +
      `${m.element.ref?.$type}:${m.element.ref?.name}`;

    expect(
      // here we first check for validity of the parsed document object by means of the reusable function
      //  'checkDocumentValid()' to sort out (critical) typos first,
      // and then evaluate the cross references we're interested in by checking
      //  the referenced AST element as well as for a potential error message;
      checkDocumentValid(document) ||
        [
          ...model.elements.filter(isStoreDecl).map((d) => `store ${d.name}: ${typeName(d.type)}`),
          ...model.elements.filter(isInitDecl).map((d) => `init -> ${d.store.ref?.$type}:${d.store.ref?.name}`),
          ...model.elements.filter(isVarDef).map((d) => `let ${d.name}: ${typeName(d.type)}`),
          ...model.elements
            .filter(isVarDef)
            .map((d) => d.value)
            .filter(isCallableLiteral)
            .map((v) => `instance of ${v.callable_type.ref?.$type}:${v.callable_type.ref?.name}`),
          ...model.elements
            .filter(isVarDef)
            .map((d) => d.value)
            .filter(isMemberCall)
            .map((v) => `value ${chain(v)}`),
          ...model.elements.filter(isConnectStatement).flatMap((c) => [
            `connect ${c.instance.ref.ref?.$type}:${c.instance.ref.ref?.name}`,
            ...[...c.inputBindings, ...c.outputBindings].map(
              (b) => `  ${b.name} = ${chain(b.variable)}`,
            ),
          ]),
        ].join("\n"),
    ).toBe(s`
        store origin: Point
        init -> StoreDecl:origin
        let grow: Grow
        let x0: float
        instance of RemoteCallableType:Grow
        value StoreDecl:origin.Field:x
        connect VarDef:grow
          size = StoreDecl:origin.Field:x
          size = StoreDecl:origin.Field:y
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
