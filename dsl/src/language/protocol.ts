/**
 * The language server's own messages, beyond LSP. Dependency-free, so the embeddable API re-exports it for clients.
 *
 * `pblang/setManifests` (client to server notification, params `{ manifests: object[] }`): replace the server's
 * manifests (`pblang-manifest/0`) with these, then re-check every open document, which republishes its diagnostics.
 * A host editor sends it once the environment is known and again whenever it changes.
 */
export const SET_MANIFESTS_NOTIFICATION = "pblang/setManifests";

export interface SetManifestsParams {
  manifests: unknown[];
}
