"""The standalone describe script: it runs with no access to this package and agrees with `describe_module`."""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from process_bigraph_lang.v2 import InterfaceRegistry
from process_bigraph_lang.v2 import describe_env as script
from process_bigraph_lang.v2 import langium
from process_bigraph_lang.v2.__main__ import main as cli_main
from process_bigraph_lang.v2.describe_env import NO_DEFAULT, default_of

ROOT = Path(__file__).resolve().parents[2]
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
    assert manifest["schema_version"] == "pblang-manifest/0"
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


@pytest.mark.parametrize(
    ("spec", "default"),
    [
        ("float", NO_DEFAULT),
        ("float{0.5}", 0.5),
        ("integer{3}", 3),
        ("string{abc}", "abc"),
        ('list[string]{["a"]}', ["a"]),
        ("map[float]{{}}", {}),
        ("a:float|b:integer{1}", NO_DEFAULT),
        ({"_type": "float", "_default": 0.01}, 0.01),
        ({"_type": "list[string]", "_default": []}, []),
        ({"a": "float"}, NO_DEFAULT),
        (3, NO_DEFAULT),
    ],
)
def test_default_of(spec: Any, default: Any) -> None:
    assert default_of(spec) == default if default is not NO_DEFAULT else default_of(spec) is NO_DEFAULT


def test_cli_manifest_only_needs_no_langium_cli(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    def no_cli(*args: str, check: bool = True) -> None:
        raise AssertionError("--manifest-only must not run the Langium CLI")

    monkeypatch.setattr(langium, "run_cli", no_cli)
    assert cli_main(["describe", TOY, "--manifest-only"]) == 0
    manifest = json.loads(capsys.readouterr().out)
    assert manifest["schema_version"] == "pblang-manifest/0"
    assert any(c["name"] == "AddFloatsProcess" for c in manifest["components"])
