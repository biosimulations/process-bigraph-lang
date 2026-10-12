# v2 language design

Status: design, 2026-10-11. Validated by the round-trip prototype described in the [plan](plan.md). The background
is in the [research notes](research.md); the tooling around the language is in
[registry and authoring](registry-and-authoring.md).

## 0. Framing

`.pblang` v2 is a tree-shaped, verifiable projection of a process-bigraph composite. Three artifacts share one abstract
model:

| Artifact                                                    | Role                                            | Produced by                                                  |
| ----------------------------------------------------------- | ----------------------------------------------- | ------------------------------------------------------------ |
| `*.pblang` composite                                        | reviewable, checkable, canonical text           | prompt-guided tools or humans; or decompiled from a document |
| `*.pblang` interface file                                   | generated `.d.ts`-like declarations per package | `pblang describe` at release time; hand-editable             |
| `{"schema","state"}` document, template, `*.composite.yaml` | what process-bigraph and the workbench run      | `pblang compile`                                             |

Decisions behind this design:

1. The syntax is **tree-shaped and mirrors the document**: nodes nest like the state tree, edges are declared in place,
   wires use `->` relative to the edge's parent, `..` goes up.
2. The DSL is a **verifiable target layer**, not the only thing an author writes. Diagnostics must be precise and
   located, the text must be readable for review, and printing must be canonical so generated text is deterministic.
3. Interfaces come from **generated interface files** imported like TypeScript `.d.ts` files.
4. The DSL interoperates **both ways** with CompositeSpec `*.composite.yaml`; `param` ↔ CompositeSpec parameter ↔
   value site with a default.

Non-goals: Python builder logic (engine choice, random placement, probe runs) stays in Python. The DSL captures the
result as a ground or template document plus `param`s for the knobs.

## 1. Semantic model

### 1.1 Abstract document

```text
Module    := { name?, docs, imports[], params[], types[], lets[], root: Composite, emitters[], options, meta }
Composite := { nodes: {key -> Node}, options?, bridge?, interface? }
Node      := Store | Subtree | Edge | Replicate
Store     := { type?: TypeExpr, value?: Value | Site, docs }
Subtree   := { type?: TypeExpr, nodes: {key -> Node}, docs }                     // `node x { … }`
Edge      := { kind: process|step|composite|shared|shared_ref, iface?: Ref<Interface>,
               address?: Address | Site(face), config: Value, inputs: Wires, outputs: Wires,
               interval?: Expr, priority?: int, triggers?: [Path], port_overrides?: {inputs, outputs},
               inner?: Composite, bridge?: {inputs, outputs, conduits}, process_id?, extra: {}, docs }
Wires     := {port -> Path | Wires}           Path := [Key | ".." | "*" | Index]
Site      := { sort: TypeExpr | Face | Ref<Interface> | NamedSort, default?: Value }
Replicate := { count: Expr, region: Subtree }                                     // _control: replicate
Param     := { name, type, default?, required, choices?, docs }
Interface := { kind: process|step|adapter|composite, name, address?, config: {key -> {type, default?, docs}},
               inputs: Face, outputs: Face, docs, contract?: {units, min, max, assumptions, refs} }
Face      := { ports: {name -> {type, units?, docs}}, conditional: [{when, ports}], open: bool, delegate?: ConfigKey }
Emitter   := { address, paths: [Path], config }
Options   := { global_time_precision, run_steps_on_init, parallel_*, skip_process_state, contract_strict }
```

### 1.2 Denotation

