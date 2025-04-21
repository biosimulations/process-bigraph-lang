import type { Model } from '../language/generated/ast.js';
import chalk from 'chalk';
import { createProcessBigraphLanguageServices } from '../language/process-bigraph-language-module.js';
import { extractAstNode, extractDocument } from './cli-util.js';
import { generateJavaScript } from './generator.js';
import { NodeFileSystem } from 'langium/node';

export const generateAction = async (fileName: string, opts: GenerateOptions): Promise<void> => {
    const services = createProcessBigraphLanguageServices(NodeFileSystem).ProcessBigraphLanguage;
    const model = await extractAstNode<Model>(fileName, services);
    const generatedFilePath = generateJavaScript(model, fileName, opts.destination);
    console.log(chalk.green(`JavaScript code generated successfully: ${generatedFilePath}`));
};

/**
 * Parse and validate a program written in our language.
 * Verifies that no lexer or parser errors occur.
 * Implicitly also checks for validation errors while extracting the document
 *
 * @param fileName Program to validate
 */
export const parseAndValidate = async (fileName: string): Promise<void> => {
    // retrieve the services for our language
    const services = createProcessBigraphLanguageServices(NodeFileSystem).ProcessBigraphLanguage;
    // extract a document for our program
    const document = await extractDocument(fileName, services);
    // extract the parse result details
    const parseResult = document.parseResult;
    // verify no lexer, parser, or general diagnostic errors show up
    if (parseResult.lexerErrors.length === 0 && 
        parseResult.parserErrors.length === 0
    ) {
        console.log(chalk.green(`Parsed and validated ${fileName} successfully!`));
    } else {
        console.log(chalk.red(`Failed to parse and validate ${fileName}!`));
    }
};

export type GenerateOptions = {
    destination?: string;
}

function parseArgs(args: string[]): { command: string; options: Record<string, string>; file?: string } {
    const result: { command: string; options: Record<string, string>; file?: string } = { command: '', options: {} };
    const commands = ['generate', 'parseAndValidate'];
    const optionsRegex = /^--?(.+)/;

    for (let i = 2; i < args.length; i++) {
        const arg = args[i];
        if (commands.includes(arg)) {
            result.command = arg;
        } else if (optionsRegex.test(arg)) {
            const [, key] = arg.match(optionsRegex) || [];
            const value = args[i + 1] && !args[i + 1].startsWith('-') ? args[++i] : '';
            result.options[key] = value;
        } else if (!result.file) {
            result.file = arg;
        }
    }

    return result;
}

const main = function (): void {
    const args = parseArgs(process.argv);

    if (!args.command) {
        console.log(chalk.red('No command provided.'));
        console.log(`Available commands: generate, parseAndValidate`);
        return;
    }

    if (args.command === 'generate') {
        if (!args.file) {
            console.log(chalk.red('No source file provided for the generate command.'));
            return;
        }
        console.log(chalk.green(`Generating for file: ${args.file}`));
        // Call synchronous generate logic here
    } else if (args.command === 'parseAndValidate') {
        if (!args.file) {
            console.log(chalk.red('No source file provided for the parseAndValidate command.'));
            return;
        }
        console.log(chalk.green(`Parsing and validating file: ${args.file}`));
        // Call synchronous parse and validate logic here
    } else {
        console.log(chalk.red(`Unknown command: ${args.command}`));
        console.log(`Available commands: generate, parseAndValidate`);
    }
}

export default main;