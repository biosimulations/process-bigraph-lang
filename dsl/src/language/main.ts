import { startLanguageServer } from "langium/lsp";
import { NodeFileSystem } from "langium/node";
import {
  createConnection,
  ProposedFeatures,
} from "vscode-languageserver/node.js";
import { createProcessBigraphLanguageServices } from "./process-bigraph-language-module.js";
import { registerGenerateStubCommand } from "./commands.js";
import { registerCodeActionProvider } from "./services.js";

// Create a connection to the client
const connection = createConnection(ProposedFeatures.all);

// Inject the shared services and language-specific services
const { shared, ProcessBigraphLanguage } = createProcessBigraphLanguageServices(
  {
    connection,
    ...NodeFileSystem,
  },
);

registerGenerateStubCommand(connection);
registerCodeActionProvider(connection, ProcessBigraphLanguage);

// Start the language server with the shared services
startLanguageServer(shared);
