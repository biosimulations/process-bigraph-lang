grammar ProcessBigraphLanguage

entry Model:
    elements+=ModelElement*;

ModelElement:
    TypeDef | VarDef | Unit | RemoteDef;

RemoteDef:
    'remote' name=ID '{'
        ('config' config=StructType)?
        'call' signature=CallableSignature
    '}';

CallableSignature:
    '(' params+=ParamDecl (',' params+=ParamDecl)* ')' '->'
    '(' results+=ParamDecl (',' results+=ParamDecl)* ')';

ParamDecl:
    name=ID ':' type=TypeRef;

TypeDef:
    PrimitiveType | StructType | TypeAlias;

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

SimpleTypeRef:
    type=[TypeDef:ID];

VarDef:
    'let' name=ID ':' type=TypeRef ('=' value=Value)? ';';

Value:
    IntLiteral |
    FloatLiteral |
    StringLiteral |
    BoolLiteral |
    VarRef |
    StructLiteral |
    ArrayLiteral |
    MapLiteral |
    TupleLiteral;

StructLiteral:
    '{' (fields+=StructFieldValue (',' fields+=StructFieldValue)* ','?)? '}';

StructFieldValue:
    name=ID '=' value=Value;

ArrayLiteral:
    '[' (elements+=Value (',' elements+=Value)* ','?)? ']';

MapLiteral:
    '{' (entries+=MapEntry (',' entries+=MapEntry)* ','?)? '}';

MapEntry:
    key=Value '=' value=Value;

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

VarRef:
    ref=[VarDef];

Unit:
    "unit" name=ID ":" (('[' symbol=STRING ']') | (unit_ref=[Unit]));

hidden terminal WS: /\s+/;
terminal FLOAT returns number: /[0-9]+(\.[0-9]+)?/;
terminal ID: /[_a-zA-Z][\w_]*/;
terminal INT returns number: /[0-9]+/;
terminal STRING: /"(\\.|[^"\\])*"|'(\\.|[^'\\])*'/;

hidden terminal ML_COMMENT: /\/\*[\s\S]*?\*\//;
hidden terminal SL_COMMENT: /\/\/[^\n\r]*/;
