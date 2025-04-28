import tempfile
from pathlib import Path

from process_bigraph_lang.dsl.generate import generate_model
from process_bigraph_lang.dsl.model import (
    Model,
    Definition,
    DeclaredParameter,
    BinaryExpression,
    VariableRef,
    NumberLiteral,
    Reference,
    FunctionCall,
    Type,
    DefaultValue,
    Unit,
)


def test_simple() -> None:
    lang = """
        def test(a):  a + 1;
    """
    expr = BinaryExpression(
        operator="+",
        left=VariableRef(variable=Reference(ref="#/definitions@0/args@0", ref_text="a")),
        right=NumberLiteral(value=1.0),
    )
    definition = Definition(
        name="test",
        args=[DeclaredParameter(name="a")],
        expr=expr,
    )
    expected_model = Model(definitions=[definition], types=[], units=[])
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir) / "test.pblang"
        with open(tmp_path, "w") as f:
            f.write(lang)
        generated_json = generate_model(tmp_path)
        print(generated_json)
        model = Model.model_validate_json(generated_json)
    assert model == expected_model


def test_square() -> None:
    lang = """
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
            VariableRef(variable=Reference(ref="#/definitions@1/args@0", ref_text="a")),
            VariableRef(variable=Reference(ref="#/definitions@1/args@0", ref_text="a")),
        ],
    )
    definition2 = Definition(
        name="square",
        args=[DeclaredParameter(name="a")],
        expr=expr2,
    )
    expected_model = Model(definitions=[definition1, definition2], types=[], units=[])
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir) / "test.pblang"
        with open(tmp_path, "w") as f:
            f.write(lang)
        generated_json = generate_model(tmp_path)
        print(generated_json)
        model = Model.model_validate_json(generated_json)
    assert model == expected_model


def test_types_units_defs() -> None:
    lang = """
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
    expected_model = Model(
        units=[unit_uM_per_h, unit_uM, unit_conc, unit_hour, unit_dimensionless],
        definitions=[def_exp, def_my_update],
        types=[type_float, type_concentration],
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir) / "test.pblang"
        with open(tmp_path, "w") as f:
            f.write(lang)
        generated_json = generate_model(tmp_path)
    print(generated_json)
    model = Model.model_validate_json(generated_json)
    assert model.model_dump_json(indent=2) == expected_model.model_dump_json(indent=2)
