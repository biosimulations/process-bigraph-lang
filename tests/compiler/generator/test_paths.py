import pytest

from process_bigraph_lang.compiler.generator import compute_relative_path


def test_compute_relative_path() -> None:
    assert compute_relative_path(["a", "b", "c"], ["a", "b", "c", "d"]) == [".."]
    assert compute_relative_path(["a"], []) == ["a"]
    assert compute_relative_path(["a", "b", "c"], ["a", "b", "d"]) == ["..", "c"]
    assert compute_relative_path(["a", "b", "c"], ["x", "y", "z"]) == ["..", "..", "..", "a", "b", "c"]

    with pytest.raises(ValueError):
        compute_relative_path(["a", "b"], ["a", "b"])
    with pytest.raises(ValueError):
        compute_relative_path([], [])
    with pytest.raises(ValueError):
        compute_relative_path([], ["a"])
    with pytest.raises(ValueError):
        compute_relative_path([".."], ["a"])
    with pytest.raises(ValueError):
        compute_relative_path([], ["..", "a"])
