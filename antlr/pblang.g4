grammar pblang;

model
    : (typeDef | definition | unit | processDef | store | compositeDef | sbmlModel)* EOF
    ;

typeDef
    : 'type' name=ID (builtin='builtin')? ('extends' ID)? ('default' defaultValue)? ('update' ID)? namedType*
    ;

namedType
    : name=ID ':' ('maybe' '[' optional_type_ref=ID ']')? type_ref=ID ('default' defaultValue)? ('[' unit_ref=ID ']')?
    ;

defaultValue
    : INT | FLOAT
    ;

schemaItem
    : name=ID ':' type_ref=ID ('default' defaultValue)? ('[' unit_ref=ID ']')?
    ;

store
    : 'store' ID ('parent' ID)? ('state' storeState)*
    ;

storeState
    : schemaItem
    ;

unit
    : 'unit' ID ':' (('[' STRING ']') | ID)
    ;

sbmlModel
    : 'sbml' ID 'file' STRING sbmlParameter* sbmlVariable*
    ;

sbmlParameter
    : 'param' schemaItem
    ;

sbmlVariable
    : 'var' schemaItem
    ;

processDef
    : 'process_def' ID pythonRef?
        processParameter*
        processVariable*
        ('inputs' processInput*)?
        ('outputs' processOutput*)?
        ('updates' update*)?
    ;

pythonRef
    : 'path' ID ('.' ID)*
    ;

processParameter
    : 'param' schemaItem
    ;

processVariable
    : 'var' schemaItem
    ;

processInput
    : ID
    ;

processOutput
    : ID
    ;

process
    : name=ID ':' process_def_ref=ID ('stores' store_def=ID*)?
    ;

compositeDef
    : 'composite_def' ID ('stores' ID*)? ('process' process)*
    ;

update
    : lhs=ID ':=' expression ';'
    ;

definition
    : 'def' ID ('(' declaredParameter (',' declaredParameter)* ')')? ':' (builtin='builtin' | (expression ';'))
    ;

declaredParameter
    : ID
    ;

expression
    : addition
    ;

addition
    : multiplication (('+' | '-') multiplication)*
    ;

multiplication
    : exponentiation (('*' | '/') exponentiation)*
    ;

exponentiation
    : modulo ('^' modulo)*
    ;

modulo
    : primaryExpression ('%' primaryExpression)*
    ;

primaryExpression
    : '(' expression ')'
    | FLOAT
    | ID ('(' expression (',' expression)* ')')?
    | ID
    ;

ID: [_a-zA-Z][_a-zA-Z0-9]*;
FLOAT: [0-9]+('.'[0-9]+)?;
INT: [0-9]+;
STRING: '"' ( '\\' . | ~('\\'|'"') )* '"';
WS: [ \t\r\n]+ -> skip;
ML_COMMENT: '/*' .*? '*/' -> skip;
SL_COMMENT: '//' ~[\r\n]* -> skip;
