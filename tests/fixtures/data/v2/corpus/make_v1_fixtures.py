"""
Dump the documents the Python tests build in memory (the v1 expected templates, the growth-division composite
and the saved toy composite) as JSON for the TypeScript round-trip tests: `poetry run python
tests/fixtures/data/v2/corpus/make_v1_fixtures.py`. Tuples are tagged (`{"__tuple__": true, "data": [...]}`),
arrays as `bigraph_schema.json_codec` tags them.
"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

import process_bigraph as pg  # type: ignore[import-untyped]
from process_bigraph.processes.growth_division import grow_divide_agent  # type: ignore[import-untyped]

from process_bigraph_lang.v2 import dumps
from tests.compiler.generator.spatio_flux.test_spatio_flux_I import step_config_template as spatio_one
from tests.compiler.generator.spatio_flux.test_spatio_flux_II import step_config_template as spatio_two
from tests.compiler.generator.spatio_flux.test_spatio_flux_III import step_config_template as spatio_three
from tests.compiler.generator.test_collections import (
    flat_expected_config_template,
    list_expected_config_template,
    map_expected_config_template,
)
from tests.compiler.generator.test_toy_add_floats import (
    add_floats_process_expected_config_template,
    add_floats_step_expected_config_template,
)

OUT = Path(__file__).resolve().parent / "v1"


def documents() -> dict[str, dict[str, Any]]:
    core = pg.allocate_core()
    authoring: dict[str, Any] = deepcopy(add_floats_process_expected_config_template)
    del authoring["state"]["print_result"]  # the file-writing step would write output.txt
    composite = pg.Composite(deepcopy(authoring), core=core)
    return {
        "toy_step": add_floats_step_expected_config_template,
        "toy_process": add_floats_process_expected_config_template,
        "collections_flat": flat_expected_config_template,
        "collections_list": list_expected_config_template,
        "collections_map": map_expected_config_template,
        "spatio_flux_I": spatio_one,
        "spatio_flux_II": spatio_two,
        "spatio_flux_III": spatio_three,
        "growth_division": {"schema": {}, "state": {"agent": grow_divide_agent(path=["agent"]), "environment": {}}},
        "saved_toy_add_floats": {"schema": composite.serialize_schema(), "state": composite.serialize_state()},
    }


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name, document in documents().items():
        (OUT / f"{name}.json").write_text(dumps(deepcopy(document)) + "\n", encoding="utf-8")
        print(f"wrote {OUT / f'{name}.json'}")
