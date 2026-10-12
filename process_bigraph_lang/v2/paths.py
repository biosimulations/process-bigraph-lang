"""Wire paths: the document's list form (`["..", "fields", "A", 0, 1]`) and the DSL's text form (`../fields.A[0][1]`)."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from process_bigraph_lang.v2.values import is_identifier


@dataclass
class Path:
    """A wire target, relative to the edge's parent. Steps are keys, integer indices, `..` or `*`."""

    steps: list[str | int] = field(default_factory=list)

    @classmethod
    def from_document(cls, wire: Any) -> Path:
        """A document wire: a list of steps, or a bare string (a one-step path)."""
        if isinstance(wire, str):
            return cls([wire])
        if isinstance(wire, (list, tuple)):
            return cls([_step(s) for s in wire])
        raise TypeError(f"not a wire path: {wire!r}")

    def to_document(self) -> list[str | int]:
        return list(self.steps)

    def to_text(self) -> str:
        """`../fields.A[0][1]`: `..` segments end with `/`, keys are joined by `.`, indices are `[i]`."""
        text = ""
        previous: str | int | None = None
        for step in self.steps:
            if isinstance(step, int):
                text += f"[{step}]"
            else:
                token = step if step in ("..", "*") or is_identifier(step) else _quote(step)
                if previous is None:
                    text += token
                elif previous == "..":
                    text += f"/{token}"
                else:
                    text += f".{token}"
            previous = step
        return text

    def to_slash(self) -> str:
        """`a/b/0`: the form `fill_sites` and CompositeSpec `emitters.paths` use."""
        return "/".join(str(s) for s in self.steps)


Wire = Path | dict[str, "Wire"]


def wire_from_document(wire: Any) -> Wire:
    """A document wire: a path, or a dict of sub-port wires."""
    if isinstance(wire, dict):
        return {str(k): wire_from_document(v) for k, v in wire.items()}
    return Path.from_document(wire)


def wire_to_document(wire: Wire) -> Any:
    if isinstance(wire, dict):
        return {k: wire_to_document(v) for k, v in wire.items()}
    return wire.to_document()


_INDEX = re.compile(r"\[(-?\d+)\]")


def parse_path(text: str) -> Path:
    """The inverse of `Path.to_text` (used by tests and the future parser)."""
    steps: list[str | int] = []
    rest = text.strip()
    while rest.startswith("../"):
        steps.append("..")
        rest = rest[3:]
    if rest == "..":
        steps.append("..")
        rest = ""
    for segment in _split_segments(rest):
        if segment.startswith('"'):
            end = segment.find('"', 1)
            while end != -1 and segment[end - 1] == "\\":
                end = segment.find('"', end + 1)
            head, indices = segment[: end + 1], segment[end + 1 :]
        else:
            head, _, indices = segment.partition("[")
            indices = f"[{indices}" if indices else ""
        if head:
            steps.append(_unquote(head))
        for index in _INDEX.findall(indices):
            steps.append(int(index))
    return Path(steps)


def _split_segments(text: str) -> list[str]:
    segments: list[str] = []
    current = ""
    quoted = False
    for char in text:
        if char == '"':
            quoted = not quoted
        if char == "." and not quoted:
            segments.append(current)
            current = ""
        else:
            current += char
    if current or segments:
        segments.append(current)
    return [s for s in segments if s]


def _step(step: Any) -> str | int:
    if isinstance(step, bool):
        return str(step)
    if isinstance(step, int):
        return step
    return str(step)


def _quote(key: str) -> str:
    return '"' + key.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _unquote(key: str) -> str:
    if len(key) >= 2 and key[0] == '"' and key[-1] == '"':
        return key[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    return key
