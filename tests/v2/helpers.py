"""Shared helpers for the v2 round-trip tests: corpus loading, snapshots, sidecar assets, realized equivalence."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import numpy as np
import process_bigraph as pg  # type: ignore[import-untyped]
from bigraph_schema import json_codec  # type: ignore[import-untyped]

from process_bigraph_lang.v2 import InterfaceRegistry, equivalent
from process_bigraph_lang.v2.model import ExternalRef
from process_bigraph_lang.v2.printer import Printed

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures" / "data" / "v2"
CORPUS = FIXTURES / "corpus"
SNAPSHOTS = FIXTURES / "snapshots"
UPDATE = os.environ.get("PBLANG_UPDATE_SNAPSHOTS") == "1"

# the interfaces of the processes the corpus uses; edges that resolve here print as imports.
# The fixture processes are described live; viva-pde-particle's come from the manifest generated in its own env
# (tests/fixtures/data/v2/interfaces/, by `python -m process_bigraph_lang.v2 describe`), never by import.
REGISTRY = InterfaceRegistry.from_modules(
    "tests.fixtures.test_registry.toy_library", "tests.fixtures.test_registry.spatio_flux.processes"
)
REGISTRY.decls.extend(
    InterfaceRegistry.from_manifest(
        json.loads((FIXTURES / "interfaces" / "viva_pde_particle.manifest.json").read_text(encoding="utf-8"))
    ).decls
)


def load_corpus_json(name: str) -> dict[str, Any]:
    """A corpus document dumped with `bigraph_schema.json_codec` (numpy arrays come back as arrays)."""
    loaded = json_codec.loads((CORPUS / name).read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def assert_snapshot(name: str, printed: Printed) -> None:
    """Compare printed text and assets with the committed snapshot; `PBLANG_UPDATE_SNAPSHOTS=1` rewrites it."""
    expected_text = SNAPSHOTS / f"{name}.pblang"
    if UPDATE:
        SNAPSHOTS.mkdir(parents=True, exist_ok=True)
        expected_text.write_text(printed.text, encoding="utf-8")
        for asset_name, content in printed.assets.items():
            target = SNAPSHOTS / asset_name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
    assert expected_text.exists(), f"no snapshot {expected_text}; run with PBLANG_UPDATE_SNAPSHOTS=1"
    assert printed.text == expected_text.read_text(
        encoding="utf-8"
    ), f"snapshot {name} differs (PBLANG_UPDATE_SNAPSHOTS=1 to update)"
    for asset_name, content in printed.assets.items():
        # pre-commit's end-of-file fixer appends a newline to committed assets; that is not a difference
        committed = (SNAPSHOTS / asset_name).read_bytes().rstrip(b"\n")
        assert committed == content.rstrip(b"\n"), f"asset {asset_name} differs"


def asset_loader(printed: Printed) -> Any:
    """An `assets` callback for the writer that resolves the printer's sidecar references."""

    def load(ref: ExternalRef) -> Any:
        return _decode_asset(ref, printed.assets[ref.path])

    return load


def snapshot_asset_loader() -> Any:
    """An `assets` callback that reads the committed sidecar files of the snapshots."""

    def load(ref: ExternalRef) -> Any:
        return _decode_asset(ref, (SNAPSHOTS / ref.path).read_bytes())

    return load


def _decode_asset(ref: ExternalRef, content: bytes) -> Any:
    if ref.kind == "text":
        return content.decode()
    payload = json.loads(content)
    if ref.kind == "array":
        return np.asarray(payload["data"], dtype=payload["dtype"]).reshape(payload["shape"])
    return payload


def realized_equivalent(a: dict[str, Any], b: dict[str, Any], core: Any) -> bool:
    """Build both documents with process-bigraph and compare what it serializes (a stronger check)."""
    saved = []
    for doc in (a, b):
        composite = pg.Composite(doc, core=core)
        saved.append({"schema": composite.serialize_schema(), "state": composite.serialize_state()})
    return equivalent(saved[0], saved[1], core)
