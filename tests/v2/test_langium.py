"""Every composite snapshot compiles to a document that decompiles to the same text: the text is a fixpoint through the document."""

from pathlib import Path

import pytest

from process_bigraph_lang.v2 import compile_file, decompile
from process_bigraph_lang.v2.langium import langium_cli
from tests.v2.helpers import REGISTRY, SNAPSHOTS

pytestmark = pytest.mark.skipif(langium_cli() is None, reason="no Langium CLI (build dsl/ or install cli-native)")

DOCUMENT_SNAPSHOTS = [
    "growth_division",
    "hybrid_two_way_exchange",
    "saved_toy_add_floats",
    "spatio_flux_II",
    "spatio_flux_III",
    "template_sites",
]


@pytest.mark.parametrize("name", DOCUMENT_SNAPSHOTS)
def test_snapshot_is_a_fixpoint_through_the_document(name: str) -> None:
    path = SNAPSHOTS / f"{name}.pbl"
    document = compile_file(path, registry=REGISTRY, force=True).document
    printed = decompile(document, name=name, registry=REGISTRY)
    assert printed.text == path.read_text(encoding="utf-8")


def test_spec_snapshot_is_a_fixpoint_through_the_composite_spec() -> None:
    path = SNAPSHOTS / "reversible-dimerization.pbl"
    spec = compile_file(path, to="spec").document
    assert decompile(spec, name="reversible-dimerization").text == path.read_text(encoding="utf-8")


def test_a_filled_model_site_compiles(tmp_path: Path) -> None:
    source = tmp_path / "demo.pbl"
    source.write_text(
        """
import pkg.mod.{Grow};
model ODE { time @ "?T"; species { _: float @ "?U"; ... } }
model Demo from "demo.xml" { time @ "s"; species { A: float @ "uM" = 1.0; } }
composite demo {
  store m : ODE = Demo;
  process g : Grow every 0.5 { config { rate = 0.1, every = 2 } inputs { mass -> ../cell.mass[0] } }
}
""",
        encoding="utf-8",
    )
    document = compile_file(source).document
    assert document["state"]["m"] == {"species": {"A": 1.0}}
    assert document["schema"]["m"] == {"species": {"A": {"_type": "float", "_units": "uM"}}}
    g = document["state"]["g"]
    assert g["address"] == "local:!pkg.mod.Grow" and g["config"]["every"] == 2 and g["interval"] == 0.5
    assert g["inputs"]["mass"] == ["..", "cell", "mass", 0]