- `Store` → `schema[path] = type`, `state[path] = value`. A site value emits **state only** (no schema entry;
  process-bigraph#213).
- `Subtree` → a dict in both halves.
- `Edge` → the state node `{_type, address, config, inputs, outputs, interval?, priority?, _triggers?, _inputs?,
_outputs?, …extra}`; the schema half gets `{"_type": kind}` only when there are no port overrides. A composite edge
  → `address: "local:Composite"`, `config: {schema, state, bridge, interface?, options…}`.
- `Site` by position: value site (store value, config value, param), address site (`address` of an edge, sorted by the
  interface face), model site (a `node` whose sort is a face), named sort, replicate region.
- `Param p` has two projections: template mode → a site with `_default` at the referenced position; spec mode →
  `"${p}"` at every reference plus `parameters: {p: {type, default, choices, description}}`.
- `Emitter` → CompositeSpec `emitters:` or the step node that `process_bigraph.emitter.emitter_node_from_declaration`
  builds.
- `Options` → top-level document keys, or keys of a nested composite's `config`.

Deliberately not modelled (stripped by normalization, never printed): `instance`, `_contract`, the injected
`global_time`, emitter `results` stores, serialized dict-form addresses, the legacy `composition` key, run-specific
emitter config injected by the workbench, CompositeSpec `id`.

### 1.3 Round-trip equivalence

```python
def normalize(doc, core):
    schema = core.render(core.access(doc.get("schema", {})), defaults=True)
    state = strip(doc["state"])
    # strip: drop runtime keys; address dict -> "proto:data"; wire str -> [str]; tuples/numpy -> lists;
    #        int -> float where the schema says float; sort edge keys;
    #        drop config keys equal to the class default (only when the core resolves the address);
    #        drop _inputs/_outputs equal to interface() of the resolved class
    return {"schema": schema, "state": state, "options": {k: doc[k] for k in OPTION_KEYS if k in doc}}

equivalent(a, b) := normalize(a) == normalize(b)
```

Three levels, all in the test suite: (1) textual fixpoint, `format(parse(text)) == text` once a parser exists;
(2) semantic, `equivalent(compile(decompile(doc)), doc)` for every fixture; (3) spec, the yaml round-trip equals the
original after key sorting, `requires` recomputed and `id` dropped. Nested composites compare recursively on
`config.state` and `config.schema` using authored documents (saved ones are lossy upstream).

## 2. Syntax

### 2.1 Lexical

v1 terminals are kept: `ID`, `INT` with a leading `-`, `FLOAT` needs a `.`, strings in either quote style, `//` and
`/* */` comments. New: `///` doc comments attach to the next declaration; `${name}` in a string is parameter
interpolation.

Keywords: `module import as param type struct interface process step adapter composite shared node store let emit
options meta every priority at with bridge conduits config inputs outputs ports extra triggers replicate when else of
file load true false`.

### 2.2 Grammar sketch

The executable form of the subset the prototype prints is the Lark grammar in `process_bigraph_lang/v2/parser.py`,
verified against every snapshot in `tests/fixtures/data/v2/snapshots/`. The sketch below is the full target.

```text
Module:        ('module' QualifiedName ';')? TopLevel*;
TopLevel:      Import | Param | TypeDecl | Let | InterfaceDecl | RootComposite | Emit | Options | Meta;
Import:        'import' (QualifiedName ('.' '{' ID (',' ID)* '}')? | STRING ('as' ID)?) ';';
Param:         DOC* 'param' ID ':' TypeExpr ('=' (Value | '?'))? ('choices' '[' Value (',' Value)* ']')? ';';
TypeDecl:      DOC* ('type' ID '=' TypeExpr ';' | 'struct' ID '{' Field* '}');
Field:         DOC* ID ':' TypeExpr ('=' Value)? ';';

TypeExpr:      PrimaryType ('|' PrimaryType)*;                     // union (bigraph `~`)
PrimaryType:   NamedType | GenericType | ArrayType | StructType | LinkType | RawType;
GenericType:   ID '<' TypeArg (',' TypeArg)* '>';                  // map<K,V> list<T> maybe<T> overwrite<T> const<T>
                                                                   // set<T> tree<T> tuple<A,B> range<lo,hi>
                                                                   // enum<a,b,c> object<"pkg.Cls">
ArrayType:     'array' '<' TypeExpr '>' ('[' ShapeDim (',' ShapeDim)* ']')? ('@' STRING)?;   // ShapeDim: INT | '_' | param
StructType:    '{' Field* '}';                                     // anonymous struct = bigraph merge a:T|b:U
LinkType:      'link' '<' '{' Field* '}' ',' '{' Field* '}' '>';
RawType:       STRING;                                             // any bigraph-schema expression verbatim

Let:           DOC* 'let' ID (':' TypeExpr)? '=' Value ';';

InterfaceDecl: DOC* ('process'|'step'|'adapter'|'composite') ID ('at' STRING)? '{'
                 ('config' '{' Field* '}')? ('inputs' FaceBody)? ('outputs' FaceBody)? ('contract' '{' … '}')? '}';
FaceBody:      '{' (PortDecl | CondPorts | '...')* '}' | 'of' 'config' '.' ID ';';   // '...' open face; 'of' delegated
PortDecl:      DOC* ID ':' TypeExpr ('@' STRING)? ';';
CondPorts:     'when' Predicate '{' PortDecl* '}' ('else' '{' PortDecl* '}')?;      // Predicate: config path ('==' Value)?

RootComposite: DOC* 'composite' ID? '{' NodeDecl* '}';
NodeDecl:      StoreDecl | SubtreeDecl | EdgeDecl | ReplicateDecl;
StoreDecl:     DOC* 'store' Key (':' TypeExpr)? ('=' Value)? ';';
SubtreeDecl:   DOC* 'node' Key (':' TypeExpr)? ('=' SiteValue ';' | '{' NodeDecl* '}');
ReplicateDecl: 'replicate' Expr SubtreeDecl;
EdgeDecl:      DOC* ('process'|'step') Key ':' EdgeHead ('every' Expr)? ('priority' INT)? '{' EdgeItem* '}'
             | DOC* 'composite' Key ('every' Expr)? ('at' STRING)? '{' CompositeItem* '}'
             | DOC* 'shared' 'process' Key ':' EdgeHead '{' ('config' ConfigBlock)? '}';
EdgeHead:      [InterfaceDecl] ('at' (STRING | '?' ('(' STRING ')')?))? | 'at' STRING | 'shared' [EdgeDecl];
EdgeItem:      'config' ConfigBlock | 'inputs' WireBlock | 'outputs' WireBlock
             | 'ports' '{' ('inputs' '{' PortDecl* '}')? ('outputs' '{' PortDecl* '}')? '}'
             | 'triggers' '[' Path (',' Path)* ']' | 'extra' '{' KeyValue* '}';
CompositeItem: EdgeItem | 'bridge' '{' ('inputs' WireBlock)? ('outputs' WireBlock)? ('conduits' WireBlock)? '}'
             | 'interface' '{' ('outputs' '{' PortDecl* '}')? '}' | Options | NodeDecl;
ConfigBlock:   '{' (KeyValue (',' KeyValue)* ','?)? '}' | '=' [Let];
WireBlock:     '{' (Wire (',' Wire)* ','?)? '}';     Wire: Key ('->' Path | WireBlock);   // nested = sub-ports
Path:          Seg ('.' Seg)*;     Seg: ID | STRING | '..' | '*' | '[' INT ']';           // fields.A[0][1]

Value:         Literal | Ref | SiteValue | StructLit | MapLit | ListLit | TupleLit | EdgeLit | FileRef | Interp;
SiteValue:     '?' ('(' Value ')')? ('as' (TypeExpr | NamedSort))?;
EdgeLit:       [InterfaceDecl] '{' KeyValue* '}';                  // {address, config} child for higher-order nodes
FileRef:       'file' '(' STRING ')' | 'load' '(' STRING ')';      // text / json|npy|npz|csv; inlined at compile
Expr:          Value | Expr ('*'|'/'|'+'|'-') Expr;                // only in every / replicate / shapes / config leaves
Emit:          'emit' (ID | STRING) '{' Path (',' Path)* '}' ('with' ConfigBlock)? ';';
Options:       'options' '{' KeyValue* '}';     Meta: 'meta' '{' KeyValue* '}';     Key: ID | STRING;
```

### 2.3 Rules

- **Wire paths are relative to the edge's parent**, exactly like the document. The printer uses `.` and quotes
  non-identifier keys (`node "[0,1]"`).
- **One `Site` type; position decides the kind.** `= ?`, `= ?(v)`, `= ? as positive` (value); `at ?`,
  `at ?("local:FV")` (address, sorted by the interface face); `node model : Engine = ?;` (model site). An edge whose
  interface has no `at` **must** be written `at ?`, so openness is visible in review.
- **Literals keep the v1 rules**: bare keys make a struct, literal keys make a map, `{}` is either; `-` is allowed in
  numbers; floats need a `.`.
- **Type spelling**: `int`, `bool`, `float`, `string`, `map<string, V>`, `list<T>`, `maybe<T>`, `overwrite<T>`,
  `enum<a, b>`, `array<float>[3,3] @ "uM"`, `{ a: T; b: U }`, `A | B`, raw `"…"`. The compiler maps `int` →
  `integer`, `bool` → `boolean`, `map<string, V>` → `map[V]`. An unknown type name is an error, never passed
  through.
- **`file()` / `load()`**: compile inlines the content so the document stays self-contained. The decompiler
  externalizes strings longer than 2000 characters and arrays with more than 64 elements into sidecar files named
  `<composite>.<path>.{txt,json,npy}`.
- **`let`**: module constants inlined at compile. The decompiler hoists subtrees that appear verbatim at two or more
  places and exceed about ten leaves (a shared `grid` config, for example), named after the config key.
- **`every` and `replicate` accept expressions** (`every k * dt`). The spec projection cannot represent arithmetic.
- **Doc comments**: `///` on `composite` → spec `description`; on `param` → parameter `description`; on interface
  ports → contract description; on stores and edges → text and `pblang doc` only (never emitted as document keys).
- **`emit` aliases**: `parquet`, `ram`, `sqlite`, `xarray`, `console`, `json` → `local:<X>Emitter`; an unknown alias
  is an error listing the known ones. `emit "local:ParquetEmitter" { … }` gives an address directly.
- **Canonical formatter**: two-space indent; the decompiler orders stores, then nodes, then edges, each
  alphabetically; config entries in interface-declared order, then unknown keys alphabetically; one wire per line when
  more than two; strings double-quoted.

### 2.4 Interface files

Generated once per package (`<pkg>/pblang/interfaces.pblang`), hand-editable for ports the generator cannot see.
`describe` emits what `config_schema` and `interface()` report, adds `...` and a `// TODO: dynamic` comment on any face
whose `inputs()`/`outputs()` body references `self.config`, and `describe --check` verifies that a hand-edited file is a
superset of the generated one.

```text
module viva_smoldyn;

struct Species { difc: float; count: int = 0; color: string = "black"; display_size: float = 1.0; }

/// Smoldyn particle simulation in a box.
process SmoldynProcess at "local:!viva_smoldyn.processes.SmoldynProcess" {
  config {
    dimensions: int = 3;
    bounds: list<list<float>>;
    boundary_type: string = "r";
    dt: float = 0.01;
    seed: maybe<int>;
    species: map<string, Species>;
    reactions: list<map<string, "any">>;     // raw type kept verbatim: describe found "map"
  }
  inputs { }
  outputs {
    molecule_counts: map<string, int>;
    molecule_positions: list<"any">;
    time: float @ "s";
  }
}
```

Dynamic ports, written honestly:

```text
module viva_pde_particle;

process SmoldynHybrid at "local:!viva_pde_particle.processes.smoldyn_hybrid.SmoldynHybrid" {
  config { grid: map<string, "any">; config_text: string; particle_species: list<string>;
           field_species: list<string> = []; dt: float = 0.01; step_multiplier: int = 1;
           quiet: bool = true; emit_positions: bool = false; }
  inputs  { fields: map<string, array<float>> @ "uM"; }
  outputs {
    particle_counts: map<string, overwrite<array<float>>>;
    particle_totals: map<string, overwrite<float>>;
    when emit_positions { particle_positions: map<string, overwrite<array<float>>>; }
  }
}

process SpatialRecorder at "local:!viva_pde_particle.processes.recorder.SpatialRecorder" {
  config { out_dir: string; base_dt: float; every: int; layout: map<string, "any">; species: list<string>;
           particle_species: list<string> = []; membranes: map<string, "any"> = {}; region: string = "cell"; }
  inputs {
    when layout.kind == "mesh" { field_dofs: map<string, array<float>>; } else { fields: map<string, array<float>>; }
    when particle_species { particle_positions: map<string, array<float>>; }
    ...                                   // open face: undeclared ports warn, not error
  }
  outputs { }
}

/// Runs a child process on a sub-multiple of the base tick.
process Stepper at "local:!viva_pde_particle.processes.stepper.Stepper" {
  config { process: edge; dt: float; every: int = 1; phase: int = 0; }   // `edge` = an {address, config} child
  inputs  of config.process;
  outputs of config.process;
}

adapter GridCountsToConcentration at "local:!viva_pde_particle.steps.transfer.GridCountsToConcentration" {
  config  { grid: map<string, "any">; species: list<string>; staircase: map<string, "any"> = {}; }
  inputs  { particle_counts: map<string, array<float>> @ "count"; }
  outputs { particle_conc:   map<string, overwrite<array<float>>> @ "uM"; }
}
```

`adapter` is `step` plus role metadata; the checker uses it for unit-mismatch fix hints. The DSL-only `edge` type is an
`{address, config}` child spec; in config position it is written as an edge literal (`SmoldynHybrid { … }`).

## 3. Mapping tables

### 3.1 DSL → document

| DSL                                                          | `schema` half                           | `state` half                                                                                                                                     |
| ------------------------------------------------------------ | --------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| `store t: float = 0.0;`                                      | `"t": "float"`                          | `"t": 0.0`                                                                                                                                       |
| `store counts: map<string, int>;`                            | `"counts": "map[integer]"`              | absent (process-bigraph fills from schema)                                                                                                       |
| `store m: float = ?(1.0);`                                   | none (#213)                             | `{"_type":"site","_sort":"float","_default":1.0}`                                                                                                |
| `store x: float = ? as positive;`                            | none                                    | `{"_type":"site","_sort":"positive"}`                                                                                                            |
| `node cell { … }`                                            | `"cell": {children}`                    | `"cell": {children}`                                                                                                                             |
| `node model : Engine = ?;`                                   | none                                    | `{"_type":"site","_sort":{"_type":"link","_inputs":…,"_outputs":…}}`                                                                             |
| `replicate n node cell {…}`                                  | children                                | `{"_control":"replicate","_count":n, …}` (assembly.build only)                                                                                   |
| `process p : I every 0.5 { config{…} inputs{…} outputs{…} }` | `"p": {"_type":"process"}`              | `{"_type":"process","address":I.address,"config":…,"inputs":…,"outputs":…,"interval":0.5}`                                                       |
| `… ports { inputs { a: T } }`                                | `{"_type":"process","_inputs":{"a":T}}` | also `"_inputs": {"a": T}`                                                                                                                       |
| `step s : I priority 2 { triggers [a.b] }`                   | `{"_type":"step"}`                      | `{"_type":"step", …, "priority":2, "_triggers":[["a","b"]]}`                                                                                     |
| `process p : I at ? { … }`                                   | `{"_type":"process"}`                   | `"address": {"_type":"site","_sort":{"_type":"link",…}}`                                                                                         |
| `process p : I at ?("local:FV")`                             | same                                    | `_sort` + `"_default":"local:FV"`                                                                                                                |
| `process p at "local:X" { ports{…} }`                        | `_inputs`/`_outputs`                    | address literal; `_inputs`/`_outputs`                                                                                                            |
| `composite c every 1.0 { body bridge{…} interface{…} }`      | `"c": {"_type":"process"}`              | `{"_type":"process","address":"local:Composite","interval":1.0,"config":{"schema":…,"state":…,"bridge":…,"interface":…},"inputs":…,"outputs":…}` |
| `shared process e : I { config {…} }`                        | —                                       | `{"_type":"shared_process","address":…,"config":…}`                                                                                              |
| `process a : shared e { inputs{…} }`                         | —                                       | `{"_type":"shared_process_ref","process_id":"e","inputs":…}`                                                                                     |
| `inputs { a -> fields.A[0][1], b -> ../x, sub { p -> q } }`  | —                                       | `{"a":["fields","A",0,1],"b":["..","x"],"sub":{"p":["q"]}}`                                                                                      |
| `extra { note = "…" }`                                       | —                                       | extra keys verbatim                                                                                                                              |
| `emit parquet { counts, cell.mass } with { out_dir = "o" }`  | —                                       | step from `emitter_node_from_declaration({"address":"local:ParquetEmitter","paths":["counts","cell/mass"],"config":{"out_dir":"o"}})`            |
| `options { global_time_precision = 6 }`                      | top-level document key                  | —                                                                                                                                                |
| `param dt: float = 0.01;` + `every dt` (template mode)       | —                                       | `"interval": {"_type":"site","_sort":"float","_default":0.01}`                                                                                   |
| `param n: int = ?;` (template mode)                          | —                                       | site without `_default` (required)                                                                                                               |
| `file("m.txt")` / `load("a.npy")`                            | —                                       | inlined string / list                                                                                                                            |

Type expressions: `int` → `integer`, `bool` → `boolean`, `list<T>` → `list[T]`, `map<string,V>` → `map[V]`,
`map<K,V>` → `map[K,V]`, `maybe<T>` → `maybe[T]`, `overwrite<T>` → `overwrite[T]`, `enum<a,b>` → `enum[a,b]`,
`range<0.0,1.0>` → `range[0.0,1.0]`, `array<float>[3,3] @ "uM"` → `{"_type":"array","_shape":[3,3],"_data":"float","_units":"uM"}`
(dict form when shape or units are present, else `array[float]`), `{a: T; b: U}` → `a:T|b:U` (dict form when a member
is a struct with defaults), `A | B` → `A~B`, `link<{…},{…}>` → `{"_type":"link","_inputs":…,"_outputs":…}`, `"raw"` →
verbatim. A field default → `{"_type":T,"_default":v}`.

### 3.2 DSL → CompositeSpec yaml

| DSL                                                   | yaml                                                                                    |
| ----------------------------------------------------- | --------------------------------------------------------------------------------------- |
| `module x;` / `composite Name {…}`                    | `name: Name` (fallback: file stem)                                                      |
| `/// text` on `composite`                             | `description: "text"`                                                                   |
| `meta { tags = […], default_n_steps = 100, … }`       | the same keys                                                                           |
| `param dt: float = 0.01 choices [0.01, 0.1];` + `///` | `parameters: {dt: {type: float, default: 0.01, choices: […], description: …}}`          |
| `param n: int = ?;`                                   | `parameters: {n: {type: integer}}` (no default; `to_document` raises if not overridden) |
| `every dt`, `config { dt = dt }`, `"out_${run}"`      | `interval: "${dt}"`, `dt: "${dt}"`, `"out_${run}"`                                      |
| `import viva_smoldyn.{SmoldynProcess}` + uses         | `requires: {processes: [SmoldynProcess]}` (computed; `meta { requires = … }` overrides) |
| `emit …`                                              | `emitters: [{address, paths, config?}]`                                                 |
| `options { global_time_precision = 6 }`               | `global_time_precision: 6`                                                              |
| composite body                                        | `state:` (+ `schema:` only for typed stores process-bigraph could not infer)            |
| sites other than params                               | not representable → `E-SPEC-UNREPRESENTABLE`                                            |
| param types beyond float/int/string/bool/list/map     | `enum<…>` becomes `string` + `choices`; others → `E-SPEC-PARAM-TYPE`                    |

### 3.3 Document → DSL (decompilation)

| Document                                                    | DSL                                                                                                                                                                                              |
| ----------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| dict containing an edge (directly or below)                 | `node key { … }`                                                                                                                                                                                 |
| dict with no edges                                          | `store key: T = {…};` (`T` from schema if present, else inferred)                                                                                                                                |
| leaf value, schema present                                  | `store key: T = v;`                                                                                                                                                                              |
| leaf value, no schema                                       | `store key: <inferred> = v;` (type printed for review)                                                                                                                                           |
| schema entry without state                                  | `store key: T;`                                                                                                                                                                                  |
| `{"_type":"site",…}`                                        | `= ?(default)` / `= ? as Sort`; in `address` → `at ?`; face sort → `node x : <interface or link<>> = ?`                                                                                          |
| `"local:Name"` / `"local:!pkg.mod.Class"`                   | resolved against interface files on the search path → `import pkg.{Name}` + `process key : Name`; unresolved → `process key at "…" { ports { … from _inputs/_outputs } }` + `W-IFACE-UNRESOLVED` |
| `{"protocol","data"}`                                       | `"protocol:data"`                                                                                                                                                                                |
| `config`                                                    | keys equal to the interface default dropped; unknown keys kept with `W-CONFIG-UNKNOWN-KEY`                                                                                                       |
| `_inputs`/`_outputs` equal to the interface face            | omitted; otherwise `ports { }`                                                                                                                                                                   |
| `interval` 1.0 on a process                                 | omitted (default)                                                                                                                                                                                |
| `address: "local:Composite"`                                | `composite key every I { … bridge … }`                                                                                                                                                           |
| emitter step equal to `emitter_node_from_declaration(decl)` | `emit alias { paths } with {config}`; otherwise a plain `step`                                                                                                                                   |
| `global_time`, `results`, `instance`, `_contract`           | dropped                                                                                                                                                                                          |
| template sites with `_default` at `interval`/config leaves  | `param <key>: T = default;` + a reference (bare key when unique, else path-joined)                                                                                                               |
| yaml `parameters` + `${p}`                                  | `param p …` + references; `${p}` inside strings kept as interpolation                                                                                                                            |
| yaml `description`, `tags`, …                               | `///` and `meta {}`                                                                                                                                                                              |
| large strings and arrays                                    | `file()` / `load()` sidecars                                                                                                                                                                     |

## 4. Worked examples

### 4.1 viva-smoldyn reversible dimerization (from `reversible-dimerization.composite.yaml`)

```text
module viva_smoldyn.composites.reversible_dimerization;
import viva_smoldyn.{SmoldynProcess};

meta { tags = ["particles", "reaction-diffusion", "3d", "simularium"] }

/// Smoldyn 3D reversible dimerization: fast red monomers A diffuse and bind pairwise into
/// slower blue dimers B (A + A <-> B) in a reflecting cubic box. Emits per-species counts,
/// per-molecule positions, and time each step; the positions drive a Simularium trajectory.
composite reversible_dimerization {
  store molecule_counts: map<string, int> = {};
  store molecule_positions: list<"any"> = [];
  store time: float = 0.0;

  process smoldyn : SmoldynProcess every 0.5 {
    config {
      dimensions = 3,
      bounds = [[0, 50], [0, 50], [0, 50]],
      boundary_type = "r",
      dt = 0.01,
      seed = 12345,
      species = {
        "A" = { difc = 3.0, count = 250, color = "red",  display_size = 1.2 },
        "B" = { difc = 1.0, count = 0,   color = "blue", display_size = 2.0 }
      },
      reactions = [ { "name" = "dimerize", "subs" = ["A", "A"], "prds" = ["B"], "rate" = 2.0, "kb" = 0.15 } ]
    }
    inputs  { }
    outputs { molecule_counts -> molecule_counts, molecule_positions -> molecule_positions, time -> time }
  }
}

emit parquet { molecule_counts, molecule_positions, time };
```

`pblang compile --to yaml` reproduces the yaml (`requires` computed from the import, `name` from the composite);
`pblang compile` produces the document with the emitter step materialized. From the yaml alone the stores are untyped
(`molecule_counts: {}`); the checker reports `W-STORE-UNTYPED` with the fix "declare `: map<string, int>` (from
`SmoldynProcess.outputs.molecule_counts`)". That review signal is exactly what the DSL is for.

### 4.2 Nested growth-division composite (`local:Composite` with a bridge)

```text
import demo.{Grow, Divide};

param growth_rate: float = 0.1;

composite grow_divide {
  store environment: map<string, float> = { "nutrient" = 10.0 };
  store mass_out: float = 0.0;

  /// One cell as a nested composite; the bridge exposes its mass and a division signal.
  composite cell every 1.0 {
    store mass: float = 1.0;
    store divide_signal: bool = false;
    process grow : Grow every 1.0 {
      config  { rate = growth_rate }
      inputs  { mass -> mass, env -> ../environment }   // `..` escapes the inner root through the bridge
      outputs { mass -> mass }
    }
    step divide : Divide {
      config  { threshold = 2.0 }
      inputs  { mass -> mass }
      outputs { divide -> divide_signal }
    }

    bridge {
      inputs   { environment -> environment }           // inner path for the outer `environment` port
      outputs  { mass -> mass }
      conduits { divide -> divide_signal }
    }
    interface { outputs { mass: float; } }
    options { run_steps_on_init = true }

    inputs  { environment -> environment }              // outer wires, relative to the root
    outputs { mass -> mass_out }
  }
}
```

Compiles to `cell: {_type: process, address: "local:Composite", interval: 1.0, config: {schema, state, bridge: {inputs:
{environment: ["environment"]}, outputs: {mass: ["mass"]}, conduits: {divide: ["divide_signal"]}}, interface: {outputs:
{mass: "float"}}, run_steps_on_init: true}, inputs, outputs}`. Decompiling a _saved_ document whose nested
`config.state` is empty raises `W-NESTED-SAVE-LOSSY`.

### 4.3 viva-pde-particle hybrid (FV PDE + Smoldyn + adapters + Stepper + SpatialRecorder)

```text
module viva_pde_particle.composites.hybrid;
import viva_pde_particle.{FVReactionDiffusion, SmoldynHybrid, GridCountsToConcentration,
                          ExtendGridField, Stepper, SpatialRecorder};

param dt: float = 0.01;
param step_multiplier: int = 5;
/// Which PDE engine fills the `pde` slot; the face is shared by FV and FEniCSx.
param pde_engine: string = "fv" choices ["fv", "fenicsx"];

let grid = { "origin" = [0.0, 0.0, 0.0], "size" = [10.0, 10.0, 10.0], "num" = [20, 20, 20] };
let species = ["A", "B"];

composite hybrid {
  store fields:          map<string, array<float>[20,20,20] @ "uM">    = load("hybrid.fields.npz");
  store particle_counts: map<string, array<float>[20,20,20] @ "count"> = load("hybrid.particle_counts.npz");
  store particle_conc:   map<string, array<float>[20,20,20] @ "uM">    = load("hybrid.particle_conc.npz");
  store particle_totals: map<string, float> = { "A" = 1200.0, "B" = 0.0 };
  store fields_ext:      map<string, array<float>>;

  /// Filled by the builder with the engine chosen by `pde_engine`; both engines satisfy this face.
  process pde : FVReactionDiffusion at ?("local:FVReactionDiffusion") every dt {
    config  { grid = grid, pde = load("hybrid.pde.json"), dt = dt,
              domain = { "mask" = ?, "volume_fraction" = ? } }    // builder-computed arrays left open
    inputs  { fields -> fields, external_conc -> particle_conc }
    outputs { fields -> fields }
  }

  step particle_to_field : GridCountsToConcentration {
    config  { grid = grid, species = species }
    inputs  { particle_counts -> particle_counts }
    outputs { particle_conc -> particle_conc }
  }

  step extend_field : ExtendGridField {
    config  { grid = grid, species = species, staircase = {} }
    inputs  { fields -> fields }
    outputs { fields_ext -> fields_ext }
  }

  /// SmoldynHybrid driven on a sub-multiple of dt, phase k-1 (vcell-fvsolver coupling).
  process particles : Stepper every dt {
    config {
      process = SmoldynHybrid {                                  // edge literal: {address, config}
        grid = grid, config_text = file("hybrid.particles.smol"),
        particle_species = species, field_species = ["A"],
        dt = dt, step_multiplier = step_multiplier
      },
      dt = dt, every = step_multiplier, phase = step_multiplier - 1
    }
    inputs  { fields -> fields }                                 // face delegated from config.process
    outputs { particle_counts -> particle_counts, particle_totals -> particle_totals }
  }

  process recorder : SpatialRecorder every dt {
    config  { out_dir = "${out_dir}", base_dt = dt, every = 10,
              layout = { "kind" = "grid", "grid" = grid }, species = species }
    inputs  { fields -> fields }                                 // ok: `when layout.kind == "mesh"` is false
  }
}
```

`load()` and `file()` keep the text reviewable while the document stays self-contained; the `?` inside `domain` are
config sites the builder fills with `fill_sites`; the `Stepper` child is an edge literal, which the checker uses to
resolve the delegated face and to type-check the child's config; `pde_engine` is a plain spec parameter (the mapping to
an address stays in the builder; the DSL records the open address site with its default). `phase = step_multiplier - 1`
is an expression: the spec projection reports `E-SPEC-EXPR`, the template projection evaluates it from the defaults with
`W-PARAM-EVALUATED`.

