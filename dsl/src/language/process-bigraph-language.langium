grammar ProcessBigraphLanguage

entry Model:
    elements+=ModelElement*;

ModelElement:
    TypeDef | VarDef | Unit | StoreDecl | InitDecl | ConnectStatement;


// Without `at`, a remote type is an interface: its instances are address sites whose
// implementation is filled in later (see SiteLiteral).
RemoteCallableType:
    'remote' kind=('step' | 'process') name=ID ('at' address=STRING)? '{'
        ('config' config=TupleType)?
        ('inputs' inputs=TupleType)?
        ('outputs' outputs=TupleType)?
    '}';

ConnectStatement:
    'connect' instance=MemberCall
    ('inputs' '(' (inputBindings+=Binding (',' inputBindings+=Binding)*)? ')')?
    ('outputs' '(' (outputBindings+=Binding (',' outputBindings+=Binding)*)? ')')?
    ';';

Binding:
    name=ID '=' variable=MemberCall;

MemberCall:
    element=[NamedElement:ID]
    ({infer MemberCall.previous=current} "." element=[NamedElement:ID])* ;

type NamedElement = VarDef | Field | StoreDecl | ParamDecl;

StoreDecl:
    'store' name=ID ':' type=TypeRef ';';

InitDecl:
    'init' store=[StoreDecl:ID] '=' value=Value ';';

TypeDef:
    PrimitiveType | StructType | TypeAlias | RemoteCallableType;

PrimitiveType:
    'type' name=ID 'builtin';

StructType:
    'struct' name=ID '{'
        fields+=Field*
    '}';

TypeAlias:
    'type' name=ID '=' type=TypeRef;

Field:
    name=ID ':' type=TypeRef ('=' default=Value)? ';';

TypeRef:
    ArrayType | MapType | TupleType | SimpleTypeRef;

ArrayType:
    'array' '<' elementType=TypeRef '>';

MapType:
    'map' '<' keyType=TypeRef ',' valueType=TypeRef '>';

TupleType:
    '(' elements+=ParamDecl (',' elements+=ParamDecl)* ')';

ParamDecl:
    name=ID ':' type=TypeRef;

SimpleTypeRef:
    type=[TypeDef:ID];

VarDef:
    'let' (name=ID | lhs=TuplePattern) ':' type=TypeRef ('=' value=Value)? ';';

TuplePattern:
    '(' bindings+=TupleBinding (',' bindings+=TupleBinding)* ')';

TupleBinding:
    name=ID ':' type=TypeRef;

Value:
    IntLiteral |
    FloatLiteral |
    StringLiteral |
    BoolLiteral |
    MemberCall |
    StructLiteral |
    ArrayLiteral |
    MapLiteral |
    TupleLiteral |
    CallableLiteral |
    SiteLiteral;

// An open value (a template site) to be filled before the composite runs: `?` is required,
// `?(v)` is optional with default v.
SiteLiteral:
    {infer SiteLiteral} '?' ('(' default=Value ')')?;

CallableLiteral:
    callable_type=[RemoteCallableType:ID] '(' (configArgs+=ConfigArg (',' configArgs+=ConfigArg)* ','?)? ')';

ConfigArg:
    name=ID '=' value=Value;

StructLiteral:
    '{' (fields+=StructFieldValue (',' fields+=StructFieldValue)* ','?)? '}';

StructFieldValue:
    name=ID '=' value=Value;

ArrayLiteral:
    '[' (elements+=Value (',' elements+=Value)* ','?)? ']';

// Map keys are literals so that '{ name = … }' is always a struct literal.
// An empty '{}' parses as a StructLiteral and is accepted where a map is expected.
MapLiteral:
    '{' entries+=MapEntry (',' entries+=MapEntry)* ','? '}';

MapEntry:
    key=MapKey '=' value=Value;

MapKey:
    StringLiteral | IntLiteral | FloatLiteral | BoolLiteral;

TupleLiteral:
    '(' (fields+=TupleFieldValue (',' fields+=TupleFieldValue)* ','?)? ')';

TupleFieldValue:
    name=ID '=' value=Value;

IntLiteral:
    value=INT;

FloatLiteral:
    value=FLOAT;

StringLiteral:
    value=STRING;

BoolLiteral:
    value=('true' | 'false');

Unit:
    "unit" name=ID ":" (('[' symbol=STRING ']') | (unit_ref=[Unit]));

hidden terminal WS: /\s+/;
terminal FLOAT returns number: /-?([0-9]+\.[0-9]*|\.[0-9]+)([eE][+-]?[0-9]+)?/;
terminal INT returns number: /-?[0-9]+/;
terminal ID: /[_a-zA-Z][\w_]*/;

terminal STRING: /"(\\.|[^"\\])*"|'(\\.|[^'\\])*'/;

hidden terminal ML_COMMENT: /\/\*[\s\S]*?\*\//;
hidden terminal SL_COMMENT: /\/\/[^\n\r]*/;
