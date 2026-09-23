"""
Pydantic mirror of the Langium AST for the process-bigraph language.

The Langium CLI serializes the AST as JSON; `langium_pblang.py` renames `$type`, `$ref` and
`$refText` to `obj_type`, `ref` and `ref_text` before validating it into these classes.
Cross-references keep Langium's document path (e.g. `#/elements@1/fields@0`) in `ref`;
`bind_ast.bind_ast_model` resolves them into `ref_object`.

Keep this module in sync with dsl/src/language/process-bigraph-language.langium.
"""

from typing import Annotated, Any, Literal, Union

from pydantic import BaseModel, Field


class Reference(BaseModel):
    ref: str | None = None  # Langium document path of the target; None if unresolved
    ref_text: str
    ref_object: Any = Field(default=None, exclude=True)


# ---------------------------------------------------------------------------
# type references
# ---------------------------------------------------------------------------


class SimpleTypeRef(BaseModel):
    obj_type: Literal["SimpleTypeRef"] = "SimpleTypeRef"
    type: Reference  # -> TypeDef


class ArrayType(BaseModel):
    obj_type: Literal["ArrayType"] = "ArrayType"
    elementType: "TypeRef"


class MapType(BaseModel):
    obj_type: Literal["MapType"] = "MapType"
    keyType: "TypeRef"
    valueType: "TypeRef"


class ParamDecl(BaseModel):
    obj_type: Literal["ParamDecl"] = "ParamDecl"
    name: str
    type: "TypeRef"


class TupleType(BaseModel):
    obj_type: Literal["TupleType"] = "TupleType"
    elements: list[ParamDecl] = []


TypeRef = Annotated[
    Union[SimpleTypeRef, ArrayType, MapType, TupleType],
    Field(discriminator="obj_type"),
]


# ---------------------------------------------------------------------------
# values
# ---------------------------------------------------------------------------


class IntLiteral(BaseModel):
    obj_type: Literal["IntLiteral"] = "IntLiteral"
    value: int


class FloatLiteral(BaseModel):
    obj_type: Literal["FloatLiteral"] = "FloatLiteral"
    value: float  # JSON serializes 1.0 as 1; pydantic coerces it back to float


class StringLiteral(BaseModel):
    obj_type: Literal["StringLiteral"] = "StringLiteral"
    value: str  # Langium strips the quotes and processes escapes


class BoolLiteral(BaseModel):
    obj_type: Literal["BoolLiteral"] = "BoolLiteral"
    value: Literal["true", "false"]


class MemberCall(BaseModel):
    """A reference `a` or member chain `a.b.c`; `previous` holds the chain up to the last segment."""

    obj_type: Literal["MemberCall"] = "MemberCall"
    element: Reference  # -> VarDef | Field | StoreDecl | ParamDecl
    previous: Union["MemberCall", None] = None


class StructFieldValue(BaseModel):
    obj_type: Literal["StructFieldValue"] = "StructFieldValue"
    name: str
    value: "Value"


class StructLiteral(BaseModel):
    obj_type: Literal["StructLiteral"] = "StructLiteral"
    fields: list[StructFieldValue] = []


class ArrayLiteral(BaseModel):
    obj_type: Literal["ArrayLiteral"] = "ArrayLiteral"
    elements: list["Value"] = []


MapKey = Annotated[
    Union[StringLiteral, IntLiteral, FloatLiteral, BoolLiteral],
    Field(discriminator="obj_type"),
]


class MapEntry(BaseModel):
    obj_type: Literal["MapEntry"] = "MapEntry"
    key: MapKey
    value: "Value"


class MapLiteral(BaseModel):
    obj_type: Literal["MapLiteral"] = "MapLiteral"
    entries: list[MapEntry] = []


class TupleFieldValue(BaseModel):
    obj_type: Literal["TupleFieldValue"] = "TupleFieldValue"
    name: str
    value: "Value"


class TupleLiteral(BaseModel):
    obj_type: Literal["TupleLiteral"] = "TupleLiteral"
    fields: list[TupleFieldValue] = []