### 4.4 spatio-flux cell `"[0,1]"` with array-indexed wires

```text
import spatio_flux.{DynamicFBA};
import spatio_flux.types;                 // registers positive_float etc. (register_types hook)

param n_bins: int = 2;

composite spatial_dfba {
  store fields: map<string, array<float>[n_bins, n_bins] @ "mM"> = {
    "glucose" = [[10.0, 10.0], [10.0, 10.0]], "acetate" = [[0.0, 0.0], [0.0, 0.0]], "biomass" = [[0.1, 0.1], [0.1, 0.1]]
  };

  node "[0,1]" {
    process dfba : DynamicFBA every 1.0 {
      config { model_file = "textbook", biomass_identifier = "biomass",
               kinetic_params = { "glucose" = [0.5, 1.0], "acetate" = [0.5, 2.0] },
               substrate_update_reactions = { "glucose" = "EX_glc__D_e", "acetate" = "EX_ac_e" },
               bounds = { "EX_o2_e" = { "lower" = -2.0, "upper" = ? as maybe<float> },
                          "ATPM" = { "lower" = 1.0, "upper" = 1.0 } } }
      inputs  { substrates { glucose -> ../fields.glucose[0][1], acetate -> ../fields.acetate[0][1],
                             biomass -> ../fields.biomass[0][1] } }
      outputs { substrates { glucose -> ../fields.glucose[0][1], acetate -> ../fields.acetate[0][1],
                             biomass -> ../fields.biomass[0][1] } }
    }
  }
}
```

