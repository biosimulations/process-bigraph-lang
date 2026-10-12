"""
Text-level round trip: every committed snapshot compiles to a document equivalent to the corpus original, and
the language's constructs (params, sites, interfaces, ports, paths) compile to the document forms they denote.
"""

from copy import deepcopy
from typing import Any

import pytest
import yaml
from process_bigraph.processes.growth_division import grow_divide_agent  # type: ignore[import-untyped]

from process_bigraph_lang.v2 import compile_file, compile_text, deep_equal, diff_documents, equivalent
from process_bigraph_lang.v2.langium import langium_cli
from tests.compiler.generator.spatio_flux.test_spatio_flux_II import step_config_template as spatio_two
from tests.compiler.generator.spatio_flux.test_spatio_flux_III import step_config_template as spatio_three
from tests.v2.helpers import CORPUS, REGISTRY, SNAPSHOTS, load_corpus_json

pytestmark = pytest.mark.skipif(langium_cli() is None, reason="no Langium CLI (build dsl/ or install cli-native)")


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
def test_snapshot_text_compiles_to_the_original(name: str, spatio_core: Any) -> None:
    written = compile_file(SNAPSHOTS / f"{name}.pbl", registry=REGISTRY, force=True).document
    original = _original(name)
    # `_inputs`/`_outputs` that repeat an imported interface's face are not a difference
    assert equivalent(original, written, spatio_core, REGISTRY), diff_documents(
        original, written, spatio_core, registry=REGISTRY
    )


def test_composite_spec_text_compiles_to_the_original(core: Any) -> None:
    spec = yaml.safe_load((CORPUS / "reversible-dimerization.composite.yaml").read_text(encoding="utf-8"))
    back = compile_file(SNAPSHOTS / "reversible-dimerization.pbl", to="spec").document
    for key in ("name", "description", "tags", "requires", "emitters"):
        assert deep_equal(back[key], spec[key])
    assert equivalent({"state": spec["state"]}, {"state": back["state"]}, core)


def test_saved_toy_text_compiles_without_a_face_of_its_own() -> None:
    document = compile_file(SNAPSHOTS / "saved_toy_add_floats.pbl", registry=REGISTRY).document
    add = document["state"]["add_nums"]
    # an imported interface is authoritative at runtime: the edge carries no `_inputs`/`_outputs` of its own
    assert "_inputs" not in add and "_outputs" not in add
    assert add["address"] == "local:!tests.fixtures.test_registry.toy_library.AddFloatsProcess"


def test_params_sites_and_interfaces_compile_to_their_document_forms() -> None:
    spec = compile_text(
        """
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
    """,
        to="spec",
    ).document
    assert spec["name"] == "demo" and spec["description"] == "the model"
    assert spec["parameters"] == {
        "rate": {"type": "float", "default": 0.1, "description": "how fast", "choices": [0.1, 0.5]},
        "n": {"type": "integer"},
    }
    state = spec["state"]
    assert state["x"] == {"_type": "site", "_sort": "float", "_default": 1.0}
    assert "x" not in spec.get("schema", {})  # an open store has no schema entry
    assert state["label"] == "run_${n}"
    assert spec["schema"]["cell"] == {"m": "float"} and state["cell"] == {"m": 2.0}
    g = state["g"]
    assert g["address"] == "local:!pkg.mod.Grow" and g["interval"] == "${rate}"
    assert g["config"] == {"k": {"_type": "site", "_sort": "integer"}, "name": "g"}
    e = state["e"]
    assert e["address"] == {
        "_type": "site",
        "_sort": {"_type": "link", "_inputs": {"x": "float"}, "_outputs": {"y": "float"}},
    }
    assert e["_inputs"] == {"x": "float"} and e["_outputs"] == {"y": "float"}
    s = state["s"]
    assert s["priority"] == 2 and s["_inputs"] == {"a": "list[float]"} and s["inputs"]["a"] == ["..", "up", "a", 0]
    assert spec["emitters"] == [{"address": "local:RAMEmitter", "paths": ["x", "cell/m"]}]
