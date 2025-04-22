import shutil
import subprocess
import sys
from collections.abc import Mapping
from pathlib import Path


def run_command(command: str, cwd: Path, env: Mapping[str, str] | None = None) -> None:
    result = subprocess.run(command, cwd=cwd, env=env, shell=True, check=True, text=True)
    if result.returncode != 0:
        sys.exit(result.returncode)


def main() -> None:
    root_dir = Path(__file__).resolve().parent
    dsl_cli_dir = root_dir / "dsl_cli"
    dist_dir = root_dir / "dsl_cli" / "dist"
    process_bigraph_lang_bin_dir = root_dir / "process_bigraph_lang" / "bin"

    # Ensure the process_bigraph_lang/bin directory exists
    process_bigraph_lang_bin_dir.mkdir(parents=True, exist_ok=True)

    # make sure Node version 23 is used


    # Build DSL CLI executable from dsl_cli/ node project
    run_command("npm install", cwd=dsl_cli_dir)
    run_command("npm run langium:generate", cwd=dsl_cli_dir)
    run_command("npm run build", cwd=dsl_cli_dir)
    run_command("npm run build:native", cwd=dsl_cli_dir)

    # Copy the cli-native executable from dsl_cli/cli-native* to process_bigraph_lang/bin
    for ext in ["", ".exe"]:
        cli_native_executable = dist_dir / f"cli-native{ext}"
        if cli_native_executable.exists():
            shutil.copy(cli_native_executable, process_bigraph_lang_bin_dir / f"cli-native{ext}")

if __name__ == "__main__":
    main()
