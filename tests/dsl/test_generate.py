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
)


def test_simple() -> None:
    lang = """
        def test(a):  a + 1;
    """
    expr = BinaryExpression(
        operator="+",
        left=VariableRef(variable=Reference(builtin_ref="#/definitions@0/args@0")),
        right=NumberLiteral(value=1.0),
    )
    definition = Definition(
        builtin_type="Definition",
        name="test",
        args=[DeclaredParameter(name="a")],
        expr=expr,
    )
    expected_model = Model(definitions=[definition])
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
        left=VariableRef(variable=Reference(builtin_ref="#/definitions@0/args@0")),
        right=VariableRef(variable=Reference(builtin_ref="#/definitions@0/args@1")),
    )
    definition1 = Definition(
        name="mult",
        args=[DeclaredParameter(name="a"), DeclaredParameter(name="b")],
        expr=expr1,
    )
    expr2 = FunctionCall(
        func=Reference(builtin_ref="#/definitions@0"),
        args=[
            VariableRef(variable=Reference(builtin_ref="#/definitions@1/args@0")),
            VariableRef(variable=Reference(builtin_ref="#/definitions@1/args@0")),
        ],
    )
    definition2 = Definition(
        name="square",
        args=[DeclaredParameter(name="a")],
        expr=expr2,
    )
    expected_model = Model(definitions=[definition1, definition2])
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir) / "test.pblang"
        with open(tmp_path, "w") as f:
            f.write(lang)
        generated_json = generate_model(tmp_path)
        print(generated_json)
        model = Model.model_validate_json(generated_json)
    assert model == expected_model
