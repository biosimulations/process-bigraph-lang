import pytest

from process_bigraph_lang.v2.paths import Path, parse_path, wire_from_document, wire_to_document


@pytest.mark.parametrize(
    ("wire", "text"),
    [
        (["A"], "A"),
        (["fields", "acetate"], "fields.acetate"),
        (["fields", "acetate", 0, 1], "fields.acetate[0][1]"),
        (["..", "A"], "../A"),
        (["..", "..", "x"], "../../x"),
        ([".."], ".."),
        (["*"], "*"),
        (["dFBA[0,0]", "mass"], '"dFBA[0,0]".mass'),
    ],
)
def test_path_text_round_trip(wire: list[str | int], text: str) -> None:
    path = Path.from_document(wire)
    assert path.to_text() == text
    assert parse_path(text) == path
    assert path.to_document() == wire


def test_string_wire_is_one_step() -> None:
    assert Path.from_document("A").steps == ["A"]


def test_nested_wires() -> None:
    wire = {"substrates": {"glucose": ["fields", "glucose"], "acetate": "fields"}}
    model = wire_from_document(wire)
    assert isinstance(model, dict)
    assert wire_to_document(model) == {"substrates": {"glucose": ["fields", "glucose"], "acetate": ["fields"]}}
