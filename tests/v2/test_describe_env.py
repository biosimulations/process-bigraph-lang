"""The standalone describe script and the shared manifest format (`pbg-interfaces/1`): the script runs with no access
to this package, agrees with `describe_module`, and everything written validates against the published JSON Schema."""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import jsonschema  # type: ignore[import-untyped]
import pytest

from process_bigraph_lang.v2 import InterfaceRegistry
from process_bigraph_lang.v2 import describe_env as script
from process_bigraph_lang.v2 import langium
from process_bigraph_lang.v2.__main__ import main as cli_main
from process_bigraph_lang.v2.interfaces import MANIFEST_VERSION, SCHEMA_URL

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = json.loads((ROOT / "docs" / "schemas" / "pbg-interfaces-1.schema.json").read_text())
INTERFACES = ROOT / "tests" / "fixtures" / "data" / "v2" / "interfaces"
TOY = "tests.fixtures.test_registry.toy_library"
SPATIO = "tests.fixtures.test_registry.spatio_flux"


def run_script(tmp_path: Path, *args: str) -> dict[str, Any]:
    """Run a copy of the script outside the repository, so it can only use the standard library and the roots."""
    copy = tmp_path / "describe_env.py"
    shutil.copy(script.__file__, copy)
    env = {**os.environ, "PYTHONPATH": str(ROOT)}
    result = subprocess.run(
        [sys.executable, "-P", str(copy), *args], cwd=tmp_path, env=env, capture_output=True, text=True, check=True
    )
    assert "described" in result.stderr
    manifest: dict[str, Any] = json.loads(result.stdout)
    return manifest


def comparable(entry: dict[str, Any]) -> dict[str, Any]:
    kept: dict[str, Any] = json.loads(
        json.dumps({k: v for k, v in entry.items() if k not in ("address", "module")}, default=str)
    )
    return kept


def test_script_agrees_with_describe_module(tmp_path: Path) -> None:
    manifest = run_script(tmp_path, TOY, SPATIO, "--env-name", "fixtures", "--image", "example/image@sha256:0")
    jsonschema.validate(manifest, SCHEMA)
    assert manifest["schema_version"] == MANIFEST_VERSION == "pbg-interfaces/1"
    assert manifest["$schema"] == SCHEMA_URL == SCHEMA["$id"]
    assert manifest["environment"]["name"] == "fixtures"
    assert manifest["environment"]["image"] == "example/image@sha256:0"
    assert manifest["environment"]["roots"] == [TOY, SPATIO]
    by_address = {c["address"]: c for c in manifest["components"]}
    assert list(by_address) == sorted(by_address)

    toy = InterfaceRegistry.from_modules(TOY).to_manifest()["components"]
    assert toy
    for entry in toy:  # classes defined in the module itself: same address
        assert comparable(by_address[entry["address"]]) == comparable(entry)

    # a package's classes are found in the submodules that define them, so they are addressed there
    spatio = InterfaceRegistry.from_modules(f"{SPATIO}.processes").to_manifest()["components"]
    by_name = {c["name"]: c for c in manifest["components"] if c["module"].startswith(SPATIO)}
    for entry in spatio:
        found = by_name[entry["name"]]
        assert found["module"].startswith(f"{SPATIO}.processes")
        assert comparable(found) == comparable(entry)
    assert by_name["DiffusionAdvection"]["dynamic_ports"] is True


def test_import_errors_are_recorded_not_fatal(tmp_path: Path) -> None:
    manifest = run_script(tmp_path, "no_such_module_anywhere", TOY)
    assert [e["module"] for e in manifest["errors"]] == ["no_such_module_anywhere"]
    assert "ModuleNotFoundError" in manifest["errors"][0]["error"]
    assert any(c["name"] == "AddFloatsProcess" for c in manifest["components"])


def test_cli_manifest_only_needs_no_langium_cli(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    def no_cli(*args: str, check: bool = True) -> None:
        raise AssertionError("--manifest-only must not run the Langium CLI")

    monkeypatch.setattr(langium, "run_cli", no_cli)
    assert cli_main(["describe", TOY, "--manifest-only"]) == 0
    manifest = json.loads(capsys.readouterr().out)
    jsonschema.validate(manifest, SCHEMA)
    assert any(c["name"] == "AddFloatsProcess" for c in manifest["components"])


@pytest.mark.parametrize("name", ["test_registry.manifest.json", "viva_pde_particle.manifest.json"])
def test_fixture_manifests_validate_and_round_trip(name: str) -> None:
    manifest = json.loads((INTERFACES / name).read_text())
    jsonschema.validate(manifest, SCHEMA)
    written = json.loads(json.dumps(InterfaceRegistry.from_manifest(manifest).to_manifest(), default=str))
    jsonschema.validate(written, SCHEMA)
    assert written["components"] == manifest["components"]


def test_config_defaults_come_from_the_types() -> None:
    manifest = json.loads((INTERFACES / "viva_pde_particle.manifest.json").read_text())
    decl = InterfaceRegistry.from_manifest(manifest).lookup("local:FVReactionDiffusion")
    assert decl is not None
    assert decl.config["dt"].default == 0.01  # {"_type": "float", "_default": 0.01}
    assert decl.doc is not None and decl.doc.startswith("PDE half")


def test_the_earlier_pblang_manifest_is_still_read() -> None:
    legacy = {
        "schema_version": "pblang-manifest/0",
        "components": [
            {
                "name": "Old",
                "kind": "step",
                "address": "local:!old.Old",
                "module": "old",
                "config": {"rate": {"type": "float", "default": 2.0}},
                "inputs": {"x": "float"},
                "outputs": None,
                "dynamic_ports": False,
                "doc": "An old entry.",
            }
        ],
    }
    registry = InterfaceRegistry.from_manifest(legacy)
    decl = registry.lookup("local:Old")
    assert decl is not None and decl.config["rate"].default == 2.0 and decl.doc == "An old entry."
    jsonschema.validate(json.loads(json.dumps(registry.to_manifest())), SCHEMA)  # written in the shared format
    with pytest.raises(ValueError, match="pblang-manifest/9"):
        InterfaceRegistry.from_manifest({"schema_version": "pblang-manifest/9", "components": []})
