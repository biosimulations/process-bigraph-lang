import getEditorServiceOverride from "@codingame/monaco-vscode-editor-service-override";
import getKeybindingsServiceOverride from "@codingame/monaco-vscode-keybindings-service-override";
import { LanguageClientConfig } from "monaco-editor-wrapper";
import { useOpenEditorStub } from "monaco-editor-wrapper/vscode/services";
import { useWorkerFactory } from "monaco-editor-wrapper/workerFactory";

/** The model the demo editors start with. */
export const SAMPLE_PBLANG = `// A process bigraph: two numbers are added every time step.
type float builtin
type string builtin

// a remote process, implemented by a Python class
remote process AddFloats at "tests.fixtures.test_registry.toy_library.AddFloatsProcess" {
    inputs (left_hand_addend: float, right_hand_addend: float)
    outputs (result: float)
}

// an interface: wired here, implementation chosen when the template is filled
remote step Report {
    config (label: string)
    inputs (value: float)
}

struct Operands {
    a: float;
    b: float;
}

// stores
let operands: Operands = { a = 2.07, b = ?(3.5) };   // b is open, default 3.5
store total: float;
init total = 0.0;

// processes, and how they are wired to the stores
let add: AddFloats = AddFloats();
connect add inputs (left_hand_addend = operands.a, right_hand_addend = operands.b)
            outputs (result = total);

let report: Report = Report(label = ?);                // label is open
connect report inputs (value = total);
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
