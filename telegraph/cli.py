"""
Command-line interface for Telegraph, powered by Typer.

Defines commands and options for:
- Rendering templates to files.
- Running mail-merge pipelines.
- Sending emails via SMTP.
"""

from pathlib import Path
from typing import Annotated

import typer

from .config import ProjectSettings
from .models import Context
from .service import handle_project_config, send_emails
from .service import (
    load_context_data as _load_context_data,
)
from .util import (
    app_setup,
    new_project_setup,
)

cli = typer.Typer(no_args_is_help=True)

config: ProjectSettings | None = None


@cli.callback()
def main(
    ctx: typer.Context,
    project: Annotated[str | None, typer.Option()] = None,
) -> None:
    global config
    if ctx.invoked_subcommand in {"init", "new-project"}:
        return
    config = handle_project_config(project)


@cli.command()
def init() -> None:
    app_setup()


@cli.command()
def new_project(project_name: Annotated[str, typer.Argument()]) -> None:
    new_project_setup(project_name=project_name)


@cli.command()
def load_context_data(
    file_name: Annotated[Path | None, typer.Option()] = None,
    write_to_file: Annotated[bool, typer.Option()] = True,
) -> list[Context]:
    if config is None:
        raise typer.BadParameter("Project configuration is required.")
    typer.echo("Loading context data...")
    data = _load_context_data(
        config=config, write_to_file=write_to_file, data_file=file_name
    )
    typer.echo("Done")
    return data


@cli.command()
def send(
    password: Annotated[str, typer.Option(prompt=True, hide_input=True)],
    data_file: Annotated[Path | None, typer.Option()] = None,
    limit: Annotated[int | None, typer.Option()] = None,
    to_file: Annotated[bool, typer.Option()] = True,
) -> None:
    if config is None:
        raise typer.BadParameter("Project configuration is required.")
    send_emails(
        config=config,
        data_file=data_file,
        password=password,
        limit=limit,
        to_file=to_file,
    )
    typer.echo("Done.")
