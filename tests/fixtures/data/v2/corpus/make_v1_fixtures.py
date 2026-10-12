"""
Regenerate the corpus documents under `v1/` that are built from code: the growth-division nested composite
(`process_bigraph.processes.growth_division`) and the saved form of the toy add-floats composite (what
`Composite.save()` writes for `toy_process.json`). The other `v1/*.json` files are the expected documents of the
v1 compiler's tests, kept as static fixtures since v1 was removed. Run with
`poetry run python tests/fixtures/data/v2/corpus/make_v1_fixtures.py`. Tuples are tagged
(`{"__tuple__": true, "data": [...]}`), arrays as `bigraph_schema.json_codec` tags them.
"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

import process_bigraph as pg  # type: ignore[import-untyped]
from process_bigraph.processes.growth_division import grow_divide_agent  # type: ignore[import-untyped]

from process_bigraph_lang.v2 import dumps, loads

OUT = Path(__file__).resolve().parent / "v1"


def documents() -> dict[str, dict[str, Any]]:
    core = pg.allocate_core()
    toy: dict[str, Any] = loads((OUT / "toy_process.json").read_text(encoding="utf-8"))
    authoring = deepcopy(toy)
    del authoring["state"]["print_result"]  # the file-writing step would write output.txt
    composite = pg.Composite(deepcopy(authoring), core=core)
    return {
        "growth_division": {"schema": {}, "state": {"agent": grow_divide_agent(path=["agent"]), "environment": {}}},
        "saved_toy_add_floats": {"schema": composite.serialize_schema(), "state": composite.serialize_state()},
    }


if __name__ == "__main__":
    for name, document in documents().items():
        (OUT / f"{name}.json").write_text(dumps(deepcopy(document)) + "\n", encoding="utf-8")
        print(f"wrote {OUT / f'{name}.json'}")
