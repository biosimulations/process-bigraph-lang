"""Value-level helpers shared by the v2 reader, writer, printer and normalizer (no bigraph imports)."""

from __future__ import annotations

import re
from typing import Any, Final

import numpy as np


class _Missing:
    """The absence of a value: a store with no state, a type with no default, ... (distinct from `None`)."""

    _instance: _Missing | None = None

    def __new__(cls) -> _Missing:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __repr__(self) -> str:
        return "MISSING"

    def __bool__(self) -> bool:
        return False


MISSING: Final = _Missing()

EDGE_KINDS: Final = ("process", "step", "shared_process", "shared_process_ref")
RUNTIME_EDGE_KEYS: Final = ("instance", "_contract")
EDGE_NODE_KEYS: Final = (
    "_type",
    "address",
    "config",
    "inputs",
    "outputs",
    "_inputs",
    "_outputs",
    "interval",
    "priority",
    "_triggers",
)
COMPOSITE_OPTION_KEYS: Final = (
    "global_time_precision",
    "run_steps_on_init",
    "parallel_steps",
    "parallel_processes",
    "parallel_workers",
    "skip_process_state",
    "contract_strict",
)

PARAM_FULL: Final = re.compile(r"^\$\{([A-Za-z_][A-Za-z0-9_]*)\}$")
PARAM_INLINE: Final = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")
IDENTIFIER: Final = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def is_site(value: Any) -> bool:
    """A template site: `{"_type": "site", "_sort": ..., "_default"?: ...}`."""
    return isinstance(value, dict) and value.get("_type") == "site"


def is_edge_node(value: Any) -> bool:
    """A step/process node in the state half (its `_type` says so, or it carries an `address`)."""
    return isinstance(value, dict) and (value.get("_type") in EDGE_KINDS or "address" in value)


def contains_edge_or_site(value: Any) -> bool:
    """Whether a state subtree holds an edge or a site anywhere below (such a dict is a `node`, not a store value)."""
    if is_edge_node(value) or is_site(value):
        return True
    if isinstance(value, dict):
        return any(contains_edge_or_site(v) for v in value.values())
    return False


def is_identifier(key: Any) -> bool:
    return isinstance(key, str) and IDENTIFIER.match(key) is not None


def is_array(value: Any) -> bool:
    return isinstance(value, np.ndarray)


def element_count(value: Any) -> int:
    """The number of scalar leaves in an array or (nested) list."""
    if isinstance(value, np.ndarray):
        return int(value.size)
    if isinstance(value, (list, tuple)):
        return sum(element_count(v) for v in value)
    return 1
