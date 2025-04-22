import os
import subprocess
from os import PathLike
from pathlib import Path

bin_dir = Path(os.path.abspath(__file__)).parent.parent / "bin"


# run cli-native with a filename of a .pblang file
def validate_file(filename: PathLike[str]) -> tuple[str, str]:
    """
    Validate a .pblang file using the cli-native executable.

    Args:
        filename (str): The path to the .pblang file to validate.

    Returns:
        str: The output from the cli-native validation command.
    """

    # find name of executable in bin directory starting with 'cli-native'
    # if not found, raise error
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
