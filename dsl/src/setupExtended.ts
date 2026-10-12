import {
  MonacoEditorLanguageClientWrapper,
  UserConfig,
} from "monaco-editor-wrapper";
import {
  configureWorker,
  defineUserServices,
  SAMPLE_PBLANG,
} from "./setupCommon.js";

export const setupConfigExtended = (): UserConfig => {
  const extensionFilesOrContents = new Map();
  extensionFilesOrContents.set(
    "/language-configuration.json",
    new URL("../language-configuration.json", import.meta.url),
  );
  extensionFilesOrContents.set(
    "/pblang-grammar.json",
    new URL("../syntaxes/pblang.tmLanguage.json", import.meta.url),
  );

  return {
    wrapperConfig: {
      serviceConfig: defineUserServices(),
      editorAppConfig: {
        $type: "extended",
        languageId: "pblang",
        code: SAMPLE_PBLANG,
        useDiffEditor: false,
        extensions: [
          {
            config: {
              name: "pblang-web",
              publisher: "generator-langium",
              version: "1.0.0",
              engines: {
                vscode: "*",
              },
              contributes: {
                languages: [
                  {
                    id: "pblang",
                    extensions: [".pblang", ".pbl"],
                    configuration: "./language-configuration.json",
                  },
                ],
                grammars: [
                  {
                    language: "pblang",
                    scopeName: "source.pblang",
                    path: "./pblang-grammar.json",
                  },
                ],
              },
            },
            filesOrContents: extensionFilesOrContents,
          },
        ],
        userConfiguration: {
          json: JSON.stringify({
            "workbench.colorTheme": "Default Dark Modern",
            "editor.semanticHighlighting.enabled": true,
          }),
        },
      },
    },
    languageClientConfig: configureWorker(),
  };
};

export const executeExtended = async (htmlElement: HTMLElement) => {
  const userConfig = setupConfigExtended();
  const wrapper = new MonacoEditorLanguageClientWrapper();
  await wrapper.initAndStart(userConfig, htmlElement);
};
