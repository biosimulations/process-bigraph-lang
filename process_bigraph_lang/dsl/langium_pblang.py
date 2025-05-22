import os
import subprocess
import tempfile
from os import PathLike
from pathlib import Path

from process_bigraph_lang.dsl.ast_model import ASTModel
from process_bigraph_lang.dsl.bind_ast import bind_ast_model

bin_dir = Path(os.path.abspath(__file__)).parent.parent / "bin"


def langium_parse_pblang_file(filename: PathLike[str]) -> ASTModel:
    json_str = _langium_generate(filename)
    ast_model = ASTModel.model_validate_json(json_str)
    bind_ast_model(ast_model)
    return ast_model


def langium_parse_pblang_str(pblang_str: str) -> ASTModel:
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir) / "test.pblang"
        with open(tmp_path, "w") as f:
            f.write(pblang_str)
        json_str = _langium_generate(tmp_path)
        ast_model = ASTModel.model_validate_json(json_str)
        bind_ast_model(ast_model)
        return ast_model


# run cli-native with a filename of a .pblang file
def _langium_generate(filename: PathLike[str]) -> str:
    if not bin_dir.exists():
        raise FileNotFoundError(bin_dir)
    if not bin_dir.is_dir():
        raise NotADirectoryError(bin_dir)
    exe_file_path = next(f for f in bin_dir.iterdir() if f.name.startswith("cli-native"))
    if not exe_file_path:
        raise ValueError(f"DSL executable 'cli-native' or 'cli-native.exe' not found in {bin_dir}")

    file_path = Path(filename)
    if not file_path.exists():
        raise FileNotFoundError(filename)
    if not file_path.is_file():
        raise NotADirectoryError(filename)
    if not file_path.name.endswith(".pblang"):
        raise ValueError(f"File {filename} is not a .pblang file")
    if not file_path.is_absolute():
        raise ValueError(f"File {filename} is not an absolute path")
    if not file_path.stat().st_size > 0:
        raise ValueError(f"File {filename} is empty")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        tmp_path.mkdir(parents=True, exist_ok=True)

        result: subprocess.CompletedProcess[str] = subprocess.run(
            [exe_file_path, "generate", str(file_path), "--destination", str(tmp_path)], capture_output=True, text=True
        )
        if result.returncode != 0:
            raise RuntimeError(f"Error generating model: {result.stderr.strip()}")
        # Read the generated JSON file (only one file in the temporary directory)
        json_file = next(tmp_path.glob("*.json"))
        if not json_file:
            raise RuntimeError("No JSON file generated.")
        with open(json_file) as file:
            json_content = file.read()
        return (
            json_content.replace('"$type":', '"obj_type":')
            .replace('"$ref":', '"ref":')
            .replace('"$refText":', '"ref_text":')
        )


def _langium_validate(filename: PathLike[str]) -> tuple[str, str]:
    if not bin_dir.exists():
        raise FileNotFoundError(bin_dir)
    if not bin_dir.is_dir():
        raise NotADirectoryError(bin_dir)
    exe_file_path = next(f for f in bin_dir.iterdir() if f.name.startswith("cli-native"))
    if not exe_file_path:
        raise ValueError(f"DSL executable 'cli-native' or 'cli-native.exe' not found in {bin_dir}")

    file_path = Path(filename)
    if not file_path.exists():
        raise FileNotFoundError(filename)
    if not file_path.is_file():
        raise NotADirectoryError(filename)
    if not file_path.name.endswith(".pblang"):
        raise ValueError(f"File {filename} is not a .pblang file")
    if not file_path.is_absolute():
        raise ValueError(f"File {filename} is not an absolute path")
    if not file_path.stat().st_size > 0:
        raise ValueError(f"File {filename} is empty")

    result: subprocess.CompletedProcess[str] = subprocess.run(
        [exe_file_path, "parseAndValidate", str(file_path)], capture_output=True, text=True
    )
    return result.stdout.strip(), result.stderr.strip()
