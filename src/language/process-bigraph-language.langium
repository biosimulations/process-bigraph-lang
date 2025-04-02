grammar ProcessBigraphLanguage

entry Model:
    (types+=Type)* (processes+=Process)*;

Type:
    'type' name=ID ('extends' superType=[Type])? ('default' Value)?;

Value:
    val=(STRING | INT | ID | FLOAT);

SchemaItem:
    name=ID ':' type=[Type] ('default' default=Value)?;

Process:
    'process' name=ID  
        ('param' configs+=SchemaItem) 
        ('var' vars+=SchemaItem) 
        ('inputs' inputs+=[SchemaItem]) 
        ('outputs' outputs+=[SchemaItem]) 
        ('updates' updates+=Update);

Update:
    (lhs=[SchemaItem]) ':=' (rhs=Expression) ';';

Statement:
    Definition | Evaluation;

Evaluation:
    expression=Expression ';';

Definition:
    'def' name=ID ('(' args+=DeclaredParameter (',' args+=DeclaredParameter)* ')')?
    ':' expr=Expression ';';

DeclaredParameter:
    name=ID;

type AbstractDefinition = Definition | DeclaredParameter | SchemaItem;


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
    {infer FunctionCall} func=[AbstractDefinition] ('(' args+=Expression (',' args+=Expression)* ')')?;

hidden terminal WS: /\s+/;
terminal FLOAT returns number: /[0-9]+(\.[0-9]+)?/;
terminal ID: /[_a-zA-Z][\w_]*/;
terminal INT returns number: /[0-9]+/;
terminal STRING: /"(\\.|[^"\\])*"|'(\\.|[^'\\])*'/;

hidden terminal ML_COMMENT: /\/\*[\s\S]*?\*\//;
hidden terminal SL_COMMENT: /\/\/[^\n\r]*/;
