"""Reading a v1 expected document and writing it back must reproduce it exactly (not just modulo normalization)."""

from copy import deepcopy
from typing import Any

import pytest

from process_bigraph_lang.v2 import deep_equal, read_document, write_document
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
from tests.v2.helpers import load_corpus_json

TEMPLATES: dict[str, dict[str, Any]] = {
    "toy_step": add_floats_step_expected_config_template,
    "toy_process": add_floats_process_expected_config_template,
    "collections_flat": flat_expected_config_template,
    "collections_list": list_expected_config_template,
    "collections_map": map_expected_config_template,
    "spatio_flux_I": spatio_one,
    "spatio_flux_II": spatio_two,
    "spatio_flux_III": spatio_three,
}


@pytest.mark.parametrize("name", list(TEMPLATES))
def test_exact_parity(name: str) -> None:
    original = deepcopy(TEMPLATES[name])
    written = write_document(read_document(deepcopy(original)))
    assert deep_equal(written, original, strict=True)


def test_exact_parity_for_template_sites() -> None:
    original = load_corpus_json("template_sites.json")
    written = write_document(read_document(deepcopy(original)))
    assert deep_equal(written, original, strict=True)
