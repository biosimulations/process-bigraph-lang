// The .pblang language: the Langium form of the grammar in docs/v2/design.md. A module is a flat list of
// statements; bind.ts binds the AST to the object model (model.ts), check.ts verifies it.
grammar Pblang

entry Module:
    ('module' name=QualifiedName ';')?
    statements+=Statement*;

QualifiedName returns string:
    ID ('.' ID)*;

Statement:
    docs+=DOC* body=StatementBody;

StatementBody:
    Import | Param | Meta | Options | Interface | ModelDecl | Composite | Emit;

// --- module-level ----------------------------------------------------------------------------------------

// `import a.b.{X, Y};` lexes `a.b.{` as one token, so the dotted module name cannot swallow the `.{`
Import:
      'import' modulePath=IMPORT_PATH names+=ImportedName (',' names+=ImportedName)* '}' ';'
    | 'import' module=QualifiedName ';';

// an imported interface name is a declaration the edges can reference
ImportedName:
    name=ID;

// a param name may coincide with a keyword (`param step`), as keys may
Param:
    'param' name=TypeName ':' type=TypeExpr ('=' default=Value)? ('choices' choices=ListLiteral)? ';';

Meta:
    'meta' block=DictLiteral;

Options:
    'options' block=DictLiteral;

Emit:
    'emit' (alias=ID | address=STRING) '{' (paths+=Path (',' paths+=Path)*)? '}' ('with' config=DictLiteral)? ';';

// --- interface declarations (headers) ---------------------------------------------------------------------

Interface:
    kind=('process' | 'step' | 'adapter') name=ID ('at' address=STRING)? '{'
        ('config' '{' config+=Field* '}')?
        ('inputs' inputs=FaceBody)?
        ('outputs' outputs=FaceBody)?
    '}';

FaceBody:
    {infer FaceBody} '{' (open?='...' | fields+=Field*) '}';

Field:
    docs+=DOC* name=Key ':' type=TypeExpr ('=' default=Value)? ';';

type IfaceLike = Interface | ImportedName;

// --- model declarations (headers and sorts) ---------------------------------------------------------------

ModelDecl:
    'model' name=ID ('from' source=STRING)? '{' items+=ModelItem* '}';

ModelItem:
    ModelTime | ModelBlock | ModelMeta;

ModelTime:
    'time' '@' units=STRING ';';

ModelBlock:
    kind=('compartments' | 'species' | 'parameters') '{' fields+=Field* (open?='...')? '}';

ModelMeta:
    'meta' block=DictLiteral;

// --- the composite tree -----------------------------------------------------------------------------------

Composite:
    'composite' (name=Key)? '{' decls+=NodeDecl* '}';

NodeDecl:
    docs+=DOC* body=NodeBody;

NodeBody:
    Store | Node | PlainEdge | CompositeEdge | SharedEdge | SchemaBlock;

Store:
    'store' name=Key (':' type=TypeExpr)? ('=' value=Value)? ';';

Node:
    'node' name=Key (':' type=TypeExpr)? '{' decls+=NodeDecl* '}';

SchemaBlock:
    'schema' block=DictLiteral;

PlainEdge:
    kind=('process' | 'step') name=Key head=EdgeHead
    ('every' interval=Scalar)? ('priority' priority=Scalar)?
    '{' items+=EdgeItem* '}';

SharedEdge:
    'shared' 'process' name=Key head=EdgeHead '{' items+=EdgeItem* '}';

CompositeEdge:
    'composite' name=Key ('every' interval=Scalar)? ('at' address=STRING)? '{' items+=CompositeItem* '}';

EdgeHead:
      ':' 'shared' sharedRef=Key
    | ':' iface=[IfaceLike:ID] ('at' address=Address)?
    | 'at' address=Address;

Address:
    {infer Address} (literal=STRING | site=SiteValue | param=PARAM);

Scalar:
    {infer Scalar} (int=INT | float=FLOAT | param=PARAM);

EdgeItem:
    ConfigBlock | InputsBlock | OutputsBlock | PortsBlock | ExtraBlock;

CompositeItem:
    EdgeItem | BridgeBlock | InterfaceBlock | OptionsBlock | InnerBlock;

ConfigBlock:
    'config' block=DictLiteral;

InputsBlock:
    'inputs' block=WireBlock;

OutputsBlock:
    'outputs' block=WireBlock;

PortsBlock:
    {infer PortsBlock} 'ports' '{' ('inputs' '{' inputs+=Field* '}')? ('outputs' '{' outputs+=Field* '}')? '}';

ExtraBlock:
    'extra' block=DictLiteral;

BridgeBlock:
    'bridge' block=WireBlock;

InterfaceBlock:
    'interface' block=DictLiteral;

