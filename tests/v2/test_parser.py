"""
Text-level round trip: every committed snapshot parses back into a model that prints to the same text and
writes a document equivalent to the corpus original.
"""

from copy import deepcopy
from typing import Any

import pytest
import yaml
from process_bigraph.processes.growth_division import grow_divide_agent  # type: ignore[import-untyped]

from process_bigraph_lang.v2 import (
    deep_equal,
    diff_documents,
    equivalent,
    print_document,
    write_composite_spec,
    write_document,
)
from process_bigraph_lang.v2.model import Edge, ParamRef, Site, Store
from process_bigraph_lang.v2.parser import read_text
from tests.compiler.generator.spatio_flux.test_spatio_flux_II import step_config_template as spatio_two
from tests.compiler.generator.spatio_flux.test_spatio_flux_III import step_config_template as spatio_three
from tests.v2.helpers import CORPUS, REGISTRY, SNAPSHOTS, load_corpus_json, snapshot_asset_loader

DOCUMENT_SNAPSHOTS = [
    "hybrid_two_way_exchange",
    "growth_division",
    "spatio_flux_II",
    "spatio_flux_III",
    "template_sites",
]


def _original(name: str) -> dict[str, Any]:
    if name == "hybrid_two_way_exchange":
        return load_corpus_json("hybrid_two_way_exchange.json")
    if name == "growth_division":
        return {"schema": {}, "state": {"agent": grow_divide_agent(path=["agent"]), "environment": {}}}
    if name == "spatio_flux_II":
        return deepcopy(spatio_two)
    if name == "spatio_flux_III":
        return deepcopy(spatio_three)
    return load_corpus_json("template_sites.json")


@pytest.mark.parametrize("name", DOCUMENT_SNAPSHOTS)
def test_snapshot_text_round_trips(name: str, spatio_core: Any) -> None:
    text = (SNAPSHOTS / f"{name}.pblang").read_text()
    model = read_text(text, registry=REGISTRY)
    assert print_document(model, name=name, registry=REGISTRY).text == text  # the printer is a fixpoint
    written = write_document(model, assets=snapshot_asset_loader())
    original = _original(name)
    assert equivalent(original, written, spatio_core), diff_documents(original, written, spatio_core)


def test_composite_spec_text_round_trips(core: Any) -> None:
    text = (SNAPSHOTS / "reversible-dimerization.pblang").read_text()
    model = read_text(text)
    assert print_document(model, name="reversible-dimerization").text == text
    spec = yaml.safe_load((CORPUS / "reversible-dimerization.composite.yaml").read_text())
    back = write_composite_spec(model)
    for key in ("name", "description", "tags", "requires", "emitters"):
        assert deep_equal(back[key], spec[key]), key
    assert equivalent({"state": spec["state"]}, {"state": back["state"]}, core)


def test_saved_toy_text_round_trips() -> None:
    text = (SNAPSHOTS / "saved_toy_add_floats.pblang").read_text()
    model = read_text(text, registry=REGISTRY)
    assert print_document(model, name="saved_toy_add_floats", registry=REGISTRY).text == text
    add = model.root.children["add_nums"]
    assert isinstance(add, Edge) and add.ports is not None and add.ports.inputs is not None
    assert str(add.address) == "local:!tests.fixtures.test_registry.toy_library.AddFloatsProcess"


def test_parses_params_sites_and_interfaces() -> None:
    model = read_text("""
        // a comment
        import pkg.mod.{Grow};
        /// how fast
        param rate: float = 0.1 choices [0.1, 0.5];
        param n: int = ?;
        process Engine { inputs { x: float; } outputs { y: float; } }
        /// the model
        composite demo {
          store x: float = ?(1.0);
          store label: string = "run_${n}";
          node cell : { m: float; } {
            store m: float = 2.0;
          }
          process g : Grow every ${rate} { config { k = ? as int, name = "g" } inputs { m -> cell.m } }
          process e : Engine at ? { outputs { y -> x } }
          step s at "local:S" priority 2 { ports { inputs { a: list<float>; } } inputs { a -> ../up.a[0] } }
        }
        emit ram { x, cell.m };
    """)
    assert [p.name for p in model.params] == ["rate", "n"]
    assert model.params[0].description == "how fast" and model.params[0].choices == [0.1, 0.5]
    assert model.name == "demo" and model.description == "the model"
    x = model.root.children["x"]
    assert isinstance(x, Store) and x.site is not None and x.site.default == 1.0
    label = model.root.children["label"]
    assert isinstance(label, Store) and label.value == ParamRef("n", "run_${n}")
    g = model.root.children["g"]
    assert isinstance(g, Edge) and str(g.address) == "local:!pkg.mod.Grow" and g.interval == ParamRef("rate")
    assert g.config["name"] == "g" and g.config["k"] == {"_type": "site", "_sort": "integer"}
    e = model.root.children["e"]
    assert isinstance(e, Edge) and isinstance(e.address, Site) and e.ports is not None and e.ports.outputs is not None
    s = model.root.children["s"]
    assert isinstance(s, Edge) and s.priority == 2 and s.ports is not None and s.ports.inputs is not None
    assert s.inputs["a"].to_document() == ["..", "up", "a", 0]  # type: ignore[union-attr]
    assert str(model.emitters[0].address) == "local:RAMEmitter" and model.emitters[0].paths[1].to_slash() == "cell/m"
