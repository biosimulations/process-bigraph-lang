import tempfile
from pathlib import Path
from typing import Generator

import pytest

from process_bigraph_lang.dsl.model import (
    Model,
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
    Process,
    ProcessDefRef,
    StoreRef,
    StoreDefRef,
    CompositeDef,
    Store,
    SchemaItem,
    TypeRef,
    StoreDef,
    UnitRef,
    DefinitionRef,
    SchemaItemRef,
    Update,
    ProcessDef,
    PythonPath,
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
def model_path_spatio_flux() -> Path:
    """
    Fixture that provides the path to the Spatio-Flux model file.
    """
    return Path(__file__).parent / "data" / "dsl" / "spatio_flux.pblang"


@pytest.fixture
def simple_parse_data_1() -> Generator[tuple[str, Path, Model], None, None]:
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
    expected_model = Model(
        definitions=[definition], types=[], units=[], processDefs=[], store_defs=[], compositeDefs=[]
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir) / "test.pblang"
        with open(tmp_path, "w") as f:
            f.write(dsl_str)

        yield dsl_str, tmp_path, expected_model


@pytest.fixture
def simple_parse_data_2() -> Generator[tuple[str, Path, Model], None, None]:
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
    expected_model = Model(
        definitions=[definition1, definition2], types=[], units=[], processDefs=[], store_defs=[], compositeDefs=[]
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir) / "test.pblang"
        with open(tmp_path, "w") as f:
            f.write(dsl_str)

        yield dsl_str, tmp_path, expected_model


@pytest.fixture
def simple_parse_data_3() -> Generator[tuple[str, Path, Model], None, None]:
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
    expected_model = Model(
        units=[unit_uM_per_h, unit_uM, unit_conc, unit_hour, unit_dimensionless],
        definitions=[def_exp, def_my_update],
        types=[type_float, type_concentration],
        processDefs=[],
        store_defs=[],
        compositeDefs=[],
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir) / "test.pblang"
        with open(tmp_path, "w") as f:
            f.write(dsl_str)

        yield dsl_str, tmp_path, expected_model


@pytest.fixture
def simple_parse_data_4() -> Generator[tuple[str, Path, Model], None, None]:
    dsl_str = """
    type float builtin
    type string builtin

    unit hour: ["h"]
    unit uM_per_h: ["10e-6 mole/liter/h"]
    unit uM: ["10e-6 mole/liter"]

    def my_update(substrate, rate, interval): substrate + rate * interval;

    process_def MyProcess path my_processes.Process1
        param glucose_growth: float default 0.1 [uM_per_h]
        param dt: float default 0.1 [hour]
        param dummy_path: string default "/tmp/file.txt"

        var glucose: float [uM]

        inputs glucose
        outputs glucose

        updates
            glucose := my_update(glucose, glucose_growth, dt);

    store_def medium
        state_def glucose: float default 3.0 [uM]
        state_def calcium: float default 0.5

    store_def cell parent medium
        state_def glucose: float default 0.0
        state_def calcium: float default 0.0

    store_def nucleus parent cell
        state_def glucose: float default 0.0
        state_def calcium: float default 0.0

    composite_def CellComposite
        store cell1: cell
        store nuc1: nucleus
        process p1: MyProcess stores cell1
        process p2: MyProcess stores nuc1
    """
    type_float = Type(name="float", builtin="builtin")
    type_string = Type(name="string", builtin="builtin")

    unit_hour = Unit(name="hour", symbol="h")
    unit_uM_per_h = Unit(name="uM_per_h", symbol="10e-6 mole/liter/h")
    unit_uM = Unit(name="uM", symbol="10e-6 mole/liter")

    def_my_update = Definition(
        name="my_update",
        args=[DeclaredParameter(name="substrate"), DeclaredParameter(name="rate"), DeclaredParameter(name="interval")],
        expr=BinaryExpression(
            operator="+",
            left=VariableRef(variable=Reference(ref="#/definitions@0/args@0", ref_text="substrate")),
            right=BinaryExpression(
                operator="*",
                left=VariableRef(variable=Reference(ref="#/definitions@0/args@1", ref_text="rate")),
                right=VariableRef(variable=Reference(ref="#/definitions@0/args@2", ref_text="interval")),
            ),
        ),
    )

    process_MyProcess = ProcessDef(
        name="MyProcess",
        python_path=PythonPath(path=["my_processes", "Process1"]),
        params=[
            SchemaItem(
                name="glucose_growth",
                type=TypeRef(ref="#/types@0", ref_text="float"),
                default=DefaultValue(val=0.1),
                unit_ref=UnitRef(ref="#/units@1", ref_text="uM_per_h"),
            ),
            SchemaItem(
                name="dt",
                type=TypeRef(ref="#/types@0", ref_text="float"),
                default=DefaultValue(val=0.1),
                unit_ref=UnitRef(ref="#/units@0", ref_text="hour"),
            ),
            SchemaItem(
                name="dummy_path",
                type=TypeRef(ref="#/types@1", ref_text="string"),
                default=DefaultValue(val="/tmp/file.txt"),
            ),
        ],
        vars=[
            SchemaItem(
                name="glucose",
                type=TypeRef(ref="#/types@0", ref_text="float"),
                unit_ref=UnitRef(ref="#/units@2", ref_text="uM"),
            ),
        ],
        inputs=[
            Reference(ref="#/processDefs@0/vars@0", ref_text="glucose"),
        ],
        outputs=[
            Reference(ref="#/processDefs@0/vars@0", ref_text="glucose"),
        ],
        updates=[
            Update(
                lhs=SchemaItemRef(ref="#/processDefs@0/vars@0", ref_text="glucose"),
                rhs=FunctionCall(
                    func=DefinitionRef(ref="#/definitions@0", ref_text="my_update"),
                    args=[
                        VariableRef(variable=Reference(ref="#/processDefs@0/vars@0", ref_text="glucose")),
                        VariableRef(variable=Reference(ref="#/processDefs@0/params@0", ref_text="glucose_growth")),
                        VariableRef(variable=Reference(ref="#/processDefs@0/params@1", ref_text="dt")),
                    ],
                ),
            )
        ],
    )
    store_medium = StoreDef(
        name="medium",
        states=[
            SchemaItem(
                name="glucose",
                type=TypeRef(ref="#/types@0", ref_text="float"),
                default=DefaultValue(val=3),
                unit_ref=UnitRef(ref="#/units@2", ref_text="uM"),
            ),
            SchemaItem(name="calcium", type=TypeRef(ref="#/types@0", ref_text="float"), default=DefaultValue(val=0.5)),
        ],
    )
    store_cell = StoreDef(
        name="cell",
        parent=Reference(ref="#/store_defs@0", ref_text="medium"),
        states=[
            SchemaItem(name="glucose", type=TypeRef(ref="#/types@0", ref_text="float"), default=DefaultValue(val=0)),
            SchemaItem(name="calcium", type=TypeRef(ref="#/types@0", ref_text="float"), default=DefaultValue(val=0)),
        ],
    )
    store_nucleus = StoreDef(
        name="nucleus",
        parent=Reference(ref="#/store_defs@1", ref_text="cell"),
        states=[
            SchemaItem(name="glucose", type=TypeRef(ref="#/types@0", ref_text="float"), default=DefaultValue(val=0)),
            SchemaItem(name="calcium", type=TypeRef(ref="#/types@0", ref_text="float"), default=DefaultValue(val=0)),
        ],
    )
    composite_def = CompositeDef(
        name="CellComposite",
        stores=[
            Store(name="cell1", store_def=StoreDefRef(ref="#/store_defs@1", ref_text="cell")),
            Store(name="nuc1", store_def=StoreDefRef(ref="#/store_defs@2", ref_text="nucleus")),
        ],
        processes=[
            Process(
                name="p1",
                process_def=ProcessDefRef(ref="#/processDefs@0", ref_text="MyProcess"),
                stores=[StoreRef(ref="#/compositeDefs@0/stores@0", ref_text="cell1")],
            ),
            Process(
                name="p2",
                process_def=ProcessDefRef(ref="#/processDefs@0", ref_text="MyProcess"),
                stores=[StoreRef(ref="#/compositeDefs@0/stores@1", ref_text="nuc1")],
            ),
        ],
    )
    expected_model = Model(
        units=[unit_hour, unit_uM_per_h, unit_uM],
        definitions=[def_my_update],
        types=[type_float, type_string],
        processDefs=[process_MyProcess],
        store_defs=[store_medium, store_cell, store_nucleus],
        compositeDefs=[composite_def],
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir) / "test.pblang"
        with open(tmp_path, "w") as f:
            f.write(dsl_str)

        yield dsl_str, tmp_path, expected_model
