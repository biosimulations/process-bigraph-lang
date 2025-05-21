import os
import sys
from pathlib import Path

import typer
from bigraph_viz import plot_bigraph  # type: ignore[import-untyped]
from process_bigraph import Composite, ProcessTypes  # type: ignore[import-untyped]
from typing_extensions import Annotated

from process_bigraph_lang.antlr_dsl.antlr_pblang_parser import bind_model
from process_bigraph_lang.dsl import generate
from process_bigraph_lang.dsl.ast_model import ASTModel
from process_bigraph_lang.runtime.v1.composite_generator import process_composite
from process_bigraph_lang.runtime.v1.process_bigraph_env import ProcessBigraphEnv
from process_bigraph_lang.runtime.v1.process_generator import register_process_defs
from process_bigraph_lang.runtime.v1.type_generator import register_types
from process_bigraph_lang.runtime.v1.unit_generator import register_units

app = typer.Typer()


@app.command()
def validate(
    pblang_path: Annotated[str, typer.Argument(help="Path to the pblang file to validate")],
    diagram_path: Annotated[str, typer.Argument(help="Path for diagram file")],
) -> None:
    ast_model: ASTModel = generate_model_ast(Path(pblang_path))
    _, pb_doc, pb_core = performConversion(ast_model)
    plot_bigraph(
        state=pb_doc["state"],
        schema=pb_doc["composition"],
        core=pb_core,
        show_values=True,
        out_dir=diagram_path,
        filename="final_diagram",
        dpi="140",
    )


@app.command()
def execute(
    duration: float, pblang_path: Annotated[str, typer.Argument(help="Path to the pblang file to validate")]
) -> None:
    ast_model: ASTModel = generate_model_ast(Path(pblang_path))
    pb_composite, _0, _1 = performConversion(ast_model)

    pb_composite.run(duration)
    print("Execution complete")


def generate_model_ast(pblang_file: os.PathLike[str]) -> ASTModel:
    model_json: str = generate.generate_model(pblang_file)
    model: ASTModel = ASTModel.model_validate_json(model_json)
    bind_model(model)
    # result: str = model.model_dump_json(indent=4)
    # rich.print(result)
    return model


def validate_pb_absolute_path(absolute_path: str) -> str:
    if not os.path.exists(absolute_path):
        sys.stderr.write(f"Error finding pblang file ({absolute_path}):: no file with that name exists.\n")
        exit(1)
    if os.path.isdir(absolute_path):
        sys.stderr.write(f"Error finding pblang file ({absolute_path}):: file is a directory, not a script.\n")
        exit(1)
    if not absolute_path.endswith(".pblang"):
        sys.stderr.write(
            f"Error finding pblang file ({absolute_path}):: file is labeled with an unexpected extension.\n"
        )
        exit(1)
    return absolute_path


def performConversion(ast_model: ASTModel) -> tuple[Composite, dict, ProcessTypes]:
    assembler = ProcessBigraphEnv()

    # # register the libraries
    # spatioflux.register(assembler)
    # toy.register(assembler)

    # register the types, units, and process definitions from the model
    register_types(assembler, ast_model.types)
    register_units(assembler, ast_model.units)
    register_process_defs(assembler, ast_model.processDefs)
    process_composite(ast_model, assembler)

    return assembler.composite, assembler.make_document(), assembler.core


if __name__ == "__main__":
    app()
