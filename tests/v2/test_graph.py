"""A viewer's graph from a document and headers alone (no process code imported), through the CLI."""

import json
from pathlib import Path
from typing import Any

import pytest
from process_bigraph.processes.growth_division import grow_divide_agent  # type: ignore[import-untyped]

from process_bigraph_lang.v2 import write_json
from process_bigraph_lang.v2.langium import langium_cli, run_cli
from tests.v2.helpers import MANIFESTS, load_corpus_json

pytestmark = pytest.mark.skipif(langium_cli() is None, reason="no Langium CLI (build dsl/ or install cli-native)")


def document_graph(doc: dict[str, Any], tmp_path: Path, manifests: list[Path] | None = None) -> dict[str, Any]:
    source = tmp_path / "doc.json"
    write_json(doc, source)
    args = ["graph", str(source)]
    if manifests:
        args += ["--interfaces", *[str(m) for m in manifests]]
    graph: dict[str, Any] = json.loads(run_cli(*args).stdout)
    return graph


def test_hybrid_graph_has_typed_ports_from_headers(tmp_path: Path) -> None:
    graph = document_graph(load_corpus_json("hybrid_two_way_exchange.json"), tmp_path, MANIFESTS)
    nodes = {n["id"]: n for n in graph["nodes"]}
    assert nodes["pde"]["interface"] == "FVReactionDiffusion" and nodes["pde"]["interval"] == 0.01
    assert nodes["pde"]["ports"]["inputs"] == {
        "fields": "map<string, array<float>>",
        "external_conc": "map<string, array<float>>",
    }
    assert nodes["pde"]["ports"]["outputs"] == {"fields": "map<string, overwrite<array<float>>>"}
    assert nodes["recorder"]["interface"] == "GridRecorder" and not nodes["recorder"]["dynamic_ports"]
    assert nodes["particles"]["interface"] == "Stepper" and nodes["particles"]["dynamic_ports"]
    stores = {s["id"]: s for s in graph["stores"]}
    assert stores["fields"]["declared"] and not stores["particle_positions"]["declared"]
    assert {
        "node": "pde",
        "port": "fields",
        "store": "fields",
        "direction": "input",
        "type": "map<string, array<float>>",
    } in graph["edges"]


def test_nested_composite_graph_is_recursive(tmp_path: Path) -> None:
    doc = {"schema": {}, "state": {"agent": grow_divide_agent(path=["agent"]), "environment": {}}}
    graph = document_graph(doc, tmp_path)
    agent = next(n for n in graph["nodes"] if n["id"] == "agent")
    assert agent["kind"] == "composite" and {n["id"] for n in agent["children"]["nodes"]} == {"grow", "divide"}
    inner_edges = {(e["node"], e["port"], e["store"]) for e in agent["children"]["edges"]}
    assert ("grow", "mass", "mass") in inner_edges


def test_sub_port_wires_and_indices(tmp_path: Path) -> None:
    from copy import deepcopy

    from tests.compiler.generator.spatio_flux.test_spatio_flux_II import step_config_template

    graph = document_graph(deepcopy(step_config_template), tmp_path, MANIFESTS)
    edges = {(e["node"], e["port"], e["store"]) for e in graph["edges"]}
    assert ("dFBA[0,1]", "substrates/glucose", "fields/glucose/[0]/[1]") in edges