`../fields.glucose[0][1]` → `["..","fields","glucose",0,1]`. The checker resolves the path type through `map` →
`array` → index → index and checks it against the port type with `core.resolve_schemas`. `n_bins` in a shape is a
param, so the shape is `[2,2]` in both projections (shapes must be ground at compile time).

### 4.5 Template with a face site for the engine and a required param

```text
import viva_pde_particle.{PdeEngine};    // an interface: a process declaration with no `at`

param n_particles: int = ?;              // required: fill_sites must supply it
param dt: float = 0.01;

composite pde_study {
  store fields: map<string, array<float>> = {};
  node model : PdeEngine = ?;            // model site: a whole subtree admitted by the PdeEngine face
  process engine : PdeEngine at ? every dt {   // address site sorted by the face
    config  { n = n_particles }
    inputs  { fields -> fields }
    outputs { fields -> fields }
  }
}
```

Compiles in template mode to sites at `engine/address` (sorted by the link face), `engine/config/n` (required),
`interval` (default 0.01) and `model`. `pblang check` reports groundness with process-bigraph's own wording:
`required site(s) left unfilled: 'engine/config/n', 'engine/address', 'model'`.

## 5. Diagnostics

### 5.1 Stages

| Stage | Where                                                                            | Needs                                 |
| ----- | -------------------------------------------------------------------------------- | ------------------------------------- |
| S1    | parse (Langium; Lark in the prototype)                                           | text                                  |
| S2    | scope and imports                                                                | interface files                       |
| S3    | static types (Langium validators)                                                | DSL types only                        |
| S4    | schema (`core.access`, `core.check`, `resolve_schemas`)                          | a core with imported `register_types` |
| S5    | face and contract (`admits_why`, `face_conforms`, `find_candidates`, unit scale) | core + interface files                |
| S6    | registry (`link_registry`, `unresolvable_addresses`; optional `--env`)           | the target environment                |
| S7    | groundness (`required_open_sites`)                                               | —                                     |

