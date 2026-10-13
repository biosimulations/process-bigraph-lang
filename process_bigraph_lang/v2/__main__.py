"""
`python -m process_bigraph_lang.v2 compile <file.pblang> [--interfaces m.json]... [--to document|spec] [-o out]`:
parse and check the text, then write the document (JSON) or the CompositeSpec (yaml); errors stop it.
`python -m process_bigraph_lang.v2 decompile <doc.json | spec.composite.yaml>`: a document as `.pblang` text.
`python -m process_bigraph_lang.v2 check <file.pblang | doc.json> [--interfaces m.json]...`: the checker's findings.
`python -m process_bigraph_lang.v2 diff <a.json> <b.json>`: explain how two documents differ after normalization.
`python -m process_bigraph_lang.v2 describe <module>...` / `describe-model <sbml>`: headers from code or SBML.
`python -m process_bigraph_lang.v2 sedml describe <x.sedml | x.omex>`: what a SED-ML file asks for, as JSON.
`python -m process_bigraph_lang.v2 sedml translate <x.omex> --solvers s.yaml -i env.json -o dir/`: per-solver composites.

Documents are JSON (`bigraph_schema.json_codec` encoding, so numpy arrays survive) or CompositeSpec yaml.
Sidecar assets of `decompile` are written next to the output when `--out` is given, else listed on stderr.
"""

from __future__ import annotations

import argparse
import json
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
    loads,
    render_interfaces,
)


def _load(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if path.suffix in (".yaml", ".yml"):
        import yaml

        loaded = yaml.safe_load(text)
    else:
        loaded = loads(text)
    if not isinstance(loaded, dict):
        raise SystemExit(f"{path}: not a document")
    return loaded


def _manifests(args: argparse.Namespace) -> list[Path]:
    return [Path(m) for m in getattr(args, "interfaces", None) or []]


def _decompile(args: argparse.Namespace) -> int:
    path = Path(args.document)
    printed = decompile(_load(path), name=path.stem.replace(".composite", ""), manifests=_manifests(args))
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
    try:
        compiled = compile_file(args.document, manifests=_manifests(args), to=args.to, strict=args.strict)
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
        from process_bigraph_lang.v2 import dumps

        text = dumps(compiled.document) + "\n"
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"wrote {args.out}", file=sys.stderr)
    else:
        sys.stdout.write(text)
    return 0


def _diff(args: argparse.Namespace) -> int:
    import process_bigraph as pg  # type: ignore[import-untyped]

    core = pg.allocate_core()
    a, b = _load(Path(args.a)), _load(Path(args.b))
    if equivalent(a, b, core):
        return 0
    print(diff_documents(a, b, core))
    return 1


def _describe(args: argparse.Namespace) -> int:
    registry = InterfaceRegistry.from_modules(*args.modules)
    if args.manifest_only and not args.manifest:
        sys.stdout.write(json.dumps(registry.to_manifest(), indent=2, default=str) + "\n")
        return 0
    if args.manifest:
        registry.write_manifest(Path(args.manifest))
    if args.manifest_only:
        return 0
    files = {
        module: render_interfaces([d for d in registry.decls if d.module == module], module) for module in args.modules
    }
    if args.out and (len(files) > 1 or Path(args.out).is_dir()):
        out_dir = Path(args.out)
        out_dir.mkdir(parents=True, exist_ok=True)
        for module, text in files.items():
            (out_dir / f"{module}.pblang").write_text(text, encoding="utf-8")
        print(f"wrote {len(files)} interface file(s) to {out_dir}", file=sys.stderr)
    elif args.out:
        Path(args.out).write_text(next(iter(files.values())), encoding="utf-8")
    else:
        sys.stdout.write("".join(files.values()))
    return 0


def _check(args: argparse.Namespace) -> int:
    from process_bigraph_lang.v2.check import check_file, check_text

    source = Path(args.document)
    manifests = _manifests(args)
    if source.suffix in (".json", ".yaml", ".yml"):  # a document: decompile it, then check the text
        printed = decompile(_load(source), name=source.stem, manifests=manifests)
        diagnostics = check_text(printed.text, manifests)
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


def _sedml_describe(args: argparse.Namespace) -> int:
    from process_bigraph_lang.v2.sedml import describe_sedml

    text = describe_sedml(args.source).to_json()
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return 0


def _structured(path: Path) -> Any:
    """A JSON file, or a YAML one when PyYAML is installed (it is not a dependency of this package)."""
    text = path.read_text(encoding="utf-8")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        try:
            import yaml
        except ModuleNotFoundError as e:
            raise SystemExit(f"{path}: not JSON, and reading YAML needs PyYAML (pip install pyyaml)") from e
        return yaml.safe_load(text)


