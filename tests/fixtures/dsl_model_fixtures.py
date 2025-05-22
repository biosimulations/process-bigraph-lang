import tempfile
from pathlib import Path
from typing import Generator

import pytest

from process_bigraph_lang.dsl.ast_model import (
    ASTModel,
    BinaryExpression,
    VariableRef,
    Reference,
    NumberLiteral,
    Definition,
    DeclaredParameter,
    FunctionCall,
    Unit,
    DefaultValue,
    Type,
)


@pytest.fixture
def model_path_abc() -> Path:
    """
    Fixture that provides the path to the ABC model file.
    """
    return Path(__file__).parent / "data" / "dsl" / "abc.pblang"


@pytest.fixture
def model_path_abc_error() -> Path:
    """
    Fixture that provides the path to the ABC model file.
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


@pytest.fixture
def simple_parse_data_1() -> Generator[tuple[str, Path, ASTModel], None, None]:
    dsl_str = """
        def test(a):  a + 1;
    """
    expr = BinaryExpression(
        operator="+",
        left=VariableRef(variable=Reference(ref="#/definitions@0/args@0", ref_text="a", ref_object=None)),
        right=NumberLiteral(value=1.0),
    )
    definition = Definition(
        name="test",
        args=[DeclaredParameter(name="a")],
        expr=expr,
    )
    expected_model = ASTModel(
        definitions=[definition],
        types=[],
        units=[],
        stepDefs=[],
        procDefs=[],
        storeNodes=[],
        parameters=[],
        proc_calls=[],
        step_calls=[],
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir) / "test.pblang"
        with open(tmp_path, "w") as f:
            f.write(dsl_str)

        yield dsl_str, tmp_path, expected_model


@pytest.fixture
def simple_parse_data_2() -> Generator[tuple[str, Path, ASTModel], None, None]:
    dsl_str = """
        def mult(a, b):  a * b;
        def square(a) : mult(a, a);
    """
    expr1 = BinaryExpression(
        operator="*",
        left=VariableRef(variable=Reference(ref="#/definitions@0/args@0", ref_text="a")),
        right=VariableRef(variable=Reference(ref="#/definitions@0/args@1", ref_text="b")),
    )
    definition1 = Definition(
        name="mult",
        args=[DeclaredParameter(name="a"), DeclaredParameter(name="b")],
        expr=expr1,
    )
    expr2 = FunctionCall(
        func=Reference(ref="#/definitions@0", ref_text="mult"),
        args=[
            VariableRef(variable=Reference(ref="#/definitions@1/args@0", ref_text="a", ref_object=None)),
            VariableRef(variable=Reference(ref="#/definitions@1/args@0", ref_text="a", ref_object=None)),
        ],
    )
    definition2 = Definition(
        name="square",
        args=[DeclaredParameter(name="a")],
        expr=expr2,
    )
    expected_model = ASTModel(
        definitions=[definition1, definition2],
        types=[],
        units=[],
        stepDefs=[],
        procDefs=[],
        storeNodes=[],
        parameters=[],
        proc_calls=[],
        step_calls=[],
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir) / "test.pblang"
        with open(tmp_path, "w") as f:
            f.write(dsl_str)

        yield dsl_str, tmp_path, expected_model


@pytest.fixture
def simple_parse_data_3() -> Generator[tuple[str, Path, ASTModel], None, None]:
    dsl_str = """
    // imported definitions from standard library (or other files)
    type float default 0.0
    def exp(a): builtin

    // my model
    type concentration extends float default 1.0
    def my_update(substrate, rate, interval): substrate + rate * interval;
    unit uM_per_h: ["10e-6 mole/liter/h"]
    unit uM: ["10e-6 mole/liter"]
    unit conc: uM_per_h
    unit hour: ["h"]
    unit dimensionless: ["1"]
    """
    type_float = Type(name="float", default=DefaultValue(val=0))
    def_exp = Definition(
        name="exp",
        args=[DeclaredParameter(name="a")],
        builtin="builtin",
    )
    type_concentration = Type(
        name="concentration",
        superType=Reference(ref="#/types@0", ref_text="float"),
        default=DefaultValue(val=1),
    )
    def_my_update = Definition(
        name="my_update",
        args=[DeclaredParameter(name="substrate"), DeclaredParameter(name="rate"), DeclaredParameter(name="interval")],
        expr=BinaryExpression(
            operator="+",
            left=VariableRef(variable=Reference(ref="#/definitions@1/args@0", ref_text="substrate")),
            right=BinaryExpression(
                operator="*",
                left=VariableRef(variable=Reference(ref="#/definitions@1/args@1", ref_text="rate")),
                right=VariableRef(variable=Reference(ref="#/definitions@1/args@2", ref_text="interval")),
            ),
        ),
    )
    unit_uM_per_h = Unit(name="uM_per_h", symbol="10e-6 mole/liter/h")
    unit_uM = Unit(name="uM", symbol="10e-6 mole/liter")
    unit_conc = Unit(name="conc", unit_ref=Reference(ref="#/units@0", ref_text="uM_per_h"))
    unit_hour = Unit(name="hour", symbol="h")
    unit_dimensionless = Unit(name="dimensionless", symbol="1")
    expected_model = ASTModel(
        units=[unit_uM_per_h, unit_uM, unit_conc, unit_hour, unit_dimensionless],
        definitions=[def_exp, def_my_update],
        types=[type_float, type_concentration],
        stepDefs=[],
        procDefs=[],
        storeNodes=[],
        parameters=[],
        proc_calls=[],
        step_calls=[],
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir) / "test.pblang"
        with open(tmp_path, "w") as f:
            f.write(dsl_str)

        yield dsl_str, tmp_path, expected_model
