import {CodeAction, CodeActionParams, Command, Connection} from 'vscode-languageserver';
import { ProcessBigraphLanguageServices } from './process-bigraph-language-module.js';
import {URI} from "langium";

export function registerCodeActionProvider(connection: Connection | undefined, services: ProcessBigraphLanguageServices) {
    connection?.onCodeAction(async (params: CodeActionParams): Promise<CodeAction[]> => {
        const textDocURI = URI.parse(params.textDocument.uri);
        const document = services.shared.workspace.LangiumDocuments.getDocument(textDocURI);
        if (!document) return [];
        const content = document.textDocument.getText();

        if (content.includes('sbml')) {
            return [
                {
                    title: 'Generate SBML stubs',
                    kind: 'quickfix',
                    command: Command.create('Generate SBML stubs', 'pblang/generateStubs', [params.textDocument.uri])
                }
            ];
        }
        return [];
    });
}