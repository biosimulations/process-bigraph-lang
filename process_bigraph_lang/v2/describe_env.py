"""
Describe the process-bigraph components an environment provides, as a `pblang-manifest/0` JSON manifest.

This file depends on the Python standard library only and imports nothing from this package, so it runs as a plain
script inside any environment that has the components installed (a simulator image, a pixi or conda env), whatever
versions of process-bigraph and bigraph-schema it carries:

    python describe_env.py viva_pde_particle --env-name viva-pde-particle --image ghcr.io/...@sha256:... > m.json

It imports every module under the given roots, keeps the step and process classes each one defines, and reads their
`config_schema` and ports the same way `interfaces.describe_module` does (which shares these helpers). A module that
fails to import is recorded under `errors` and skipped, never fatal. Types stay in bigraph-schema's own form; a config
default is recorded when the type carries one (`{"_type": ..., "_default": v}` or `float{0.5}`).
"""

from __future__ import annotations

import argparse
import importlib
import importlib.metadata
import inspect
import json
import pkgutil
import platform
import re
import sys
from typing import Any

MANIFEST_VERSION = "pblang-manifest/0"
NO_DEFAULT: Any = object()
_TRAILING_DEFAULT = re.compile(r"^([^{}]*)\{(.*)\}$")


# --- one class -------------------------------------------------------------------------------------------------


def is_edge_class(cls: type) -> bool:
    """A step or process class: `Edge` is in its MRO (by name, so process-bigraph need not be importable here)."""
    return any(base.__name__ == "Edge" for base in cls.__mro__)


def kind_of(cls: type) -> str:
    return "process" if any(base.__name__ == "Process" for base in cls.__mro__) else "step"


def ports_of(cls: type) -> tuple[dict[str, Any] | None, dict[str, Any] | None, bool]:
    """`inputs()` and `outputs()` with the class standing in for `self`; `None` and dynamic when they need an instance."""
    faces: list[dict[str, Any] | None] = []
    dynamic = False
    for method_name in ("inputs", "outputs"):
        method = getattr(cls, method_name, None)
        if method is None:
            faces.append(None)
            continue
        try:
            ports = method(cls)
        except Exception:  # noqa: BLE001 - ports depend on an instance (self.config, children, ...)
            faces.append(None)
            dynamic = True
            continue
        faces.append({str(k): v for k, v in ports.items()} if isinstance(ports, dict) else None)
    return faces[0], faces[1], dynamic


def doc_of(cls: type) -> str | None:
    """The first paragraph of the class's own docstring."""
    text = cls.__dict__.get("__doc__")
    if not text:
        return None
    first = inspect.cleandoc(text).split("\n\n", 1)[0].strip()
    return first or None


def default_of(spec: Any) -> Any:
    """The default a bigraph-schema type carries, or `NO_DEFAULT`: `{"_type": T, "_default": v}` or `T{v}`."""
    if isinstance(spec, dict):
        return spec["_default"] if "_type" in spec and "_default" in spec else NO_DEFAULT
    if not isinstance(spec, str):
        return NO_DEFAULT
    match = _TRAILING_DEFAULT.match(spec.strip())
    if not match or not _is_single_name(match.group(1).strip()):
        return NO_DEFAULT
    try:
        return json.loads(match.group(2))
    except ValueError:
        return match.group(2)


def _is_single_name(text: str) -> bool:
    """`name` or `name[args]`: no top-level union (`|`, `~`), field (`:`) or tuple, where a default cannot attach."""
    if not text or text.startswith("("):
        return False
    depth = 0
    for char in text:
        if char in "[(":
            depth += 1
        elif char in "])":
            depth -= 1
        elif depth == 0 and char in "|~:,":
            return False
    return True


def config_entry(schema: Any, default: Any = default_of) -> dict[str, dict[str, Any]]:
    """A `config_schema` as manifest config fields: the type (string or dict form, else null) and its default."""
    if not isinstance(schema, dict):
        return {}
    fields: dict[str, dict[str, Any]] = {}
    for key, spec in schema.items():
        value = default(spec)
        fields[str(key)] = {
            "type": spec if isinstance(spec, (str, dict)) else None,
            **({} if value is NO_DEFAULT else {"default": value}),
        }
    return fields


