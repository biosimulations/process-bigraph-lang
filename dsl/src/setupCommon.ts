import getEditorServiceOverride from "@codingame/monaco-vscode-editor-service-override";
import getKeybindingsServiceOverride from "@codingame/monaco-vscode-keybindings-service-override";
import { LanguageClientConfig } from "monaco-editor-wrapper";
import { useOpenEditorStub } from "monaco-editor-wrapper/vscode/services";
import { useWorkerFactory } from "monaco-editor-wrapper/workerFactory";

/** The composite the demo editors start with: two numbers added every time step, one operand left open. */
export const SAMPLE_PBLANG = `// A process bigraph: two numbers are added every time step.

// the header of the process, as a generated interface file would declare it
process AddFloats at "local:!tests.fixtures.test_registry.toy_library.AddFloatsProcess" {
  inputs { left_hand_addend: float; right_hand_addend: float; }
  outputs { result: float; }
}

// an interface: wired here, the implementation is chosen when the template is filled
step Report {
  config { label: string; }
  inputs { value: float; }
}

composite demo {
  store a: float = 2.07;
  store b: float = ?(3.5);     // open, default 3.5
  store total: float = 0.0;

  process add : AddFloats every 1.0 {
    inputs { left_hand_addend -> a, right_hand_addend -> b }
    outputs { result -> total }
  }
  step report : Report at ? {   // the address is an open site
    config { label = ? }
    inputs { value -> total }
  }
}

emit ram { total };
`;

export const defineUserServices = () => {
  return {
    userServices: {
      ...getEditorServiceOverride(useOpenEditorStub),
      ...getKeybindingsServiceOverride(),
    },
    debugLogging: true,
  };
};

export const configureMonacoWorkers = () => {
  // override the worker factory with your own direct definition
  useWorkerFactory({
    ignoreMapping: true,
    workerLoaders: {
      editorWorkerService: () =>
        new Worker(
          new URL(
            "monaco-editor/esm/vs/editor/editor.worker.js",
            import.meta.url,
          ),
          { type: "module" },
        ),
    },
  });
};

export const configureWorker = (): LanguageClientConfig => {
  // vite does not extract the worker properly if it is URL is a variable
  const lsWorker = new Worker(
    new URL("./language/main-browser", import.meta.url),
    {
      type: "module",
      name: "ProcessBigraphLanguage Language Server",
    },
  );

  return {
    options: {
      $type: "WorkerDirect",
      worker: lsWorker,
    },
  };
};
