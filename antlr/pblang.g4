grammar pblang;

model
    : (typeDef | definition | unit | processDef | storeDef | compositeDef | sbmlModel)* EOF
    ;

typeDef
    : 'type' name=ID (builtin='builtin')? ('extends' ID)? ('default' defaultValue)? ('update' ID)? namedType*
    ;

namedType
    : name=ID ':' ('maybe' '[' optional_type_ref=ID ']')? type_ref=ID ('default' defaultValue)? ('[' unit_ref=ID ']')?
    ;

defaultValue
    : INT | FLOAT | STRING | 'true' | 'false'
    ;

schemaItem
    : name=ID ':' type_ref=ID ('default' defaultValue)? ('[' unit_ref=ID ']')?
    ;

storeDef
    : 'store_def' name=ID ('parent' store_def_ref=ID)? ('state_def' storeDefStateDef)*
    ;

storeDefStateDef
    : schemaItem
    ;

unit
    : 'unit' name=ID ':' (('[' STRING ']') | ID)
    ;

sbmlModel
    : 'sbml' name=ID 'file' STRING sbmlParameter* sbmlVariable*
    ;

sbmlParameter
    : 'param' schemaItem
    ;

sbmlVariable
    : 'var' schemaItem
    ;

processDef
    : 'process_def' ID pythonPath?
        processParameter*
        processVariable*
        ('inputs' processInput*)?
        ('outputs' processOutput*)?
        ('updates' update*)?
    ;

pythonPath
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
    : 'process' name=ID ':' process_def_ref=ID ('stores' store_def_refs+=ID*)?
    ;

store
    : 'store' name=ID ':' store_def=ID*
    ;

compositeDef
    : 'composite_def' name=ID store* process*
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