OptionsBlock:
    'options' block=DictLiteral;

InnerBlock:
    {infer InnerBlock} 'composite' '{' decls+=NodeDecl* '}';

// --- wires and paths --------------------------------------------------------------------------------------

WireBlock:
    {infer WireBlock} '{' (wires+=Wire (',' wires+=Wire)* ','?)? '}';

Wire:
    port=Key ('->' path=Path | block=WireBlock);

// `../fields.acetate[0][1]`: `..` segments are followed by `/`, keys are joined by `.`, indices attach as `[i]`
Path:
    segments+=Segment (('.' | '/') segments+=Segment | segments+=Index)*;

Segment:
    {infer Segment} (key=Key | up?='..' | star?='*');

Index:
    '[' index=INT ']';

// --- values -----------------------------------------------------------------------------------------------

Value:
    IntLiteral | FloatLiteral | StringLiteral | BoolLiteral | NullLiteral | ParamRef
    | SiteValue | DictLiteral | ListLiteral | TupleLiteral | ArrayLiteral | FileLiteral | ModelRef;

IntLiteral:
    value=INT;

FloatLiteral:
    value=FLOAT;

StringLiteral:
    value=STRING;

BoolLiteral:
    value=('true' | 'false');

NullLiteral:
    {infer NullLiteral} 'null';

ParamRef:
    value=PARAM;

SiteValue:
    {infer SiteValue} '?' ('(' default=Value ')')? ('as' sort=TypeExpr)?;

DictLiteral:
    {infer DictLiteral} '{' (entries+=Entry (',' entries+=Entry)* ','?)? '}';

Entry:
    key=Key '=' value=Value;

ListLiteral:
    {infer ListLiteral} '[' (items+=Value (',' items+=Value)* ','?)? ']';

TupleLiteral:
    {infer TupleLiteral} '(' (items+=Value (',' items+=Value)* ','?)? ')';

ArrayLiteral:
    'array' '(' data=ArrayData (',' options+=Entry)* ')';

ArrayData:
    ListLiteral | FileLiteral;

FileLiteral:
    'file' '(' path=STRING ')';

// a model site filled by a model header: `store m : ODEModel = Caravagna2010;`
ModelRef:
    model=[ModelDecl:ID];

// --- types ------------------------------------------------------------------------------------------------

TypeExpr:
    options+=PrimaryType ('|' options+=PrimaryType)*;

PrimaryType:
    NamedType | LinkType | StructType | RawType;

// `float{0.5}`: bigraph-schema's default-in-type form, kept so that schemas carrying defaults round-trip
NamedType:
    name=TypeName ('<' args+=TypeArg (',' args+=TypeArg)* '>')?
    ('[' dims+=Dim (',' dims+=Dim)* ']')? ('@' units=STRING)? ('{' default=Value '}')?;

TypeArg:
    {infer TypeArg} (type=TypeExpr | int=INT | float=FLOAT);

Dim:
    {infer Dim} (size=INT | name=ID);

LinkType:
    'link' '<' inputs=StructType ',' outputs=StructType '>';

StructType:
    {infer StructType} '{' fields+=Field* '}';

RawType:
    raw=STRING;

// keywords are allowed as type names and as keys (`every = 1`, `process = {…}` are real config keys)
TypeName returns string:
    ID | Keyword;

Key returns string:
    ID | STRING | Keyword;

Keyword returns string:
    'process' | 'step' | 'adapter' | 'composite' | 'shared' | 'node' | 'store' | 'schema' | 'import' | 'param'
    | 'meta' | 'options' | 'emit' | 'interface' | 'model' | 'time' | 'species' | 'parameters' | 'compartments'
    | 'config' | 'inputs' | 'outputs' | 'ports' | 'extra' | 'bridge' | 'every' | 'priority' | 'at' | 'as'
    | 'from' | 'with' | 'choices' | 'array' | 'file' | 'link' | 'module';

hidden terminal WS: /\s+/;
terminal DOC: /\/\/\/[^\n\r]*/;
hidden terminal SL_COMMENT: /\/\/[^\n\r]*/;
hidden terminal ML_COMMENT: /\/\*[\s\S]*?\*\//;
terminal IMPORT_PATH: /[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)*\.\{/;
terminal PARAM: /\$\{[A-Za-z_][A-Za-z0-9_]*\}/;
terminal FLOAT returns number: /-?([0-9]+\.[0-9]*|\.[0-9]+)([eE][+-]?[0-9]+)?|-?[0-9]+[eE][+-]?[0-9]+/;
terminal INT returns number: /-?[0-9]+/;
terminal ID: /[_a-zA-Z][\w_]*/;
terminal STRING: /"(\\.|[^"\\])*"/;
