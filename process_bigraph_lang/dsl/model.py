from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field


class NamedObject(BaseModel):
    name: str


class Reference(BaseModel):
    ref: str
    ref_text: str
    ref_object: NamedObject | None = Field(default=None, exclude=True)


SchemaItemRef = Reference
TypeRef = Reference
UnitRef = Reference
DefinitionRef = Reference
StoreDefRef = Reference
StoreRef = Reference
ProcessDefRef = Reference
StoreNodeRef = Reference
StepDefRef = Reference
ProcDefRef = Reference
ParameterRef = Reference

BinaryOp = Literal["+", "-", "*", "/", "^", "%"]


class DefaultValue(BaseModel):
    val: int | float | str | bool


class DeclaredParameter(NamedObject):
    obj_type: Literal["DeclaredParameter"] = Field(default="DeclaredParameter")


class SchemaItem(NamedObject):
    obj_type: Literal["SchemaItem"] = Field(default="SchemaItem")
    type_ref: TypeRef
    default: DefaultValue | None = None
    unit_ref: UnitRef | None = None


class StoreDef(NamedObject):
    obj_type: Literal["StoreDef"] = Field(default="StoreDef")
    parent: StoreDefRef | None = None
    states: list[SchemaItem] | None = None


class Store(NamedObject):
    obj_type: Literal["Store"] = Field(default="Store")
    store_def: StoreDefRef


class Parameter(NamedObject):
    obj_type: Literal["Parameter"] = Field(default="Parameter")
    default: DefaultValue
    type_ref: TypeRef | None = None
    unit_ref: UnitRef | None = None


class Update(BaseModel):
    lhs: SchemaItemRef
    rhs: "Expression"


class PythonPath(BaseModel):
    obj_type: Literal["PythonPath"] = Field(default="PythonPath")
    path: list[str]


class EdgeDef(NamedObject):
    params: list[SchemaItem]
    vars: list[SchemaItem]
    inputs: list[SchemaItemRef]
    outputs: list[SchemaItemRef]
    python_path: PythonPath | None = None


class StepDef(EdgeDef):
    obj_type: Literal["StepDef"] = Field(default="StepDef")


class ProcDef(EdgeDef):
    obj_type: Literal["ProcDef"] = Field(default="ProcDef")


class ProcessDef(NamedObject):
    obj_type: Literal["ProcessDef"] = Field(default="ProcessDef")
    params: list[SchemaItem]
    vars: list[SchemaItem]
    inputs: list[SchemaItemRef]
    outputs: list[SchemaItemRef]
    updates: list[Update]
    python_path: PythonPath | None = None


class StoreNode(NamedObject):
    obj_type: Literal["StoreNode"] = Field(default="StoreNode")
    optional_val: DefaultValue | None = None
    optional_type: TypeRef | None = None
    child_defs: list["StoreNode"] | None = None


class StoreNodeList(BaseModel):
    obj_type: Literal["StoreNodeList"] = Field(default="StoreNodeList")
    store_node_refs: list[StoreNodeRef]


class ParameterList(BaseModel):
    obj_type: Literal["ParameterList"] = Field(default="ParameterList")
    parameter_refs: list[ParameterRef]


class StepCall(BaseModel):
    obj_type: Literal["StepCall"] = Field(default="StepCall")
    step_def_ref: StepDefRef
    output_node_list: StoreNodeList | None = None
    config_node_list: ParameterList | None = None
    input_node_list: StoreNodeList | None = None


class ProcCall(BaseModel):
    obj_type: Literal["ProcCall"] = Field(default="ProcCall")
    proc_def_ref: ProcDefRef
    output_node_list: StoreNodeList | None = None
    config_node_list: ParameterList | None = None
    input_node_list: StoreNodeList | None = None


class SbmlModel(NamedObject):
    obj_type: Literal["SbmlModel"] = Field(default="SbmlModel")
    filepath: str
    params: list[SchemaItem]
    vars: list[SchemaItem]


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


class Definition(NamedObject):
    obj_type: Literal["Definition"] = Field(default="Definition")
    args: list[DeclaredParameter]
    builtin: Literal["builtin"] | None = None
    expr: Expression | None = None


class Type(NamedObject):
    obj_type: Literal["Type"] = Field(default="Type")
    builtin: Literal["builtin"] | None = None
    superType: Reference | None = None
    default: DefaultValue | None = None
    update: DefaultValue | None = None
    subtypes: list[Reference] = []


class Unit(NamedObject):
    obj_type: Literal["Unit"] = Field(default="Unit")
    symbol: str | None = None
    unit_ref: UnitRef | None = None


class Process(NamedObject):
    obj_type: Literal["Process"] = Field(default="Process")
    process_def: ProcessDefRef
    stores: list[StoreRef] = []


class CompositeDef(NamedObject):
    obj_type: Literal["CompositeDef"] = Field(default="CompositeDef")
    stores: list[Store] = []
    processes: list[Process] = []


class Model(BaseModel):
    obj_type: Literal["Model"] = Field(default="Model")
    definitions: list[Definition]
    types: list[Type]
    units: list[Unit]
    processDefs: list[ProcessDef]
    store_defs: list[StoreDef]
    compositeDefs: list[CompositeDef]
    stepDefs: list[StepDef]
    procDefs: list[ProcDef]
    storeNodes: list[StoreNode]
    parameters: list[Parameter]
    step_calls: list[StepCall]
    proc_calls: list[ProcCall]
