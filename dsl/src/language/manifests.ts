import { DocumentState } from "langium";
import type { LangiumSharedServices } from "langium/lsp";
import type { Connection } from "vscode-languageserver";
import type { PblangServices } from "./process-bigraph-language-module.js";
import {
  SET_MANIFESTS_NOTIFICATION,
  type SetManifestsParams,
} from "./protocol.js";

/**
 * Replace the server's manifests and re-check every document. The registry is read only while checking (and by
 * hover and completion, on request), never while linking, so re-running validation is enough: each document drops
 * back to the state before `Validated` and is rebuilt under the workspace lock, and the language server's
 * diagnostics handler republishes its markers.
 */
export async function applyManifests(
  shared: LangiumSharedServices,
  pblang: PblangServices,
  manifests: unknown[],
): Promise<void> {
  pblang.validation.HeaderRegistry.setManifests(manifests);
  await shared.workspace.WorkspaceLock.write(async (token) => {
    const documents = shared.workspace.LangiumDocuments.all.toArray();
    for (const document of documents) {
      if (document.state >= DocumentState.Validated) {
        document.state = DocumentState.IndexedReferences;
        document.diagnostics = undefined;
      }
    }
    await shared.workspace.DocumentBuilder.build(
      documents,
      { validation: true },
      token,
    );
  });
}

/** Answer `pblang/setManifests` on a language server connection. */
export function listenForManifests(
  connection: Connection,
  shared: LangiumSharedServices,
  pblang: PblangServices,
): void {
  connection.onNotification(
    SET_MANIFESTS_NOTIFICATION,
    async (params: SetManifestsParams) => {
      try {
        await applyManifests(shared, pblang, params?.manifests ?? []);
      } catch (error) {
        connection.console.error(
          `pblang/setManifests: ${
            error instanceof Error ? error.message : String(error)
          }`,
        );
      }
    },
  );
}
