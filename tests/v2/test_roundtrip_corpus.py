"""
The round-trip corpus: real documents are decompiled to `.pblang` text (snapshot), compiled back and compared.

Each entry checks `equivalent(original, compile(decompile(original)))` under the normalizer, that the printed
text matches the committed `.pblang` snapshot (regenerate with `PBLANG_UPDATE_SNAPSHOTS=1`), and, where the
processes are available here, that process-bigraph realizes both documents to the same thing. Everything runs
through the CLI: there is no Python model in between.
"""

from copy import deepcopy
from typing import Any

import numpy as np
import process_bigraph as pg  # type: ignore[import-untyped]
import pytest
import yaml
from process_bigraph.composite_spec import CompositeSpec  # type: ignore[import-untyped]
from process_bigraph.processes.growth_division import grow_divide_agent  # type: ignore[import-untyped]
from process_bigraph.templates import open_sites, template_document  # type: ignore[import-untyped]

from process_bigraph_lang.v2 import compile_text, decompile, deep_equal, diff_documents, equivalent
from process_bigraph_lang.v2.langium import langium_cli
from tests.fixtures.test_registry.toy_library import AddFloatsProcess
from tests.v2.helpers import CORPUS, REGISTRY, assert_snapshot, load_corpus_json, realized_equivalent

pytestmark = pytest.mark.skipif(langium_cli() is None, reason="no Langium CLI (build dsl/ or install cli-native)")


def _round_trip(name: str, original: dict[str, Any], core: Any) -> dict[str, Any]:
    printed = decompile(deepcopy(original), name=name, registry=REGISTRY)
    assert_snapshot(name, printed)
    # existing documents may rely on config defaults the checker flags as missing (T121): compile anyway
    written = compile_text(printed.text, registry=REGISTRY, assets=printed.assets, force=True).document
    assert equivalent(original, written, core, REGISTRY), diff_documents(original, written, core, registry=REGISTRY)
    return written


# 1. viva-smoldyn reversible dimerization: a CompositeSpec yaml with parameters-free state and emitters


def test_reversible_dimerization_spec(core: Any) -> None:
    spec = yaml.safe_load((CORPUS / "reversible-dimerization.composite.yaml").read_text(encoding="utf-8"))
    printed = decompile(deepcopy(spec), name="reversible-dimerization")
    assert_snapshot("reversible-dimerization", printed)
    back = compile_text(printed.text, to="spec").document
    for key in ("name", "description", "tags", "requires", "emitters"):
        assert deep_equal(back[key], spec[key])
    assert equivalent({"state": spec["state"]}, {"state": back["state"]}, core)
    # process-bigraph's own reading of both specs agrees (SmoldynProcess is not installed here, so no run)
    original_doc = CompositeSpec.from_dict({"id": "a", **spec}).to_document(emit=False)
    written_doc = CompositeSpec.from_dict({"id": "b", **back}).to_document(emit=False)
    assert equivalent(original_doc, written_doc, core), diff_documents(original_doc, written_doc, core)


# 2. viva-pde-particle hybrid: FV PDE + Smoldyn in a Stepper + adapter + recorder (generated fixture, no run)


@pytest.mark.skipif(not (CORPUS / "hybrid_two_way_exchange.json").exists(), reason="fixture not generated")
def test_hybrid_two_way_exchange(core: Any) -> None:
    original = load_corpus_json("hybrid_two_way_exchange.json")
    written = _round_trip("hybrid_two_way_exchange", original, core)
    particles = written["state"]["particles"]
    assert particles["config"]["process"]["address"] == original["state"]["particles"]["config"]["process"]["address"]
    assert deep_equal(
        particles["config"]["process"]["config"], original["state"]["particles"]["config"]["process"]["config"]
    )
    assert np.array_equal(written["state"]["fields"]["B"], original["state"]["fields"]["B"])


# 3. growth-division: a nested composite with a bridge (authoring document; saving one is lossy upstream)


def test_growth_division_nested_composite(core: Any) -> None:
    original = {"schema": {}, "state": {"agent": grow_divide_agent(path=["agent"]), "environment": {}}}
    written = _round_trip("growth_division", original, core)
    assert written["state"]["agent"]["config"]["bridge"] == original["state"]["agent"]["config"]["bridge"]
    assert realized_equivalent(original, written, core)


def test_saved_nested_composite_loses_inner_state(core: Any) -> None:
    original = {"schema": {}, "state": {"agent": grow_divide_agent(path=["agent"]), "environment": {}}}
    composite = pg.Composite(deepcopy(original), core=core)
    saved_agent = composite.serialize_state()["agent"]
    # the upstream trap: the saved nested composite has no inner state; the printer says so
    assert not saved_agent["config"].get("state")
    printed = decompile({"schema": composite.serialize_schema(), "state": composite.serialize_state()})
    assert "inner state lost" in printed.text


# 4. spatio-flux: array-indexed wires, ndarray state, dict-form custom array types (the v1 expected documents)


def test_spatio_flux_grid(spatio_core: Any) -> None:
    written = _round_trip("spatio_flux_II", load_corpus_json("v1/spatio_flux_II.json"), spatio_core)
    assert written["state"]["dFBA[0,1]"]["inputs"]["substrates"]["glucose"] == ["fields", "glucose", 0, 1]


def test_spatio_flux_arrays(spatio_core: Any) -> None:
    original = load_corpus_json("v1/spatio_flux_III.json")
    written = _round_trip("spatio_flux_III", original, spatio_core)
    assert realized_equivalent(original, written, spatio_core)


# 5. template sites: open stores, config sites and an address site; a written template still fills and runs


def test_template_sites(core: Any) -> None:
    _round_trip("template_sites", load_corpus_json("template_sites.json"), core)


TEMPLATE = """
process AddFloats { inputs { left_hand_addend: float; right_hand_addend: float; } outputs { result: float; } }
composite {
  node operands { store a: float = ?; store b: float = ?(3.5); }
  store total: float = 0.0;
  process add : AddFloats at ? every 1.0 {
    inputs { left_hand_addend -> operands.a, right_hand_addend -> operands.b }
    outputs { result -> total }
  }
}
"""


def test_written_template_fills_and_runs() -> None:
    core = pg.allocate_core()
    core.register_link("AddFloatsProcess", AddFloatsProcess)
    written = compile_text(TEMPLATE).document
    assert decompile(deepcopy(written)).text == decompile(compile_text(decompile(written).text).document).text
    template = core.access(written["state"])
    assert sorted(open_sites(template)) == [("add", "address"), ("operands", "a"), ("operands", "b")]
    state = template_document(core, template, {"operands/a": 2.07, "add/address": "local:AddFloatsProcess"})
    composite = pg.Composite({"schema": written["schema"], "state": state}, core=core)
    composite.run(10.0)
    assert np.allclose(composite.state["total"], (2.07 + 3.5) * 10)


# 6. the saved form of the toy add-floats composite


def test_saved_toy_add_floats(core: Any) -> None:
    authoring: dict[str, Any] = load_corpus_json("v1/toy_process.json")
    del authoring["state"]["print_result"]  # the file-writing step would write output.txt
    composite = pg.Composite(deepcopy(authoring), core=core)
    saved = {"schema": composite.serialize_schema(), "state": composite.serialize_state()}
    written = _round_trip("saved_toy_add_floats", saved, core)
    # the edge's face now comes from the imported interface, not from `_inputs`/`_outputs` of its own
    assert equivalent(written, authoring, core, REGISTRY), diff_documents(written, authoring, core, registry=REGISTRY)
