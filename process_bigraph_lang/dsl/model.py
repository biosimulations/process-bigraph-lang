from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field


class Reference(BaseModel):
    ref: str
    ref_text: str


SchemaItemRef = Reference
TypeRef = Reference
UnitRef = Reference
DefinitionRef = Reference
StoreRef = Reference

BinaryOp = Literal["+", "-", "*", "/", "^", "%"]


class DefaultValue(BaseModel):
    val: int | float


class DeclaredParameter(BaseModel):
    obj_type: Literal["DeclaredParameter"] = Field(default="DeclaredParameter")
    name: str


class SchemaItem(BaseModel):
    obj_type: Literal["SchemaItem"] = Field(default="SchemaItem")
    name: str
    type: TypeRef
    default: DefaultValue | None = None
    unit_ref: UnitRef | None = None


class Store(BaseModel):
    obj_type: Literal["Store"] = Field(default="Store")
    name: str
    parent: StoreRef | None = None
    states: list[SchemaItem] | None = None


class Update(BaseModel):
    lhs: SchemaItemRef
    rhs: "Expression"


class ProcessDef(BaseModel):
    obj_type: Literal["ProcessDef"] = Field(default="ProcessDef")
    name: str
    params: list[SchemaItem]
    vars: list[SchemaItem]
    inputs: list[SchemaItemRef]
    outputs: list[SchemaItemRef]
    updates: list[Update]


class BinaryExpression(BaseModel):
    obj_type: Literal["BinaryExpression"] = Field(default="BinaryExpression")
    operator: BinaryOp
    left: "Expression"
    right: "Expression"


class FunctionCall(BaseModel):
    obj_type: Literal["FunctionCall"] = Field(default="FunctionCall")
    func: DefinitionRef
    args: list["Expression"]


class VariableRef(BaseModel):
    obj_type: Literal["VariableRef"] = Field(default="VariableRef")
    variable: Reference


class NumberLiteral(BaseModel):
    obj_type: Literal["NumberLiteral"] = Field(default="NumberLiteral")
    value: float


Expression = Annotated[
    Union[BinaryExpression | FunctionCall | VariableRef | NumberLiteral], Field(discriminator="obj_type")
]


class Definition(BaseModel):
    obj_type: Literal["Definition"] = Field(default="Definition")
    name: str
    args: list[DeclaredParameter]
    builtin: Literal["builtin"] | None = None
    expr: Expression | None = None


class Type(BaseModel):
    obj_type: Literal["Type"] = Field(default="Type")
    name: str
    builtin: Literal["builtin"] | None = None
    superType: Reference | None = None
    default: DefaultValue | None = None
    update: DefaultValue | None = None
    subtypes: list[Reference] = []


class Unit(BaseModel):
    obj_type: Literal["Unit"] = Field(default="Unit")
    name: str
    symbol: str | None = None
    unit_ref: UnitRef | None = None


class Model(BaseModel):
    obj_type: Literal["Model"] = Field(default="Model")
    definitions: list[Definition]
    types: list[Type]
    units: list[Unit]
    processDefs: list[ProcessDef]
    stores: list[Store]
