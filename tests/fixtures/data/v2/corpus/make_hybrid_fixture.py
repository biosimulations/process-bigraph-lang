"""
Generate `hybrid_two_way_exchange.json`: a viva-pde-particle hybrid composite document.

Run once, inside the viva-pde-particle checkout's own environment (it needs the PDE and particle engines
to build the document), and commit the JSON:

    cd /path/to/viva-pde-particle
    pixi run python /path/to/process-bigraph-lang/tests/fixtures/data/v2/corpus/make_hybrid_fixture.py \
        /path/to/process-bigraph-lang/tests/fixtures/data/v2/corpus/hybrid_two_way_exchange.json

The document is `two_way_exchange()` (the smallest grid, 11x11x3) with a `SpatialRecorder` attached,
wrapped as `{"state": ...}` and dumped with `bigraph_schema.json_codec` (numpy-safe). pytest does not
collect this file.
"""

import sys
import tempfile
from pathlib import Path

from bigraph_schema import json_codec  # type: ignore[import-untyped]
from viva_pde_particle.composites.examples import two_way_exchange  # type: ignore[import-not-found]
from viva_pde_particle.viz3d.record import attach_recorder  # type: ignore[import-not-found]


def main(out: Path) -> None:
    doc = two_way_exchange(core=None)
    doc = attach_recorder(doc, Path(tempfile.gettempdir()) / "hybrid_fixture_out", output_dt=0.1)
    out.write_text(json_codec.dumps({"state": doc}, indent=1), encoding="utf-8")
    print(f"wrote {out} ({out.stat().st_size} bytes); top-level nodes: {sorted(doc)}")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
