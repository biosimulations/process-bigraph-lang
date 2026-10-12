// The .pblang v2 language (files: .pbl), the Langium form of the grammar in docs/v2/design.md.
// It covers what the Python prototype (process_bigraph_lang/v2/parser.py) parses, and binds to the
// same model through process_bigraph_lang/v2/langium.py. Rule names carry a V2 prefix because v1 and
// v2 share one generated ast.ts while they coexist.
grammar PblangV2

entry V2Module:
    ('module' name=V2QualifiedName ';')?
    statements+=V2Statement*;

V2QualifiedName returns string:
    ID ('.' ID)*;

V2Statement:
    docs+=DOC* body=V2StatementBody;

V2StatementBody:
    V2Import | V2Param | V2Meta | V2Options | V2Interface | V2ModelDecl | V2Composite | V2Emit;

// --- module-level ----------------------------------------------------------------------------------------

// `import a.b.{X, Y};` lexes `a.b.{` as one token, so the dotted module name cannot swallow the `.{`
V2Import:
      'import' modulePath=IMPORT_PATH names+=V2ImportedName (',' names+=V2ImportedName)* '}' ';'
    | 'import' module=V2QualifiedName ';';

// an imported interface name is a declaration the edges can reference
V2ImportedName:
    name=ID;

// a param name may coincide with a keyword (`param step`), as keys may
V2Param:
    'param' name=V2TypeName ':' type=V2TypeExpr ('=' default=V2Value)? ('choices' choices=V2ListLiteral)? ';';

V2Meta:
    'meta' block=V2DictLiteral;

V2Options:
    'options' block=V2DictLiteral;

V2Emit:
    'emit' (alias=ID | address=STRING) '{' (paths+=V2Path (',' paths+=V2Path)*)? '}' ('with' config=V2DictLiteral)? ';';

// --- interface declarations (headers) ---------------------------------------------------------------------

V2Interface:
    kind=('process' | 'step' | 'adapter') name=ID ('at' address=STRING)? '{'
        ('config' '{' config+=V2Field* '}')?
        ('inputs' inputs=V2FaceBody)?
        ('outputs' outputs=V2FaceBody)?
    '}';

V2FaceBody:
    {infer V2FaceBody} '{' (open?='...' | fields+=V2Field*) '}';

V2Field:
    docs+=DOC* name=V2Key ':' type=V2TypeExpr ('=' default=V2Value)? ';';

type V2IfaceLike = V2Interface | V2ImportedName;

// --- model declarations (headers and sorts) ---------------------------------------------------------------

V2ModelDecl:
    'model' name=ID ('from' source=STRING)? '{' items+=V2ModelItem* '}';

V2ModelItem:
    V2ModelTime | V2ModelBlock | V2ModelMeta;

V2ModelTime:
    'time' '@' units=STRING ';';

V2ModelBlock:
    kind=('compartments' | 'species' | 'parameters') '{' fields+=V2Field* (open?='...')? '}';

V2ModelMeta:
    'meta' block=V2DictLiteral;

// --- the composite tree -----------------------------------------------------------------------------------

V2Composite:
    'composite' (name=V2Key)? '{' decls+=V2NodeDecl* '}';

V2NodeDecl:
    docs+=DOC* body=V2NodeBody;

V2NodeBody:
    V2Store | V2Node | V2PlainEdge | V2CompositeEdge | V2SharedEdge | V2SchemaBlock;

V2Store:
    'store' name=V2Key (':' type=V2TypeExpr)? ('=' value=V2Value)? ';';

V2Node:
    'node' name=V2Key (':' type=V2TypeExpr)? '{' decls+=V2NodeDecl* '}';

V2SchemaBlock:
    'schema' block=V2DictLiteral;

V2PlainEdge:
    kind=('process' | 'step') name=V2Key head=V2EdgeHead
    ('every' interval=V2Scalar)? ('priority' priority=V2Scalar)?
    '{' items+=V2EdgeItem* '}';

V2SharedEdge:
    'shared' 'process' name=V2Key head=V2EdgeHead '{' items+=V2EdgeItem* '}';

V2CompositeEdge:
    'composite' name=V2Key ('every' interval=V2Scalar)? ('at' address=STRING)? '{' items+=V2CompositeItem* '}';

V2EdgeHead:
      ':' 'shared' sharedRef=V2Key
    | ':' iface=[V2IfaceLike:ID] ('at' address=V2Address)?
    | 'at' address=V2Address;

V2Address:
    {infer V2Address} (literal=STRING | site=V2SiteValue | param=PARAM);

V2Scalar:
    {infer V2Scalar} (int=INT | float=FLOAT | param=PARAM);

V2EdgeItem:
    V2ConfigBlock | V2InputsBlock | V2OutputsBlock | V2PortsBlock | V2ExtraBlock;

