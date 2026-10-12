"""
The `.pblang` v2 language, Python side.

The v2 language is a tree-shaped, verifiable projection of a process-bigraph composite document
(see `docs/v2/design.md`). The grammar, the checker, the compiler and the decompiler are TypeScript (`dsl/`),
run here through `cli-native`; this package is the Python entry to them, plus what has to be Python:

- `compile_text` / `compile_file`: `.pbl` text -> parsed, checked -> a `{"schema", "state"}` document or a
  CompositeSpec mapping (`CompileError` when the checker finds errors)
- `decompile`: a document or a CompositeSpec mapping -> canonical `.pbl` text plus sidecar assets
- `check_file` / `check_text`: the checker's findings (`Diagnostic`s)
- `describe_module` / `InterfaceRegistry`: interface declarations ("headers") from a package's classes, as the
  JSON manifest the CLI reads; `render_interfaces` has the CLI print the `.pbl` header file
- `normalize_document` / `equivalent` / `diff_documents`: equivalence of two documents modulo representation

There is no Python model of a composite: a Python tool that builds composites targets the DSL text.
"""

from process_bigraph_lang.v2.api import (
    CompileError,
    Compiled,
    Printed,
    compile_file,
    compile_text,
    decompile,
    dumps,
    loads,
    read_json,
    write_json,
)
from process_bigraph_lang.v2.check import Diagnostic, check_file, check_text
from process_bigraph_lang.v2.interfaces import InterfaceRegistry, describe_module, render_interfaces
from process_bigraph_lang.v2.normalize import deep_equal, diff_documents, equivalent, normalize_document

__all__ = [
    "CompileError",
    "Compiled",
    "Diagnostic",
    "InterfaceRegistry",
    "Printed",
    "check_file",
    "check_text",
    "compile_file",
    "compile_text",
    "decompile",
    "deep_equal",
    "describe_module",
    "diff_documents",
    "dumps",
    "equivalent",
    "loads",
    "normalize_document",
    "read_json",
    "render_interfaces",
    "write_json",
]
