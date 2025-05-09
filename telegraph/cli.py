from typing import Annotated

import typer

from .util import (
    initial_setup,
    new_project_setup,
)

cli = typer.Typer(no_args_is_help=True)


@cli.command()
def init() -> None:
    initial_setup()


@cli.command()
def new_project(project_name: Annotated[str, typer.Argument()]) -> None:
    new_project_setup(project_name=project_name)
