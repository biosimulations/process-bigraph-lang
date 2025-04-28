from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field


class Reference(BaseModel):
    ref: str
    ref_text: str


class DefaultValue(BaseModel):
    val: int | float


class DeclaredParameter(BaseModel):
    type: Literal["DeclaredParameter"] = Field(default="DeclaredParameter")
    name: str


class BinaryExpression(BaseModel):
    type: Literal["BinaryExpression"] = Field(default="BinaryExpression")
    operator: Literal["+", "-", "*", "/", "^", "%"]
    left: "Expression"
    right: "Expression"


class FunctionCall(BaseModel):
    type: Literal["FunctionCall"] = Field(default="FunctionCall")
    func: Reference
    args: list["Expression"]


class VariableRef(BaseModel):
    type: Literal["VariableRef"] = Field(default="VariableRef")
    variable: Reference


class NumberLiteral(BaseModel):
    type: Literal["NumberLiteral"] = Field(default="NumberLiteral")
    value: float


Expression = Annotated[
    Union[BinaryExpression | FunctionCall | VariableRef | NumberLiteral], Field(discriminator="type")
]


class Definition(BaseModel):
    type: Literal["Definition"] = Field(default="Definition")
    name: str
    args: list[DeclaredParameter]
    builtin: Literal["builtin"] | None = None
    expr: Expression | None = None


class Type(BaseModel):
    type: Literal["Type"] = Field(default="Type")
    name: str
    builtin: Literal["builtin"] | None = None
    superType: Reference | None = None
    default: DefaultValue | None = None
    update: DefaultValue | None = None
    subtypes: list[Reference] = []


class Unit(BaseModel):
    type: Literal["Unit"] = Field(default="Unit")
    name: str
    symbol: str | None = None
    unit_ref: Reference | None = None


class Model(BaseModel):
    type: Literal["Model"] = Field(default="Model")
    definitions: list[Definition]
    types: list[Type]
    units: list[Unit]