class ConfigArg(BaseModel):
    obj_type: Literal["ConfigArg"] = "ConfigArg"
    name: str
    value: "Value"


class SiteLiteral(BaseModel):
    """An open value (a template site): `?` is required, `?(v)` is optional with default v."""

    obj_type: Literal["SiteLiteral"] = "SiteLiteral"
    default: Union["Value", None] = None


class CallableLiteral(BaseModel):
    """An instance of a remote step or process, e.g. `Grow(rate = 0.5)`."""

    obj_type: Literal["CallableLiteral"] = "CallableLiteral"
    callable_type: Reference  # -> RemoteCallableType
    configArgs: list[ConfigArg] = []


Value = Annotated[
    Union[
        IntLiteral,
        FloatLiteral,
        StringLiteral,
        BoolLiteral,
        MemberCall,
        StructLiteral,
        ArrayLiteral,
        MapLiteral,
        TupleLiteral,
        CallableLiteral,
        SiteLiteral,
    ],
    Field(discriminator="obj_type"),
]


# ---------------------------------------------------------------------------
# model elements
# ---------------------------------------------------------------------------


class PrimitiveType(BaseModel):
    obj_type: Literal["PrimitiveType"] = "PrimitiveType"
    name: str


class Field_(BaseModel):
    """A struct field (named `Field_` to avoid shadowing pydantic.Field)."""

    obj_type: Literal["Field"] = "Field"
    name: str
    type: TypeRef
    default: Value | None = None


class StructType(BaseModel):
    obj_type: Literal["StructType"] = "StructType"
    name: str
    fields: list[Field_] = []


class TypeAlias(BaseModel):
    obj_type: Literal["TypeAlias"] = "TypeAlias"
    name: str
    type: TypeRef


class RemoteCallableType(BaseModel):
    """
    A remote step or process: `remote step|process Name at "python.path" { config/inputs/outputs }`.
    Without `at` (address None) it is an interface: instances get an open address (an address site).
    """

    obj_type: Literal["RemoteCallableType"] = "RemoteCallableType"
    kind: Literal["step", "process"]
    name: str
    address: str | None = None
    config: TupleType | None = None
    inputs: TupleType | None = None
    outputs: TupleType | None = None


class TupleBinding(BaseModel):
    obj_type: Literal["TupleBinding"] = "TupleBinding"
    name: str
    type: TypeRef


class TuplePattern(BaseModel):
    obj_type: Literal["TuplePattern"] = "TuplePattern"
    bindings: list[TupleBinding] = []


class VarDef(BaseModel):
    """`let name: T = value;` or the destructuring form `let (a: A, b: B): T = value;`."""

    obj_type: Literal["VarDef"] = "VarDef"
    name: str | None = None
    lhs: TuplePattern | None = None
    type: TypeRef
    value: Value | None = None


class StoreDecl(BaseModel):
    obj_type: Literal["StoreDecl"] = "StoreDecl"
    name: str
    type: TypeRef


class InitDecl(BaseModel):
    obj_type: Literal["InitDecl"] = "InitDecl"
    store: Reference  # -> StoreDecl
    value: Value


class Unit(BaseModel):
    obj_type: Literal["Unit"] = "Unit"
    name: str
    symbol: str | None = None
    unit_ref: Reference | None = None  # -> Unit


class Binding(BaseModel):
    obj_type: Literal["Binding"] = "Binding"
    name: str
    variable: MemberCall


class ConnectStatement(BaseModel):
    obj_type: Literal["ConnectStatement"] = "ConnectStatement"
    instance: MemberCall
    inputBindings: list[Binding] = []
    outputBindings: list[Binding] = []


TypeDef = Union[PrimitiveType, StructType, TypeAlias, RemoteCallableType]

ModelElement = Annotated[
    Union[
        PrimitiveType,
        StructType,
        TypeAlias,
        RemoteCallableType,
        VarDef,
        Unit,
        StoreDecl,
        InitDecl,
        ConnectStatement,
    ],
    Field(discriminator="obj_type"),
]


class ASTModel(BaseModel):
    obj_type: Literal["Model"] = "Model"
    elements: list[ModelElement] = []
