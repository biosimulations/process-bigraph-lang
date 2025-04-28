grammar ProcessBigraphLanguage

entry Model:
    ((types+=Type) | (definitions+=Definition) | (units+=Unit) | (processDefs+=ProcessDef) | (stores+=Store) | (compositeDefs+=CompositeDef))*;

Type:
    'type' name=ID (builtin='builtin')? ('extends' superType=[Type])? ('default' default=DefaultValue)? ('update' update=[Definition])? (subtypes+=NamedType)*;

NamedType:
    name=ID ':' (('maybe' "[" optional_type=[Type] "]") | type=[Type])
    ('default' default=DefaultValue)? ("[" unit_symbol=[Unit] "]")?;

DefaultValue:
    val=(INT | FLOAT);

SchemaItem:
    name=ID ':' type=[Type] ('default' default=DefaultValue)? ("[" unit_symbol=[Unit] "]")?;

Store:
    'store' name=ID ('parent' parent=[Store])?
        ('state' item+=SchemaItem)*;

Unit:
    "unit" name=ID ":" (('[' symbol=STRING ']') | (unit_ref=[Unit]));

ProcessDef:
    'process_def' name=ID
        ('param' configs+=SchemaItem)*
        ('var' vars+=SchemaItem)*
        ('inputs' inputs+=[SchemaItem]*)?
        ('outputs' outputs+=[SchemaItem]*)?
        ('updates' updates+=Update*)?;

Process:
    name=ID ':' process_def=[ProcessDef] ('stores' stores+=[Store]*);

CompositeDef infers ProcessDef:
    'composite_def' name=ID
        ('stores' stores+=[Store]*)?
        ('process' process+=Process)*;

Update:
    (lhs=[SchemaItem]) ':=' (rhs=Expression) ';';

Definition:
    'def' name=ID ('(' args+=DeclaredParameter (',' args+=DeclaredParameter)* ')')?
    ':' (builtin='builtin' | (expr=Expression ';'));

DeclaredParameter:
    name=ID;

type VariableDefinition = Definition | DeclaredParameter | SchemaItem;


Expression:
    Addition;

Addition infers Expression:
    Multiplication ({infer BinaryExpression.left=current} operator=('+' | '-') right=Multiplication)*;

Multiplication infers Expression:
    Exponentiation ({infer BinaryExpression.left=current} operator=('*' | '/') right=Exponentiation)*;

Exponentiation infers Expression:
    Modulo ({infer BinaryExpression.left=current} operator='^' right=Modulo)*;

Modulo infers Expression:
    PrimaryExpression ({infer BinaryExpression.left=current} operator='%' right=PrimaryExpression)*;

PrimaryExpression infers Expression:
    '(' Expression ')' |
    {infer NumberLiteral} value=FLOAT |
    {infer FunctionCall} func=[Definition] ('(' args+=Expression (',' args+=Expression)* ')') |
    {infer VariableRef} variable=[VariableDefinition:ID];

hidden terminal WS: /\s+/;
terminal FLOAT returns number: /[0-9]+(\.[0-9]+)?/;
terminal ID: /[_a-zA-Z][\w_]*/;
terminal INT returns number: /[0-9]+/;
terminal STRING: /"(\\.|[^"\\])*"|'(\\.|[^'\\])*'/;

hidden terminal ML_COMMENT: /\/\*[\s\S]*?\*\//;
hidden terminal SL_COMMENT: /\/\/[^\n\r]*/;
