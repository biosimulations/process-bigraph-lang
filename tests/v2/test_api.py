"""
The public Python API: text -> checked document (`compile_text` / `compile_file`), document -> text
(`decompile`), and nothing public that reaches a runnable document without the checker.
"""

from pathlib import Path
from typing import Any

import pytest
import yaml

import process_bigraph_lang.v2 as v2
from process_bigraph_lang.v2 import CompileError, compile_file, compile_text, decompile, equivalent
from process_bigraph_lang.v2.__main__ import main
from process_bigraph_lang.v2.langium import langium_cli
from tests.v2.helpers import CORPUS, FIXTURES, REGISTRY, SNAPSHOTS, load_corpus_json

pytestmark = pytest.mark.skipif(langium_cli() is None, reason="no Langium CLI (build dsl/ or install cli-native)")

TOY = "tests.fixtures.test_registry.toy_library"
ADD = f"""
import {TOY}.{{AddFloatsProcess}};
composite {{
  store A: float = 2.07;
  store B: float = 3.5;
  store C: float = 0.0;
  process add_nums : AddFloatsProcess every 1.0 {{
    inputs {{ left_hand_addend -> A, right_hand_addend -> B }}
    outputs {{ result -> C }}
  }}
}}
"""


def test_compile_text_checks_then_writes(core: Any) -> None:
    import process_bigraph as pg  # type: ignore[import-untyped]

    compiled = compile_text(ADD, registry=REGISTRY)
    assert compiled.diagnostics == []
    edge = compiled.document["state"]["add_nums"]
    assert edge["address"] == f"local:!{TOY}.AddFloatsProcess" and edge["interval"] == 1.0
    composite = pg.Composite(compiled.document, core=core)
    composite.run(2.0)
    assert composite.state["C"] == pytest.approx(2 * (2.07 + 3.5))


def test_compile_stops_on_errors_and_reports_every_finding() -> None:
    bad = ADD.replace("result -> C", "result -> C, bogus -> nowhere")
    with pytest.raises(CompileError) as raised:
        compile_text(bad, registry=REGISTRY)
    codes = {d.code for d in raised.value.diagnostics}
    assert "S021" in codes  # bogus is not an output port
    assert "W211" in codes  # nowhere is not a store (the warning is reported alongside the error)
    assert "S021" in str(raised.value) and "W211" not in str(raised.value)  # the message names the errors


def test_warnings_do_not_stop_the_compile_unless_strict() -> None:
    warned = ADD.replace("result -> C", "result -> nowhere")
    compiled = compile_text(warned, registry=REGISTRY)
    assert [d.code for d in compiled.warnings] == ["W211"]
    with pytest.raises(CompileError):
        compile_text(warned, registry=REGISTRY, strict=True)


def test_compile_file_resolves_sidecar_assets(spatio_core: Any) -> None:
    compiled = compile_file(SNAPSHOTS / "hybrid_two_way_exchange.pblang", registry=REGISTRY)
    original = load_corpus_json("hybrid_two_way_exchange.json")
    assert equivalent(original, compiled.document, spatio_core, REGISTRY)


def test_compile_to_composite_spec() -> None:
    text = (SNAPSHOTS / "reversible-dimerization.pblang").read_text(encoding="utf-8")
    compiled = compile_text(text, to="spec")
    spec = yaml.safe_load((CORPUS / "reversible-dimerization.composite.yaml").read_text(encoding="utf-8"))
    for key in ("name", "description", "tags", "requires", "emitters"):
        assert compiled.document.get(key) == spec.get(key), key
    assert "schema" not in compiled.document or "state" in compiled.document


def test_decompile_prints_the_snapshot_for_documents_and_specs() -> None:
    document = decompile(load_corpus_json("template_sites.json"), name="template_sites", registry=REGISTRY)
    assert document.text == (SNAPSHOTS / "template_sites.pblang").read_text(encoding="utf-8")
    spec = yaml.safe_load((CORPUS / "reversible-dimerization.composite.yaml").read_text(encoding="utf-8"))
    printed = decompile(spec, name="reversible-dimerization")  # detected as a spec by its keys
    assert printed.text == (SNAPSHOTS / "reversible-dimerization.pblang").read_text(encoding="utf-8")


def test_there_is_no_python_model() -> None:
    import importlib.util

    assert {"compile_text", "compile_file", "decompile", "check_file"} <= set(v2.__all__)
    for module in ("model", "reader", "writer", "printer"):
        assert importlib.util.find_spec(f"process_bigraph_lang.v2.{module}") is None


def test_cli_compile_and_decompile(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    source = tmp_path / "add.pblang"
    source.write_text(ADD, encoding="utf-8")
    out = tmp_path / "add.json"
    assert main(["compile", str(source), "-o", str(out)]) == 0
    assert '"add_nums"' in out.read_text(encoding="utf-8")
    assert main(["decompile", str(out)]) == 0
    printed = capsys.readouterr().out  # no manifest given: the edge prints with an inline declaration
    assert "process add_nums" in printed and "every 1.0 {" in printed and "left_hand_addend -> A" in printed
    source.write_text(ADD.replace("result -> C", "bogus -> C"), encoding="utf-8")
    manifest = str(FIXTURES / "interfaces" / "test_registry.manifest.json")
    assert main(["compile", str(source), "-o", str(out), "--interfaces", manifest]) == 1
    assert "S021" in capsys.readouterr().err