def component(cls: type, module_name: str | None = None, name: str | None = None) -> dict[str, Any]:
    """The manifest entry of one step or process class, addressed `local:!module.Name`."""
    module_name = module_name or cls.__module__
    name = name or cls.__name__
    inputs, outputs, dynamic = ports_of(cls)
    entry: dict[str, Any] = {
        "name": name,
        "kind": kind_of(cls),
        "address": f"local:!{module_name}.{name}",
        "module": module_name,
        "config": config_entry(getattr(cls, "config_schema", None) or {}),
        "inputs": inputs,
        "outputs": outputs,
        "dynamic_ports": dynamic,
    }
    doc = doc_of(cls)
    if doc:
        entry["doc"] = doc
    return entry


# --- an environment --------------------------------------------------------------------------------------------


def _error(module: str, exc: BaseException) -> dict[str, str]:
    message = f"{type(exc).__name__}: {exc}"
    return {"module": module, "error": message if len(message) <= 500 else message[:497] + "..."}


def _modules_under(root: str, errors: list[dict[str, str]]) -> list[Any]:
    """The root module and every submodule that imports (a `__main__` is never imported: it would run)."""
    try:
        module = importlib.import_module(root)
    except Exception as exc:  # noqa: BLE001 - recorded; the other roots still run
        errors.append(_error(root, exc))
        return []
    modules = [module]
    if not hasattr(module, "__path__"):
        return modules

    def onerror(name: str) -> None:
        errors.append(_error(name, sys.exc_info()[1] or RuntimeError("import failed")))

    for info in pkgutil.walk_packages(module.__path__, prefix=root + ".", onerror=onerror):
        if info.name.rsplit(".", 1)[-1] == "__main__":
            continue
        try:
            modules.append(importlib.import_module(info.name))
        except Exception as exc:  # noqa: BLE001 - recorded, never fatal
            errors.append(_error(info.name, exc))
    return modules


def describe_roots(roots: list[str]) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    """Every public step and process class defined under the roots, sorted by address, plus the import errors."""
    errors: list[dict[str, str]] = []
    found: dict[str, dict[str, Any]] = {}
    for root in roots:
        for module in _modules_under(root, errors):
            for name, cls in vars(module).items():
                if (
                    name.startswith("_")
                    or not inspect.isclass(cls)
                    or cls.__module__ != module.__name__
                    or not is_edge_class(cls)
                ):
                    continue
                try:
                    entry = component(cls)
                except Exception as exc:  # noqa: BLE001 - one bad class never stops the rest
                    errors.append(_error(f"{module.__name__}.{name}", exc))
                    continue
                found.setdefault(entry["address"], entry)
    return [found[address] for address in sorted(found)], errors


def _version(distribution: str) -> str | None:
    try:
        return importlib.metadata.version(distribution)
    except importlib.metadata.PackageNotFoundError:
        return None


def environment(roots: list[str], name: str | None, image: str | None) -> dict[str, Any]:
    """Where the manifest was generated: the environment's name and image, Python, and the versions that matter."""
    by_module = importlib.metadata.packages_distributions()
    packages: dict[str, str | None] = {}
    for root in roots:
        top = root.split(".", 1)[0]
        # an editable install may map no top-level module: then try the root's own name as the distribution's
        for dist in by_module.get(top) or [name for name in (top, top.replace("_", "-")) if _version(name)][:1]:
            packages[dist] = _version(dist)
    return {
        "name": name,
        "image": image,
        "python": platform.python_version(),
        "process_bigraph": _version("process-bigraph"),
        "bigraph_schema": _version("bigraph-schema"),
        "packages": packages,
        "roots": roots,
        "generated_by": "process_bigraph_lang/v2/describe_env.py",
    }


def describe_environment(roots: list[str], name: str | None = None, image: str | None = None) -> dict[str, Any]:
    components, errors = describe_roots(roots)
    return {
        "schema_version": MANIFEST_VERSION,
        "environment": environment(roots, name, image),
        "components": components,
        "errors": errors,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().split("\n\n", 1)[0] if __doc__ else None)
    parser.add_argument("roots", nargs="+", help="module roots to describe (every submodule is imported)")
    parser.add_argument("--env-name", help="the environment's name, recorded in the manifest")
    parser.add_argument("--image", help="the image reference the environment was read from, recorded in the manifest")
    parser.add_argument("--out", help="write the manifest here instead of stdout")
    args = parser.parse_args(argv)
    manifest = describe_environment(args.roots, args.env_name, args.image)
    text = json.dumps(manifest, indent=2, default=str) + "\n"
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(text)
    else:
        sys.stdout.write(text)
    print(
        f"described {len(manifest['components'])} component(s), {len(manifest['errors'])} import error(s)",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
