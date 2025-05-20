grammar ProcessBigraphLanguage

entry Model:
    ((types+=Type) |
     (definitions+=Definition) |
     (units+=Unit) |
     (processDefs+=ProcessDef) |
     (store_defs+=StoreDef) |
     (compositeDefs+=CompositeDef) |
     (sbmlModels+=SbmlModel) |
     (stepDefs+=StepDef) |
     (procDefs+=ProcDef) |
     ('store' storeNodes+=StoreNode) |
     (step_calls+=StepCall) |
     (proc_calls+=ProcCall))*;

Type:
    'type' name=ID (builtin='builtin')? ('extends' superType=[Type])? ('default' default=DefaultValue)? ('update' update=[Definition])? (subtypes+=NamedType)*;

NamedType:
    name=ID ':' ((option=('maybe' | 'list' | 'array')  "[" optional_type=[Type] "]") | type=[Type])
    ('default' default=DefaultValue)? ("[" unit_ref=[Unit] "]")?;

DefaultValue:
    val=(INT | FLOAT | STRING | 'true' | 'false');

SchemaItem:
    name=ID ':' type=[Type] ('default' default=DefaultValue)? ("[" unit_ref=[Unit] "]")?;

StoreDef:
    'store_def' name=ID ('parent' parent=[StoreDef])?
        ('state_def' states+=SchemaItem)*;

Unit:
    "unit" name=ID ":" (('[' symbol=STRING ']') | (unit_ref=[Unit]));

SbmlModel:
    'sbml' name=ID 'file' filepath=STRING
        ('param' params+=SchemaItem)*
        ('var' vars+=SchemaItem)*;

PythonPath:
    'path' path+=ID ("." path+=ID)*;

ProcessDef:
    'process_def' name=ID python_path=PythonPath?
        ('param' params+=SchemaItem)*
        ('var' vars+=SchemaItem)*
        ('inputs' inputs+=[SchemaItem]*)?
        ('outputs' outputs+=[SchemaItem]*)?
        ('updates' updates+=Update*)?;

Store:
    'store' name=ID ':' store_def=[StoreDef];

StoreNode:
    name=ID (
        ('=' optional_val=DefaultValue) |
        (':' optional_type=[Type] ('=' optional_val=DefaultValue)?) |
        ('{' child_defs+=StoreNode (',' child_defs+=StoreNode)* '}'));

StepDef:
    'step' name=ID python_path=PythonPath?
        ('param' params+=SchemaItem)*
        ('var' vars+=SchemaItem)*
        ('inputs' inputs+=[SchemaItem]*)?
        ('outputs' outputs+=[SchemaItem]*)?;

ProcDef:
    'proc' name=ID python_path=PythonPath?
        ('param' params+=SchemaItem)*
        ('var' vars+=SchemaItem)*
        ('inputs' inputs+=[SchemaItem]*)?
        ('outputs' outputs+=[SchemaItem]*)?;

StepCall:
    ('set' '(' (output_node_list=StoreNodeList)? ')')
    (('as' | '=') step_def_ref=[StepDef])
    ('[' (config_node_list=StoreNodeList)? ']')
    ('(' (input_node_list=StoreNodeList)? ')');

ProcCall:
    ('update' '(' (output_node_list=StoreNodeList)? ')')
    (('using' | '<=') process_def_ref=[ProcDef])
    ('[' (config_node_list=StoreNodeList)? ']')
    ('(' (input_node_list=StoreNodeList)? ')');

StoreNodeList:
    (store_node_refs+=[StoreNode]) (',' store_node_refs+=[StoreNode])*;

Process:
    'process' name=ID ':' process_def=[ProcessDef] ('stores' stores+=[Store]*);

CompositeDef:
    'composite_def' name=ID
        stores+=Store*
        processes+=Process*;

Update:
    (lhs=[SchemaItem]) ':=' (rhs=Expression) ';';

Definition:
    'def' name=ID ('(' args+=DeclaredParameter (',' args+=DeclaredParameter)* ')')?
    ':' (builtin='builtin' | (expr=Expression ';'));

DeclaredParameter:
    name=ID;

type VariableDefinition = DeclaredParameter | SchemaItem;


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
