/**
 * Manifests at run time: a registry that can be replaced (an editor switching environments), and the language
 * server's `pblang/setManifests` notification, which re-checks the open documents.
 */
import { DocumentState, EmptyFileSystem, URI } from "langium";
import { describe, expect, test } from "vitest";
import * as fs from "node:fs";
import * as path from "node:path";
import type { Connection } from "vscode-languageserver";
import {
  MANIFEST_VERSION,
  Pblang,
  SET_MANIFESTS_NOTIFICATION,
} from "../../src/api.js";
import {
  applyManifests,
  listenForManifests,
} from "../../src/language/manifests.js";
import { createProcessBigraphLanguageServices } from "../../src/language/process-bigraph-language-module.js";
import { Registry } from "../../src/language/v2/headers.js";

const interfaces = path.resolve(
  __dirname,
  "../../../tests/fixtures/data/v2/interfaces",
);
const manifest = JSON.parse(
  fs.readFileSync(
    path.join(interfaces, "test_registry.manifest.json"),
    "utf-8",
  ),
);
const pde = JSON.parse(
  fs.readFileSync(
    path.join(interfaces, "viva_pde_particle.manifest.json"),
    "utf-8",
  ),
);

const TEXT = `import tests.fixtures.test_registry.toy_library.{AddFloatsProcess};
composite demo {
  store a: float = 1.0;
  store b: float = 2.0;
  store sum: float = 0.0;
  process add : AddFloatsProcess {
    inputs { left_hand_addend -> a, right_hand_addend -> b }
    outputs { result -> sum }
  }
}
`;

describe("registry", () => {
  test("adding the same manifest twice keeps short names unique", () => {
    const registry = new Registry();
    registry.addManifest(manifest);
    const count = registry.decls.length;
    registry.addManifest(manifest);
    expect(registry.decls.length).toBe(count);
    expect(registry.lookup("local:AddFloatsProcess")?.name).toBe(
      "AddFloatsProcess",
    );
  });

  test("setManifests replaces, and a rejected manifest leaves the registry as it was", () => {
    const registry = new Registry();
    registry.setManifests([manifest]);
    expect(registry.lookup("local:AddFloatsProcess")).toBeDefined();
    registry.setManifests([pde]);
    expect(registry.lookup("local:AddFloatsProcess")).toBeUndefined();
    expect(registry.lookup("local:FVReactionDiffusion")).toBeDefined();
    expect(() =>
      registry.setManifests([
        manifest,
        { schema_version: "pblang-manifest/9", components: [] },
      ]),
    ).toThrow(/pblang-manifest\/9/);
    expect(registry.lookup("local:FVReactionDiffusion")).toBeDefined();
    expect(registry.lookup("local:AddFloatsProcess")).toBeUndefined();
    expect(MANIFEST_VERSION).toBe("pbg-interfaces/1");
  });

  test("reads the shared format's config_schema and description, and the earlier pblang-manifest/0", () => {
    const registry = new Registry();
    registry.setManifests([pde]);
    const fv = registry.lookup("local:FVReactionDiffusion");
    expect(fv?.config.dt).toMatchObject({ hasDefault: true, default: 0.01 });
    expect(fv?.config.grid?.hasDefault).toBe(false);
    expect(fv?.doc).toMatch(/^PDE half/);
    registry.addManifest({
      schema_version: "pblang-manifest/0",
      components: [
        {
          name: "Old",
          kind: "step",
          address: "local:!old.Old",
          config: { rate: { type: "float", default: 2.0 } },
          inputs: { x: "float" },
          outputs: null,
          doc: "An old entry.",
        },
      ],
    });
    const old = registry.lookup("local:Old");
    expect(old?.config.rate).toMatchObject({ hasDefault: true, default: 2.0 });
    expect(old?.doc).toBe("An old entry.");
  });

  test("a session's setManifests switches what its checks resolve", async () => {
    const pblang = new Pblang().setManifests([pde]);
    expect((await pblang.check(TEXT)).diagnostics.map((d) => d.code)).toContain(
      "S020",
    );
    pblang.setManifests([JSON.stringify(manifest)]);
    expect((await pblang.check(TEXT)).ok).toBe(true);
  });
});

describe("pblang/setManifests", () => {
  async function server() {
    const { shared, Pblang: services } =
      createProcessBigraphLanguageServices(EmptyFileSystem);
    const document = shared.workspace.LangiumDocumentFactory.fromString(
      TEXT,
      URI.parse("memory:///editor/demo.pblang"),
    );
    shared.workspace.LangiumDocuments.addDocument(document);
    await shared.workspace.DocumentBuilder.build([document], {
      validation: true,
    });
    const codes = () => (document.diagnostics ?? []).map((d) => d.code);
    return { shared, services, document, codes };
  }

  test("re-checks open documents against the new manifests and publishes again", async () => {
    const { shared, services, document, codes } = await server();
    expect(codes()).toContain("S020");
    const published: string[] = [];
    shared.workspace.DocumentBuilder.onDocumentPhase(
      DocumentState.Validated,
      (d) => {
        published.push(d.uri.toString());
      },
    );
    await applyManifests(shared, services, [manifest]);
    expect(codes()).not.toContain("S020");
    expect(document.state).toBe(DocumentState.Validated);
    expect(published).toEqual([document.uri.toString()]);
    await applyManifests(shared, services, []);
    expect(codes()).toContain("S020");
  });

  test("the notification handler applies manifests and reports a bad one", async () => {
    const { shared, services, codes } = await server();
    const handlers = new Map<string, (params: unknown) => Promise<void>>();
    const errors: string[] = [];
    const connection = {
      onNotification: (
        method: string,
        handler: (p: unknown) => Promise<void>,
      ) => handlers.set(method, handler),
      console: { error: (message: string) => errors.push(message) },
    } as unknown as Connection;
    listenForManifests(connection, shared, services);
    const handler = handlers.get(SET_MANIFESTS_NOTIFICATION);
    expect(handler).toBeDefined();
    await handler!({ manifests: [manifest] });
    expect(codes()).not.toContain("S020");
    await handler!({ manifests: [{ schema_version: "nope" }] });
    expect(errors).toHaveLength(1);
    expect(errors[0]).toMatch(/pblang\/setManifests: unsupported manifest/);
    expect(codes()).not.toContain("S020"); // the registry kept the previous manifests
  });
});