V2CompositeItem:
    V2EdgeItem | V2BridgeBlock | V2InterfaceBlock | V2OptionsBlock | V2InnerBlock;

V2ConfigBlock:
    'config' block=V2DictLiteral;

V2InputsBlock:
    'inputs' block=V2WireBlock;

V2OutputsBlock:
    'outputs' block=V2WireBlock;

V2PortsBlock:
    {infer V2PortsBlock} 'ports' '{' ('inputs' '{' inputs+=V2Field* '}')? ('outputs' '{' outputs+=V2Field* '}')? '}';

V2ExtraBlock:
    'extra' block=V2DictLiteral;

V2BridgeBlock:
    'bridge' block=V2WireBlock;

V2InterfaceBlock:
    'interface' block=V2DictLiteral;

V2OptionsBlock:
    'options' block=V2DictLiteral;

V2InnerBlock:
    {infer V2InnerBlock} 'composite' '{' decls+=V2NodeDecl* '}';

// --- wires and paths --------------------------------------------------------------------------------------

V2WireBlock:
    {infer V2WireBlock} '{' (wires+=V2Wire (',' wires+=V2Wire)* ','?)? '}';

V2Wire:
    port=V2Key ('->' path=V2Path | block=V2WireBlock);

// `../fields.acetate[0][1]`: `..` segments are followed by `/`, keys are joined by `.`, indices attach as `[i]`
V2Path:
    segments+=V2Segment (('.' | '/') segments+=V2Segment | segments+=V2Index)*;

V2Segment:
    {infer V2Segment} (key=V2Key | up?='..' | star?='*');

V2Index:
    '[' index=INT ']';

// --- values -----------------------------------------------------------------------------------------------

V2Value:
    V2IntLiteral | V2FloatLiteral | V2StringLiteral | V2BoolLiteral | V2NullLiteral | V2ParamRef
    | V2SiteValue | V2DictLiteral | V2ListLiteral | V2TupleLiteral | V2ArrayLiteral | V2FileLiteral | V2ModelRef;

V2IntLiteral:
    value=INT;

V2FloatLiteral:
    value=FLOAT;

V2StringLiteral:
    value=STRING;

V2BoolLiteral:
    value=('true' | 'false');

V2NullLiteral:
    {infer V2NullLiteral} 'null';

V2ParamRef:
    value=PARAM;

V2SiteValue:
    {infer V2SiteValue} '?' ('(' default=V2Value ')')? ('as' sort=V2TypeExpr)?;

V2DictLiteral:
    {infer V2DictLiteral} '{' (entries+=V2Entry (',' entries+=V2Entry)* ','?)? '}';

V2Entry:
    key=V2Key '=' value=V2Value;

V2ListLiteral:
    {infer V2ListLiteral} '[' (items+=V2Value (',' items+=V2Value)* ','?)? ']';

V2TupleLiteral:
    {infer V2TupleLiteral} '(' (items+=V2Value (',' items+=V2Value)* ','?)? ')';

V2ArrayLiteral:
    'array' '(' data=V2ArrayData (',' options+=V2Entry)* ')';

V2ArrayData:
    V2ListLiteral | V2FileLiteral;

V2FileLiteral:
    'file' '(' path=STRING ')';

// a model site filled by a model header: `store m : ODEModel = Caravagna2010;`
V2ModelRef:
    model=[V2ModelDecl:ID];

// --- types ------------------------------------------------------------------------------------------------

V2TypeExpr:
    options+=V2PrimaryType ('|' options+=V2PrimaryType)*;

V2PrimaryType:
    V2NamedType | V2LinkType | V2StructType | V2RawType;

// `float{0.5}`: bigraph-schema's default-in-type form, kept so that schemas carrying defaults round-trip
V2NamedType:
    name=V2TypeName ('<' args+=V2TypeArg (',' args+=V2TypeArg)* '>')?
    ('[' dims+=V2Dim (',' dims+=V2Dim)* ']')? ('@' units=STRING)? ('{' default=V2Value '}')?;

V2TypeArg:
    {infer V2TypeArg} (type=V2TypeExpr | int=INT | float=FLOAT);

V2Dim:
    {infer V2Dim} (size=INT | name=ID);

V2LinkType:
    'link' '<' inputs=V2StructType ',' outputs=V2StructType '>';

V2StructType:
    {infer V2StructType} '{' fields+=V2Field* '}';

V2RawType:
    raw=STRING;

// keywords are allowed as type names and as keys (`every = 1`, `process = {…}` are real config keys)
V2TypeName returns string:
    ID | V2Keyword;

V2Key returns string:
    ID | STRING | V2Keyword;

V2Keyword returns string:
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
