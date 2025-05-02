import { EmptyFileSystem } from "langium";
import { startLanguageServer } from "langium/lsp";
import {
  BrowserMessageReader,
  BrowserMessageWriter,
  createConnection,
} from "vscode-languageserver/browser.js";
import { createProcessBigraphLanguageServices } from "./process-bigraph-language-module.js";
import { registerGenerateStubsCommand } from "./commands.js";
import { registerCodeActionProvider } from "./services.js";

declare const self: DedicatedWorkerGlobalScope;

const messageReader = new BrowserMessageReader(self);
const messageWriter = new BrowserMessageWriter(self);

const connection = createConnection(messageReader, messageWriter);

const { shared, ProcessBigraphLanguage } = createProcessBigraphLanguageServices(
  {
    connection,
    ...EmptyFileSystem,
  },
);

registerGenerateStubsCommand(connection);
registerCodeActionProvider(connection, ProcessBigraphLanguage);

startLanguageServer(shared);
