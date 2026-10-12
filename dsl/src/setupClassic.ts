import {
  MonacoEditorLanguageClientWrapper,
  UserConfig,
} from "monaco-editor-wrapper";
import {
  configureWorker,
  defineUserServices,
  SAMPLE_PBLANG,
} from "./setupCommon.js";
import monarchSyntax from "./syntaxes/pblang-v2.monarch.js";

export const setupConfigClassic = (): UserConfig => {
  return {
    wrapperConfig: {
      serviceConfig: defineUserServices(),
      editorAppConfig: {
        $type: "classic",
        languageId: "pblang-v2",
        code: SAMPLE_PBLANG,
        useDiffEditor: false,
        languageExtensionConfig: { id: "langium" },
        languageDef: monarchSyntax,
        editorOptions: {
          "semanticHighlighting.enabled": true,
          theme: "vs-dark",
        },
      },
    },
    languageClientConfig: configureWorker(),
  };
};

export const executeClassic = async (htmlElement: HTMLElement) => {
  const userConfig = setupConfigClassic();
  const wrapper = new MonacoEditorLanguageClientWrapper();
  await wrapper.initAndStart(userConfig, htmlElement);
};
