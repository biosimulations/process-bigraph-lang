"""
The `.pblang` v2 round-trip prototype.

The v2 language is a tree-shaped, verifiable projection of a process-bigraph composite document
(see `docs/v2/design.md`). This package holds the abstract model the language denotes and the
tools that move between it and the documents process-bigraph runs:

- `reader`: `{"schema", "state"}` document (authoring or saved form) or a CompositeSpec mapping -> `Document`
- `writer`: `Document` -> document or CompositeSpec mapping
- `printer`: `Document` -> canonical `.pblang` v2 text (plus sidecar assets for large values)
- `normalize`: equivalence of two documents modulo representation

There is no v2 text parser yet: the model is the round-trip pivot, and the printed text is for
human review and for seeding the Langium v2 grammar.
"""

from process_bigraph_lang.v2.normalize import deep_equal, diff_documents, equivalent, normalize_document
from process_bigraph_lang.v2.printer import print_document
from process_bigraph_lang.v2.reader import read_composite_spec, read_document
from process_bigraph_lang.v2.writer import write_composite_spec, write_document

__all__ = [
    "deep_equal",
    "diff_documents",
    "equivalent",
    "normalize_document",
    "print_document",
    "read_composite_spec",
    "read_document",
    "write_composite_spec",
    "write_document",
]
