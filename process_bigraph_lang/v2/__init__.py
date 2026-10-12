"""
The `.pblang` v2 language, Python side.

The v2 language is a tree-shaped, verifiable projection of a process-bigraph composite document
(see `docs/v2/design.md`). The grammar and the checker are TypeScript (`dsl/`), run here through `cli-native`;
this package is the Python entry to them:

- `compile_text` / `compile_file`: `.pbl` text -> parsed, checked -> a `{"schema", "state"}` document or a
  CompositeSpec mapping (`CompileError` when the checker finds errors)
- `decompile`: a document or a CompositeSpec mapping -> canonical `.pbl` text plus sidecar assets
- `check_file`: the checker's findings for a `.pbl` file (`Diagnostic`s)
- `describe_module` / `InterfaceRegistry`: interface declarations ("headers") from a package's classes, as a
  JSON manifest the checker reads and as `.pbl` header text (`print_interfaces`)
- `normalize_document` / `equivalent` / `diff_documents`: equivalence of two documents modulo representation

The dataclass model (`model.py`) and its reader, writer and printer are the pivot of the compile and decompile
paths and are internal: there is no public way to a runnable document that skips the text and the checker.
"""

from process_bigraph_lang.v2.api import (
    Compiled,
    CompileError,
    asset_loader,
    compile_file,
    compile_text,
    decode_asset,
    decompile,
)
from process_bigraph_lang.v2.check import Diagnostic, check_file
from process_bigraph_lang.v2.interfaces import InterfaceRegistry, describe_module
from process_bigraph_lang.v2.normalize import deep_equal, diff_documents, equivalent, normalize_document
from process_bigraph_lang.v2.printer import print_interfaces

__all__ = [
    "CompileError",
    "Compiled",
    "Diagnostic",
    "InterfaceRegistry",
    "asset_loader",
    "check_file",
    "compile_file",
    "compile_text",
    "decode_asset",
    "decompile",
    "deep_equal",
    "describe_module",
    "diff_documents",
    "equivalent",
    "normalize_document",
    "print_interfaces",
]
