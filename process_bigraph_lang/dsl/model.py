from typing import Annotated
from typing import Literal
from typing import Union

from pydantic import BaseModel
from pydantic import Field


class Reference(BaseModel):
    path: str = Field(alias="builtin_ref")


class DeclaredParameter(BaseModel):
    type: Literal["DeclaredParameter"] = Field(default="DeclaredParameter", alias="builtin_type")
    name: str


class BinaryExpression(BaseModel):
    type: Literal["BinaryExpression"] = Field(default="BinaryExpression", alias="builtin_type")
    operator: Literal["+", "-", "*", "/", "^", "%"]
    left: "AnnotatedExpression"
    right: "AnnotatedExpression"


class FunctionCall(BaseModel):
    type: Literal["FunctionCall"] = Field(default="FunctionCall", alias="builtin_type")
    func: Reference
    args: list["AnnotatedExpression"]


class VariableRef(BaseModel):
    type: Literal["VariableRef"] = Field(default="VariableRef", alias="builtin_type")
    variable: Reference

    @property
    def path(self) -> str:
        return self.variable.path


class NumberLiteral(BaseModel):
    type: Literal["NumberLiteral"] = Field(default="NumberLiteral", alias="builtin_type")
    value: float


Expression = Union[BinaryExpression | FunctionCall | VariableRef | NumberLiteral]
AnnotatedExpression = Annotated[Expression, Field(discriminator="type")]


class Definition(BaseModel):
    type: Literal["Definition"] = Field(default="Definition", alias="builtin_type")
    name: str
    args: list[DeclaredParameter]
    builtin: Literal["builtin"] | None = None
    expr: AnnotatedExpression | None = None


class Model(BaseModel):
    type: Literal["Model"] = Field(default="Model", alias="builtin_type")
    definitions: list[Definition]
