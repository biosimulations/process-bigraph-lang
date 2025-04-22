import os
import subprocess
from os import PathLike
from pathlib import Path

root_dir = Path(os.path.dirname(os.path.abspath(__file__))).parent.parent


# run cli-native with a filename of a .pblang file
def validate_file(filename: PathLike[str]) -> tuple[str, str]:
    """
    Validate a .pblang file using the cli-native executable.

    Args:
        filename (str): The path to the .pblang file to validate.

    Returns:
        str: The output from the cli-native validation command.
    """

    # Execute the command and return the output
    executable_path = root_dir / "dsl_cli" / "dist" / "cli-native"
    if not executable_path.exists():
        raise FileNotFoundError(executable_path)
    result: subprocess.CompletedProcess[str] = subprocess.run(
        [executable_path, "parseAndValidate", str(filename)], capture_output=True, text=True
    )
    return result.stdout, result.stderr
