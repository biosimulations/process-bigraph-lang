import { EmptyFileSystem } from "langium";
import { startLanguageServer } from "langium/lsp";
import {
  BrowserMessageReader,
  BrowserMessageWriter,
  createConnection,
} from "vscode-languageserver/browser.js";
import { listenForManifests } from "./manifests.js";
import { createProcessBigraphLanguageServices } from "./process-bigraph-language-module.js";

declare const self: DedicatedWorkerGlobalScope;

const messageReader = new BrowserMessageReader(self);
const messageWriter = new BrowserMessageWriter(self);

const connection = createConnection(messageReader, messageWriter);

const { shared, Pblang } = createProcessBigraphLanguageServices({
  connection,
  ...EmptyFileSystem,
});

// the host editor sends the manifests of the environment the text will run in (pblang/setManifests)
listenForManifests(connection, shared, Pblang);
startLanguageServer(shared);
