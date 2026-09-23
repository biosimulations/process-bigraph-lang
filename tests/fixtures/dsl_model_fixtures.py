import tempfile
from pathlib import Path
from typing import Generator

import pytest

from process_bigraph_lang.dsl.ast_model import (
    ArrayType,
    ASTModel,
    FloatLiteral,
    Field_,
    MemberCall,
    PrimitiveType,
    Reference,
    SimpleTypeRef,
    StructFieldValue,
    StructLiteral,
    StructType,
    TypeAlias,
    Unit,
    VarDef,
)


@pytest.fixture
def model_path_abc() -> Path:
    """
    Fixture that provides the path to the ABC model file.
    """
    return Path(__file__).parent / "data" / "dsl" / "abc.pblang"


@pytest.fixture
def model_path_abc_antlr() -> Path:
    """
    Fixture that provides the path to the ABC model file in the legacy ANTLR grammar.
    """
    return Path(__file__).parent / "data" / "antlr" / "abc.pblang"


@pytest.fixture
def model_path_abc_error() -> Path:
    """
    Fixture that provides the path to the ABC model file with an unresolved reference.
    """
    return Path(__file__).parent / "data" / "dsl" / "abc_with_error.pblang"


@pytest.fixture
def model_add_floats() -> Path:
    """
    Fixture that provides the path to the toy add floats model file.
    """
    return Path(__file__).parent / "data" / "dsl" / "add_floats.pblang"


@pytest.fixture
def model_dfba_single() -> Path:
    """
    Fixture that provides the path to the single dfba model file.
    """
    return Path(__file__).parent / "data" / "dsl" / "dfba_single.pblang"


def _float_ref() -> SimpleTypeRef:
    return SimpleTypeRef(type=Reference(ref="#/elements@0", ref_text="float"))


def _write(dsl_str: str) -> Generator[Path, None, None]:
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir) / "test.pblang"
        with open(tmp_path, "w") as f:
            f.write(dsl_str)
        yield tmp_path


@pytest.fixture
def simple_parse_data_1() -> Generator[tuple[str, Path, ASTModel], None, None]:
    dsl_str = """
        type float builtin
        let a: float = 1.0;
        let b: float = a;
    """
    expected_model = ASTModel(
        elements=[
            PrimitiveType(name="float"),
            VarDef(name="a", type=_float_ref(), value=FloatLiteral(value=1.0)),
            VarDef(
                name="b",
                type=_float_ref(),
                value=MemberCall(element=Reference(ref="#/elements@1", ref_text="a")),
            ),
        ]
    )
    for tmp_path in _write(dsl_str):
        yield dsl_str, tmp_path, expected_model


@pytest.fixture
def simple_parse_data_2() -> Generator[tuple[str, Path, ASTModel], None, None]:
    dsl_str = """
        type float builtin
        struct Point { x: float; y: float = 0.0; }
        let p: Point = { x = 1.0, y = 2.0 };
        let px: float = p.x;
    """
    expected_model = ASTModel(
        elements=[
            PrimitiveType(name="float"),
            StructType(
                name="Point",
                fields=[
                    Field_(name="x", type=_float_ref()),
                    Field_(name="y", type=_float_ref(), default=FloatLiteral(value=0.0)),
                ],
            ),
            VarDef(
                name="p",
                type=SimpleTypeRef(type=Reference(ref="#/elements@1", ref_text="Point")),
                value=StructLiteral(
                    fields=[
                        StructFieldValue(name="x", value=FloatLiteral(value=1.0)),
                        StructFieldValue(name="y", value=FloatLiteral(value=2.0)),
                    ]
                ),
            ),
            VarDef(
                name="px",
                type=_float_ref(),
                value=MemberCall(
                    previous=MemberCall(element=Reference(ref="#/elements@2", ref_text="p")),
                    element=Reference(ref="#/elements@1/fields@0", ref_text="x"),
                ),
            ),
        ]
    )
    for tmp_path in _write(dsl_str):
        yield dsl_str, tmp_path, expected_model


@pytest.fixture
def simple_parse_data_3() -> Generator[tuple[str, Path, ASTModel], None, None]:
    dsl_str = """
    // imported definitions from standard library (or other files)
    type float builtin

    // my model
    type concentration = float
    type concentrations = array<concentration>
    unit uM_per_h: ["10e-6 mole/liter/h"]
    unit uM: ["10e-6 mole/liter"]
    unit conc: uM_per_h
    unit hour: ["h"]
    unit dimensionless: ["1"]
    """
    expected_model = ASTModel(
        elements=[
            PrimitiveType(name="float"),
            TypeAlias(name="concentration", type=_float_ref()),
            TypeAlias(
                name="concentrations",
                type=ArrayType(elementType=SimpleTypeRef(type=Reference(ref="#/elements@1", ref_text="concentration"))),
            ),
            Unit(name="uM_per_h", symbol="10e-6 mole/liter/h"),
            Unit(name="uM", symbol="10e-6 mole/liter"),
            Unit(name="conc", unit_ref=Reference(ref="#/elements@3", ref_text="uM_per_h")),
            Unit(name="hour", symbol="h"),
            Unit(name="dimensionless", symbol="1"),
        ]
    )
    for tmp_path in _write(dsl_str):
        yield dsl_str, tmp_path, expected_model
