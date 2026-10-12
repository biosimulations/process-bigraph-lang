import numpy as np

from process_bigraph_lang.v2 import print_document, read_document, write_document
from process_bigraph_lang.v2.model import Composite, Document, Edge, ExternalRef, Store
from process_bigraph_lang.v2.printer import _float, _scalar
from process_bigraph_lang.v2.types import Named
from tests.v2.helpers import asset_loader


def test_scalars() -> None:
    assert _scalar(None) == "null" and _scalar(True) == "true" and _scalar(3) == "3"
    assert _scalar('a"b') == '"a\\"b"'
    assert _float(1.0) == "1.0" and _float(2.5e-3) == "0.0025" and _float(1e-07) == "1.0e-07"
    assert _float(np.float64(0.1)) == "0.1"


def test_struct_and_map_literals_and_quoting() -> None:
    doc = read_document({"schema": {}, "state": {"cfg": {"a": {"b": 1}, "k-1": 2}, "dFBA[0,0]": 1.5, "t": (1, 2)}})
    text = print_document(doc).text
    assert 'store cfg = { "a" = { b = 1 }, "k-1" = 2 };' in text  # one non-identifier key makes it a map literal
    assert 'store "dFBA[0,0]" = 1.5;' in text
    assert "store t = (1, 2);" in text


def test_blocks_break_when_too_wide() -> None:
    config = {f"key_{i}": f"value number {i}" for i in range(8)}
    doc = read_document({"schema": {}, "state": {"e": {"_type": "step", "address": "local:X", "config": config}}})
    text = print_document(doc).text
    assert '    config {\n      key_0 = "value number 0",\n' in text
    assert text.endswith("}\n")


def test_interfaces_are_declared_once_and_named_by_address() -> None:
    edge = {"_type": "process", "_inputs": {"a": "float"}, "address": "local:!pkg.mod.Add"}
    other = {"_type": "process", "_inputs": {"b": "float"}, "address": "local:!pkg.mod.Add"}
    doc = read_document({"schema": {}, "state": {"one": edge, "two": dict(edge), "three": other}})
    text = print_document(doc).text
    assert text.count('process Add at "local:!pkg.mod.Add" {') == 1
    assert 'process Add_2 at "local:!pkg.mod.Add" {' in text
    assert "process one : Add {" in text and "process three : Add_2 {" in text


def test_edges_without_ports_use_at() -> None:
    doc = read_document({
        "schema": {},
        "state": {"em": {"_type": "step", "address": "local:RAMEmitter", "inputs": {"a": ["A"]}}},
    })
    text = print_document(doc).text
    assert 'step em at "local:RAMEmitter" {\n    inputs { a -> A }\n  }' in text


def test_sites_print_as_open_values() -> None:
    doc = read_document({
        "schema": {},
        "state": {
            "rate": {"_type": "site", "_sort": "float", "_default": 0.5},
            "s": {
                "_type": "process",
                "address": {"_type": "site", "_sort": "link[x:float,y:float]"},
                "config": {"k": {"_type": "site", "_sort": "integer"}},
            },
        },
    })
    text = print_document(doc).text
    assert "store rate: float = ?(0.5);" in text
    assert "process s at ? {" in text and "config { k = ? as int }" in text


def test_large_values_are_externalized_and_reloadable() -> None:
    big = np.arange(500, dtype=np.float64).reshape(5, 100)
    long_text = "x" * 2000
    doc = read_document({
        "schema": {},
        "state": {"fields": {"A": big}, "e": {"_type": "step", "address": "local:X", "config": {"text": long_text}}},
    })
    printed = print_document(doc, name="demo")
    assert 'A = array(file("demo.assets/fields_A.json"), dtype = "float64", shape = [5, 100])' in printed.text
    assert 'text = file("demo.assets/e_text.txt")' in printed.text
    assert set(printed.assets) == {"demo.assets/fields_A.json", "demo.assets/e_text.txt"}
    # the model now carries ExternalRefs only inside the printer; the writer resolves them through a loader
    model = Document(
        root=Composite({
            "A": Store("A", value=ExternalRef("demo.assets/fields_A.json", "array", "float64", (5, 100))),
            "e": Edge("e", "step", config={"text": ExternalRef("demo.assets/e_text.txt", "text")}),
        })
    )
    written = write_document(model, assets=asset_loader(printed))
    assert np.array_equal(written["state"]["A"], big) and written["state"]["e"]["config"]["text"] == long_text


def test_small_arrays_print_inline() -> None:
    doc = read_document({"schema": {"a": "array[float]"}, "state": {"a": np.array([1.0, 2.0])}})
    assert 'store a: array<float> = array([1.0, 2.0], dtype = "float64");' in print_document(doc).text


def test_typed_store_declaration_without_value() -> None:
    doc = Document(root=Composite({"C": Store("C", type=Named("float"))}))
    assert "store C: float;" in print_document(doc).text