def _sedml_translate(args: argparse.Namespace) -> int:
    import dataclasses
    import json

    from process_bigraph_lang.v2.api import CompileError
    from process_bigraph_lang.v2.sedml_translate import compile_instance, instance_archive, solvers_from, translate

    data = _structured(Path(args.solvers)) if args.solvers else []
    solvers = solvers_from(data.get("solvers", []) if isinstance(data, dict) else data)
    translation = translate(args.source, solvers, output_dir=args.output_dir)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    findings = [dataclasses.asdict(f) for f in translation.findings]
    errors = 0
    for task in translation.tasks:
        (out / f"{task.name}.pblang").write_text(task.template, encoding="utf-8")
        for path, content in task.models.items():
            (out / path).write_bytes(content)
        findings += [{**dataclasses.asdict(f), "task": task.task} for f in task.findings]
        for solver, text in task.instances.items():
            (out / f"{task.name}.{solver}.pblang").write_text(text, encoding="utf-8")
            if not args.interfaces:
                continue
            try:
                compiled = compile_instance(task, solver, [Path(m) for m in args.interfaces], addresses=args.addresses)
            except CompileError as e:
                errors += 1
                findings += [{"severity": "error", "code": d.code, "message": d.message, "solver": solver,
                              "task": task.task, "path": d.path} for d in e.diagnostics]  # fmt: skip
                continue
            (out / f"{task.name}.{solver}.omex").write_bytes(instance_archive(task, solver, compiled.document))
    (out / "findings.json").write_text(json.dumps(findings, indent=2) + "\n", encoding="utf-8")
    for f in findings:
        who = f" [{f['solver']}]" if f.get("solver") else ""
        print(f"{f['severity']:<8}{f['code']}{who} {f.get('task', '')}: {f['message']}", file=sys.stderr)
    return 1 if errors or any(f["severity"] == "error" for f in findings) else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m process_bigraph_lang.v2")
    commands = parser.add_subparsers(dest="command", required=True)
    compile_cmd = commands.add_parser("compile", help="parse and check a .pblang file, then write the document")
    compile_cmd.add_argument("document", help="a .pblang file (file(...) references resolve next to it)")
    compile_cmd.add_argument("--interfaces", action="append", help="a manifest.json (repeatable)")
    compile_cmd.add_argument("--to", choices=["document", "spec"], default="document")
    compile_cmd.add_argument("--strict", action="store_true", help="warnings fail the compile too")
    compile_cmd.add_argument("-o", "--out", help="write the document (JSON) or CompositeSpec (yaml) here")
    compile_cmd.set_defaults(run=_compile)
    decompile_cmd = commands.add_parser(
        "decompile", aliases=["print"], help="print a document or CompositeSpec as .pblang text"
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
        "--manifest-only",
        action="store_true",
        help="only the manifest (to --manifest, else stdout): no interface files, so no Langium CLI is needed",
    )
    describe_cmd.add_argument(
        "--out", help="the .pblang interface file (one module) or a directory (one file per module)"
    )
    describe_cmd.set_defaults(run=_describe)
    model_cmd = commands.add_parser("describe-model", help="generate a model header from an SBML file")
    model_cmd.add_argument("model", help="an SBML file")
    model_cmd.add_argument("--manifest", help="write the JSON form here")
    model_cmd.add_argument("--out", help="write the .pblang model header here")
    model_cmd.set_defaults(run=_describe_model)
    sedml_cmd = commands.add_parser("sedml", help="SED-ML: what a file asks for, and its translation")
    sedml_commands = sedml_cmd.add_subparsers(dest="sedml_command", required=True)
    sedml_describe = sedml_commands.add_parser(
        "describe", help="what a .sedml file or a COMBINE/OMEX archive's SED-ML asks for, as JSON (pblang-sedml/0)"
    )
    sedml_describe.add_argument("source", help="a .sedml file or an .omex archive")
    sedml_describe.add_argument("-o", "--out", help="write the JSON here (default: stdout)")
    sedml_describe.set_defaults(run=_sedml_describe)
    sedml_translate = sedml_commands.add_parser(
        "translate",
        help="each SED-ML task as a .pblang template and one instance per solver; with --interfaces, compiled archives",
    )
    sedml_translate.add_argument("source", help="a .sedml file or an .omex archive")
    sedml_translate.add_argument(
        "--solvers",
        help="JSON (or YAML, with PyYAML): [{id, address, algorithms, provides?}], or a mapping with `solvers`",
    )
    sedml_translate.add_argument(
        "-i", "--interfaces", action="append", help="the solvers' environment manifest(s): compile each instance"
    )
    sedml_translate.add_argument("--addresses", choices=["import", "registered"], default="registered")
    sedml_translate.add_argument("--output-dir", default="/experiment/output", help="where the job writes its files")
    sedml_translate.add_argument("-o", "--out", required=True, help="a directory for the texts, models and archives")
    sedml_translate.set_defaults(run=_sedml_translate)
    check_cmd = commands.add_parser("check", help="statically check a .pblang file or a document against manifests")
    check_cmd.add_argument(
        "document", help="a .pblang file, or a document (.json) / CompositeSpec (.yaml) to decompile and check"
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
