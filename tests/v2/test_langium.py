"""Every snapshot reads back through the Langium grammar into a model that prints to the same text."""

from pathlib import Path

import pytest

from process_bigraph_lang.v2.langium import langium_cli, read_langium, read_text
from process_bigraph_lang.v2.printer import print_document, print_interfaces, print_model
from tests.v2.helpers import REGISTRY, SNAPSHOTS

pytestmark = pytest.mark.skipif(langium_cli() is None, reason="no Langium CLI (build dsl/ or install cli-native)")

SNAPSHOT_FILES = sorted(SNAPSHOTS.glob("*.pbl"))


def _print(document, name: str) -> str:  # type: ignore[no-untyped-def]
    if document.models and not document.root.children and not document.interfaces:
        return "".join(print_model(m) for m in document.models)
    if document.interfaces and not document.root.children:
        return print_interfaces(document.interfaces, document.module or name)
    return print_document(document, name=name, registry=REGISTRY).text


@pytest.mark.parametrize("path", SNAPSHOT_FILES, ids=[p.name for p in SNAPSHOT_FILES])
def test_snapshot_prints_back_identically(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    document = read_langium(path, registry=REGISTRY)
    printed = _print(document, path.stem)
    # model headers and interface files are regenerated from data; composites are a fixpoint of the printer
    comparable = "\n".join(line for line in printed.splitlines() if not line.startswith("//"))
    expected = "\n".join(line for line in text.splitlines() if not line.startswith("//"))
    assert comparable == expected


def test_langium_reads_a_filled_model_site(tmp_path: Path) -> None:
    source = tmp_path / "demo.pbl"
    source.write_text(
        """
import pkg.mod.{Grow};
model ODE { time @ "?T"; species { _: float @ "?U"; ... } meta { events = 0 } }
model Demo from "demo.xml" { time @ "s"; species { A: float @ "uM" = 1.0; } }
composite demo {
  store m : ODE = Demo;
  process g : Grow every 0.5 { config { rate = 0.1, every = 2 } inputs { mass -> ../cell.mass[0] } }
}
""",
        encoding="utf-8",
    )
    document = read_langium(source)
    assert [m.name for m in document.models] == ["ODE", "Demo"] and document.models[0].is_sort
    store = document.root.children["m"]
    assert getattr(store, "value").name == "Demo"  # a ModelRef
    g = document.root.children["g"]
    assert str(getattr(g, "address")) == "local:!pkg.mod.Grow" and getattr(g, "config")["every"] == 2
    assert getattr(g, "inputs")["mass"].to_document() == ["..", "cell", "mass", 0]
    assert print_document(document).text == print_document(read_text(source.read_text(encoding="utf-8"))).text
