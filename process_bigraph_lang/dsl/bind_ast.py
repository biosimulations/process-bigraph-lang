"""
Resolve cross-references in an ASTModel.

Langium serializes each reference with the document path of its target, e.g. `#/elements@1/fields@0`
(property `elements`, index 1, then property `fields`, index 0) or `#/elements@2/config/elements@0`
(a single-valued property has no index). Binding follows that path from the model root and stores
the target object in `Reference.ref_object`.
"""

from typing import Any

from pydantic import BaseModel

from process_bigraph_lang.dsl.ast_model import ASTModel, Reference


def resolve_path(model: ASTModel, path: str) -> Any:
    if not path.startswith("#/"):
        raise ValueError(f"Unsupported reference path '{path}'")
    target: Any = model
    for segment in path[2:].split("/"):
        prop, _, index = segment.partition("@")
        target = getattr(target, prop, None)
        if index:
            target = target[int(index)] if isinstance(target, list) and int(index) < len(target) else None
        if target is None:
            raise ValueError(f"Reference path '{path}' does not resolve (at '{segment}')")
    return target


def _references(node: Any) -> list[Reference]:
    if isinstance(node, Reference):
        return [node]
    if isinstance(node, list):
        return [ref for item in node for ref in _references(item)]
    if isinstance(node, BaseModel):
        return [ref for name in type(node).model_fields for ref in _references(getattr(node, name))]
    return []


def bind_ast_model(model: ASTModel) -> None:
    for ref in _references(model):
        if ref.ref is None:
            raise ValueError(f"Unresolved reference '{ref.ref_text}'")
        ref.ref_object = resolve_path(model, ref.ref)