S1–S3 run in the editor; S4–S7 in `pblang check` and CI. Every diagnostic has a stable code (family prefix plus slug, see
the [registry and authoring design](registry-and-authoring.md#4-validation-and-error-ux)), a range, a document `path`
(slash-joined, as `fill_sites` uses it) and, where possible, an LSP-shaped fix.

### 5.2 Codes

| Code                                                                                    | Severity | Example                                                                                                                |
| --------------------------------------------------------------------------------------- | -------- | ---------------------------------------------------------------------------------------------------------------------- |
| `E-UNKNOWN-PORT`                                                                        | error    | `smoldyn: port 'molecule_count' is not an output of SmoldynProcess (outputs: molecule_counts, …)`                      |
| `E-WIRE-TYPE`                                                                           | error    | `grow.inputs.mass: port type 'float' cannot be resolved with store 'cell.mass' of type 'string'`                       |
| `E-UNKNOWN-TYPE`                                                                        | error    | `type 'any' is not a bigraph-schema type (it would pass through silently); did you mean "any" as a raw type, or node?` |
| `E-CONFIG-TYPE`                                                                         | error    | `smoldyn.config.dimensions: expected integer, got 3.0`                                                                 |
| `E-CONFIG-MISSING`                                                                      | error    | `recorder.config: required key 'out_dir' is missing`                                                                   |
| `E-FACE-NOT-ADMITTED`                                                                   | error    | `pde: address 'local:FenicsxMesh' does not satisfy face PdeEngine: missing input 'external_conc'`                      |
| `E-ADDRESS-UNRESOLVABLE`                                                                | error    | `particles: 'local:SmoldynHybrid' is not registered in this environment (known: …)`                                    |
| `E-NOT-GROUND`                                                                          | error    | `composite document is not ground — required site(s) left unfilled: 'engine/config/n'`                                 |
| `E-PARAM-UNDECLARED`                                                                    | error    | `'${out_dir}' references a parameter that is not declared`                                                             |
| `E-MIXED-APPLY`                                                                         | error    | `store 'fields' receives 'overwrite[array[float]]' from pde and additive 'array[float]' from extend_field`             |
| `E-SPEC-UNREPRESENTABLE`                                                                | error    | `site at 'pde/address' cannot be written as a CompositeSpec; use --template or give it a param`                        |
| `E-PATH-ESCAPES-ROOT`                                                                   | error    | `grow.inputs.env: '../../x' goes above the composite root`                                                             |
| `W-WIRE-UNIT`                                                                           | warning  | `particle_to_field.inputs.particle_counts: 'count' wired to a store in 'uM'` (fix hint lists adapters)                 |
| `W-ADDITIVE-OUTPUT`                                                                     | info     | `particles.outputs.particle_counts: 'map[array[float]]' is additive; wrap in overwrite<> if the port replaces values`  |
| `W-STORE-CREATED-FROM-PORT`                                                             | warning  | `wire 'fields_ext' names no store; it will be created from ExtendGridField.outputs.fields_ext`                         |
| `W-STORE-UNTYPED`                                                                       | warning  | see 4.1                                                                                                                |
| `W-OPEN-FACE-PORT`                                                                      | warning  | `recorder.inputs.extra: not declared by SpatialRecorder, which has an open face ('...')`                               |
| `W-CONFIG-UNKNOWN-KEY`                                                                  | warning  | `smoldyn.config.colour: not in SmoldynProcess.config`                                                                  |
| `W-IFACE-UNRESOLVED`                                                                    | warning  | `'local:Foo' has no interface file; ports taken from _inputs/_outputs`                                                 |
| `W-NESTED-SAVE-LOSSY`                                                                   | warning  | `cell: nested composite has empty config.state (saved documents lose inner state)`                                     |
| `W-PARAM-EVALUATED`                                                                     | warning  | `phase = step_multiplier - 1 evaluated with defaults (4)`                                                              |
| `E-INTERVAL`, `E-DUPLICATE-KEY`, `E-UNRESOLVED-IMPORT`, `E-EMIT-ALIAS`, `E-BRIDGE-PORT` | error    | as named                                                                                                               |

### 5.3 `pblang check`

```text
pblang check <file.pblang>... [--env] [--format json|text] [--spec|--template|--ground]
             [--set name=value]... [--interface-path DIR]... [--strict]
exit 0 = no errors; 1 = errors; 2 = tool failure
```

```json
{
  "version": 1,
  "ok": false,
  "diagnostics": [
    {
      "code": "E-UNKNOWN-PORT",
      "severity": "error",
      "stage": "type",
      "file": "hybrid.pblang",
      "range": {
        "start": { "line": 41, "col": 15 },
        "end": { "line": 41, "col": 30 }
      },
      "path": "particles/outputs/particle_count",
      "message": "...",
      "related": [
        {
          "file": "viva_pde_particle.pblang",
          "line": 88,
          "message": "outputs declared here"
        }
      ],
      "fix": {
        "title": "rename to particle_counts",
        "edits": [{ "range": {}, "newText": "particle_counts" }]
      },
      "docs": "https://…/codes#E-UNKNOWN-PORT"
    }
  ],
  "summary": {
    "errors": 1,
    "warnings": 2,
    "ground": false,
    "open_sites": ["engine/config/n"]
  }
}
```

`fmt`, `compile`, `decompile`, `describe` and `doc` share the same envelope.

## 6. Open questions

1. **Params referenced at several positions in template mode.** Substitute at compile time by default (`--set`);
   emit same-key multi-sites only if `fill_sites` confirms multi-fill (a quick test against
   `process_bigraph/templates.py`).
2. **Expressions.** Allow `+ - * /` on literals and params in `every`, `replicate`, shapes and config leaves; the spec
   projection emits `E-SPEC-EXPR` unless the expression is a bare param; the template projection evaluates with
   defaults.
3. **Union syntax.** `A | B` in the DSL (bigraph `~`); anonymous struct `{a: T; b: U}` for merges; raw strings cover
   the rest.
4. **`node` vs `store` for dicts.** The edges-inside rule is deterministic; `--node-depth N` promotes dicts to `node`
   for readability without changing meaning.
5. **Untyped stores.** `W-STORE-UNTYPED` with an auto-fix; `pblang fmt --infer-types`.
6. **Interface resolution.** `<pkg>/pblang/interfaces.pblang` in the wheel plus an entry point; `PBLANG_PATH`
   overrides; the catalog aggregates by reading wheels, never by importing.
7. **Units `@ "uM"`.** Contract-level metadata (`_units` in the contract and on `array`); `W-WIRE-UNIT` fires only when
   both ends declare units.
8. **Edge literals in config.** Allowed wherever the interface declares an `edge` or `list<edge>` field.
9. **`shared` semantics.** Wires on `shared_process_ref` and where `interval` lives need confirmation against
   `composite.py`.
10. **Doc comments on stores and edges.** Text-only until process-bigraph has a convention for state descriptions.
11. **Prototype parser.** A small Lark grammar in Python gives text-level round trip quickly; the Langium v2 grammar
    remains the long-term single source of truth and binds to the same model.
