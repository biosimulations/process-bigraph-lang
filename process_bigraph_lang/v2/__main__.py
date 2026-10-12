"""
`python -m process_bigraph_lang.v2 compile <file.pbl> [--interfaces m.json]... [--to document|spec] [-o out]`:
parse and check the text, then write the document (JSON) or the CompositeSpec (yaml); errors stop it.
`python -m process_bigraph_lang.v2 decompile <doc.json | spec.composite.yaml>`: a document as `.pbl` text.
`python -m process_bigraph_lang.v2 check <file.pbl | doc.json> [--interfaces m.json]...`: the checker's findings.
`python -m process_bigraph_lang.v2 diff <a.json> <b.json>`: explain how two documents differ after normalization.
`python -m process_bigraph_lang.v2 describe <module>...` / `describe-model <sbml>`: headers from code or SBML.

Documents are JSON (`bigraph_schema.json_codec` encoding, so numpy arrays survive) or CompositeSpec yaml.
Sidecar assets of `decompile` are written next to the output when `--out` is given, else listed on stderr.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from process_bigraph_lang.v2 import (
    CompileError,
    InterfaceRegistry,
    compile_file,
    decompile,
    diff_documents,
    equivalent,
    print_interfaces,
)


def _load(path: Path) -> tuple[dict[str, Any], bool]:
    text = path.read_text(encoding="utf-8")
    if path.suffix in (".yaml", ".yml"):
        import yaml

        loaded = yaml.safe_load(text)
        return loaded, True
    from bigraph_schema import json_codec  # type: ignore[import-untyped]

    loaded = json_codec.loads(text)
    return loaded, False


def _registry(manifests: list[str] | None) -> InterfaceRegistry | None:
    if not manifests:
        return None
    import json

    registry = InterfaceRegistry(decls=[])
    for manifest in manifests:
        registry.decls.extend(
            InterfaceRegistry.from_manifest(json.loads(Path(manifest).read_text(encoding="utf-8"))).decls
        )
    return registry


def _decompile(args: argparse.Namespace) -> int:
    path = Path(args.document)
    loaded, is_spec = _load(path)
    printed = decompile(
        loaded,
        name=path.stem.replace(".composite", ""),
        registry=_registry(args.interfaces),
        kind="spec" if is_spec else "document",
    )
    if args.out:
        out = Path(args.out)
        out.write_text(printed.text, encoding="utf-8")
        for asset_name, content in printed.assets.items():
            target = out.parent / asset_name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
        print(f"wrote {out} and {len(printed.assets)} asset(s)", file=sys.stderr)
    else:
        sys.stdout.write(printed.text)
        for asset_name in printed.assets:
            print(f"asset (not written): {asset_name}", file=sys.stderr)
    return 0


def _compile(args: argparse.Namespace) -> int:
    manifests = [Path(m) for m in args.interfaces or []]
    try:
        compiled = compile_file(args.document, manifests=manifests, to=args.to, strict=args.strict)
    except CompileError as error:
        for diagnostic in error.diagnostics:
            print(diagnostic, file=sys.stderr)
        print("compile failed", file=sys.stderr)
        return 1
    for diagnostic in compiled.diagnostics:
        print(diagnostic, file=sys.stderr)
    if args.to == "spec":
        import yaml

        text = yaml.safe_dump(compiled.document, sort_keys=False)
    else:
        from bigraph_schema import json_codec

        text = json_codec.dumps(compiled.document, indent=2) + "\n"
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"wrote {args.out}", file=sys.stderr)
    else:
        sys.stdout.write(text)
    return 0


def _diff(args: argparse.Namespace) -> int:
    import process_bigraph as pg  # type: ignore[import-untyped]

    core = pg.allocate_core()
    a, _ = _load(Path(args.a))
    b, _ = _load(Path(args.b))
    if equivalent(a, b, core):
        return 0
    print(diff_documents(a, b, core))
    return 1


def _describe(args: argparse.Namespace) -> int:
    import json

    registry = InterfaceRegistry.from_modules(*args.modules)
    if args.manifest:
        Path(args.manifest).write_text(
            json.dumps(registry.to_manifest(), indent=2, default=str) + "\n", encoding="utf-8"
        )
    files = {
        module: print_interfaces([d for d in registry.decls if d.module == module], module) for module in args.modules
    }
    if args.out and (len(files) > 1 or Path(args.out).is_dir()):
        out_dir = Path(args.out)
        out_dir.mkdir(parents=True, exist_ok=True)
        for module, text in files.items():
            (out_dir / f"{module}.pbl").write_text(text, encoding="utf-8")
        print(f"wrote {len(files)} interface file(s) to {out_dir}", file=sys.stderr)
    elif args.out:
        Path(args.out).write_text(next(iter(files.values())), encoding="utf-8")
    else:
        sys.stdout.write("".join(files.values()))
    return 0


def _check(args: argparse.Namespace) -> int:
    from process_bigraph_lang.v2.check import check_file

    source = Path(args.document)
    manifests = [Path(m) for m in args.interfaces or []]
    if source.suffix in (".json", ".yaml", ".yml"):  # a document: decompile it, then check the text
        import tempfile

        loaded, is_spec = _load(source)
        printed = decompile(loaded, name=source.stem, kind="spec" if is_spec else "document")
        with tempfile.TemporaryDirectory() as tmp:
            text = Path(tmp) / f"{source.stem}.pbl"
            text.write_text(printed.text, encoding="utf-8")
            diagnostics = check_file(text, manifests)
    else:
        diagnostics = check_file(source, manifests)
    for diagnostic in diagnostics:
        print(diagnostic)
    errors = sum(1 for d in diagnostics if d.severity == "error")
    print(f"{errors} error(s), {sum(1 for d in diagnostics if d.severity == 'warning')} warning(s)", file=sys.stderr)
    return 1 if errors else 0


def _describe_model(args: argparse.Namespace) -> int:
    import json

    from process_bigraph_lang.v2.sbml import describe_sbml, print_model_header

    header = describe_sbml(args.model)
    if args.manifest:
        Path(args.manifest).write_text(json.dumps(header.to_dict(), indent=2) + "\n", encoding="utf-8")
    text = print_model_header(header)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m process_bigraph_lang.v2")
    commands = parser.add_subparsers(dest="command", required=True)
    compile_cmd = commands.add_parser("compile", help="parse and check a .pbl file, then write the document")
    compile_cmd.add_argument("document", help="a .pbl file (file(...) references resolve next to it)")
    compile_cmd.add_argument("--interfaces", action="append", help="a manifest.json (repeatable)")
    compile_cmd.add_argument("--to", choices=["document", "spec"], default="document")
    compile_cmd.add_argument("--strict", action="store_true", help="warnings fail the compile too")
    compile_cmd.add_argument("-o", "--out", help="write the document (JSON) or CompositeSpec (yaml) here")
    compile_cmd.set_defaults(run=_compile)
    decompile_cmd = commands.add_parser(
        "decompile", aliases=["print"], help="print a document or CompositeSpec as .pbl text"
    )
    decompile_cmd.add_argument("document")
    decompile_cmd.add_argument("--out", help="write the text here (assets go next to it)")
    decompile_cmd.add_argument(
        "--interfaces", action="append", help="a manifest.json (repeatable); matching addresses print as imports"
    )
    decompile_cmd.set_defaults(run=_decompile)
    describe_cmd = commands.add_parser("describe", help="generate interface declarations from Python modules")
    describe_cmd.add_argument("modules", nargs="+", help="importable module names (run in the package's env)")
    describe_cmd.add_argument("--manifest", help="write the JSON manifest here")
    describe_cmd.add_argument(
        "--out", help="the .pblang interface file (one module) or a directory (one file per module)"
    )
    describe_cmd.set_defaults(run=_describe)
    model_cmd = commands.add_parser("describe-model", help="generate a model header from an SBML file")
    model_cmd.add_argument("model", help="an SBML file")
    model_cmd.add_argument("--manifest", help="write the JSON form here")
    model_cmd.add_argument("--out", help="write the .pblang model header here")
    model_cmd.set_defaults(run=_describe_model)
    check_cmd = commands.add_parser("check", help="statically check a .pbl file or a document against manifests")
    check_cmd.add_argument(
        "document", help="a .pbl file, or a document (.json) / CompositeSpec (.yaml) to print and check"
    )
    check_cmd.add_argument("--interfaces", action="append", help="a manifest.json (repeatable)")
    check_cmd.set_defaults(run=_check)
    diff_cmd = commands.add_parser("diff", help="compare two documents after normalization (exit 1 if they differ)")
    diff_cmd.add_argument("a")
    diff_cmd.add_argument("b")
    diff_cmd.set_defaults(run=_diff)
    args = parser.parse_args(argv)
    result: int = args.run(args)
    return result


if __name__ == "__main__":
    sys.exit(main())
