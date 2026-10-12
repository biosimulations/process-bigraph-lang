from copy import deepcopy
from typing import Any

import numpy as np
import process_bigraph as pg  # type: ignore[import-untyped]
import pytest

from process_bigraph_lang.v2 import deep_equal, diff_documents, equivalent, normalize_document
from tests.v2.helpers import load_corpus_json

# pairs that spell the same thing differently and must collide after normalization
PAIRS: list[tuple[dict[str, Any], dict[str, Any]]] = [
    ({"schema": {"x": "float{3.5}"}, "state": {}}, {"schema": {"x": {"_type": "float", "_default": 3.5}}, "state": {}}),
    ({"schema": {"m": "map[string,float]"}, "state": {}}, {"schema": {"m": "map[float]"}, "state": {}}),
    ({"schema": {"a": "array[float]"}, "state": {}}, {"schema": {"a": "array[1,float]"}, "state": {}}),
    ({"schema": {"pt": "x:float|y:float"}, "state": {}}, {"schema": {"pt": {"x": "float", "y": "float"}}, "state": {}}),
    # a schema-only store equals the store holding the default process-bigraph materializes
    ({"schema": {"C": "float"}, "state": {}}, {"schema": {"C": "float"}, "state": {"C": 0.0}}),
    # the default interval is not a difference; neither are string wires or dict addresses
    (
        {"schema": {}, "state": {"e": {"_type": "step", "address": "local:X", "inputs": {"a": "A"}}}},
        {
            "schema": {"e": {"_type": "step"}},
            "state": {"e": {"address": {"protocol": "local", "data": "X"}, "inputs": {"a": ["A"]}}},
        },
    ),
    (
        {"schema": {}, "state": {"p": {"_type": "process", "address": "local:X"}}},
        {"schema": {}, "state": {"p": {"_type": "process", "address": "local:X", "interval": 1.0, "config": {}}}},
    ),
    # tuples equal lists, arrays equal nested lists, runtime keys are dropped
    (
        {"schema": {}, "state": {"v": (1, 2), "a": np.zeros((2, 2)), "global_time": 3.0}},
        {"schema": {}, "state": {"v": [1, 2], "a": [[0.0, 0.0], [0.0, 0.0]]}},
    ),
]


@pytest.mark.parametrize(("a", "b"), PAIRS)
def test_spellings_collide(a: dict[str, Any], b: dict[str, Any], core: Any) -> None:
    assert equivalent(a, b, core), diff_documents(a, b, core)


def test_differences_are_reported(core: Any) -> None:
    a = {
        "schema": {"x": "float"},
        "state": {"x": 1.0, "p": {"_type": "process", "address": "local:X", "interval": 0.5}},
    }
    b = {
        "schema": {"x": "float"},
        "state": {"x": 2.0, "p": {"_type": "process", "address": "local:Y", "interval": 0.5}},
    }
    assert not equivalent(a, b, core)
    report = diff_documents(a, b, core)
    assert "~ state/x: 1.0 -> 2.0" in report
    assert "~ state/p/address" in report


def test_unknown_dict_form_type_falls_back_to_canonical_dict(core: Any) -> None:
    doc = {"schema": {"f": {"_type": "positive_array", "_shape": (2, 2), "_data": "float"}}, "state": {}}
    normalized = normalize_document(doc, core)
    assert normalized["schema"]["f"] == {"_data": "float", "_shape": [2, 2], "_type": "positive_array"}


def test_saved_document_equals_authoring_document(core: Any) -> None:
    authoring: dict[str, Any] = load_corpus_json("v1/toy_process.json")
    del authoring["state"]["print_result"]  # the file-writing step is not needed here
    composite = pg.Composite(deepcopy(authoring), core=core)
    saved = {"state": composite.serialize_state(), "schema": composite.serialize_schema()}
    assert "global_time" in saved["state"]
    assert equivalent(saved, authoring, core), diff_documents(saved, authoring, core)


def test_deep_equal_modes() -> None:
    assert deep_equal((1, 2.0), [1, 2])
    assert not deep_equal((1, 2.0), [1, 2], strict=True)
    assert deep_equal(np.array([1.0, 2.0]), [1, 2])
    assert not deep_equal(1.0, 1.0 + 1e-6)
    assert deep_equal({"a": [1, {"b": 2}]}, {"a": [1, {"b": 2}]}, strict=True)
    assert not deep_equal(True, 1)
