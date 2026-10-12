import { startLanguageServer } from "langium/lsp";
import { NodeFileSystem } from "langium/node";
import {
  createConnection,
  ProposedFeatures,
} from "vscode-languageserver/node.js";
import { listenForManifests } from "./manifests.js";
import { createProcessBigraphLanguageServices } from "./process-bigraph-language-module.js";

// Create a connection to the client
const connection = createConnection(ProposedFeatures.all);

// Inject the shared services and language-specific services
const { shared, Pblang } = createProcessBigraphLanguageServices({
  connection,
  ...NodeFileSystem,
});

// a host editor may send the manifests the text is checked against (pblang/setManifests)
listenForManifests(connection, shared, Pblang);

// Start the language server with the shared services
startLanguageServer(shared);
