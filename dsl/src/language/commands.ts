import { Connection, ExecuteCommandParams } from 'vscode-languageserver';
import { URI } from 'langium';
import * as fs from 'fs/promises';
import * as path from 'path';
import {generateStubPblang, parseSBML} from "./sbml.js";

export function registerGenerateStubCommand(connection: Connection) {
    connection.onExecuteCommand(async (params: ExecuteCommandParams) => {
        if (params.command === 'pblang/generateStub') {
            const result = await handleGenerateStubCommand(params.arguments);
            connection.window.showInformationMessage(result ? 'Stub generation succeeded!' : 'Stub generation failed.');
        }
    });
}

async function handleGenerateStubCommand(args: any[] | undefined): Promise<boolean> {
    try {
        const pblangFiles = args || [];
        for (const fileUri of pblangFiles) {
            console.log(`Processing SBML file: ${fileUri}`);
            const filePath = URI.parse(fileUri).fsPath;
            const fileText = await fs.readFile(filePath, 'utf-8');

            const isSbmlFile = fileText.indexOf("<sbml") >= 0;
            if (!isSbmlFile) {
                console.error(`SBML file: ${fileUri} did not contain <sbml> tag.`);
                return false;
            }
            const sbmlContent = parseSBML(fileText);
            if (!sbmlContent) {
                console.error(`Failed to parse SBML content from file: ${fileUri}`);
                return false;
            }

            const sbmlModelName = path.basename(filePath).replace('.sbml', '').replace('.xml', '');
            const stubPath = path.resolve(path.dirname(filePath), 'generated', `${path.basename(filePath, '.sbml_stub')}.pblang`);
            const relativePath = path.relative(path.dirname(stubPath), filePath);
            const stubPblang = generateStubPblang(sbmlContent, sbmlModelName, relativePath);

            if (sbmlContent) {

                await fs.mkdir(path.dirname(stubPath), {recursive: true});
                await fs.writeFile(stubPath, `// Generated SBML Stub\n${stubPblang}`, 'utf-8');
            }
        }
        return true;
    } catch (error) {
        console.error('Error generating stub:', error);
        return false;
    }
}
