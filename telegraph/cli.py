"""
Command-line interface for Telegraph, powered by Typer.

Exposes commands for:
- Initializing Telegraph application directories.
- Scaffolding new project workspaces.
- Inspecting resolved project configuration.
- Loading project context data.
- Sending rendered email output.
"""

from pathlib import Path
from typing import Annotated

import typer
import yaml

from .config import ResolvedProjectSettings
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


def get_runtime_config(
    project: str | None = None,
) -> ResolvedProjectSettings:
    """
    Resolve runtime configuration for a CLI command.

    Parameters
    ----------
    project : str | None, optional
        Project name to resolve. When omitted, Telegraph attempts to load
        `telegraph-project-config.yaml` from the current working directory.

    Returns
    -------
    ResolvedProjectSettings
        Fully resolved settings ready for runtime use.
    """
    return handle_project_config(project)


@cli.command()
def init() -> None:
    """Create Telegraph application directories and global config."""
    app_setup()


@cli.command()
def new_project(project_name: Annotated[str, typer.Argument()]) -> None:
    """Create a new Telegraph project scaffold."""
    new_project_setup(project_name=project_name)


@cli.command("show-config")
def show_config(
    project: Annotated[str | None, typer.Option()] = None,
) -> None:
    """Print the resolved configuration for a project."""
    runtime_config = get_runtime_config(project)
    typer.echo(
        yaml.safe_dump(
            runtime_config.model_dump(mode="json"),
            sort_keys=False,
        )
    )


@cli.command()
def load_context_data(
    project: Annotated[str | None, typer.Option()] = None,
    file_name: Annotated[Path | None, typer.Option()] = None,
    write_to_file: Annotated[bool, typer.Option()] = True,
) -> list[Context]:
    """Load project context data and optionally write normalized JSON."""
    runtime_config = get_runtime_config(project)
    typer.echo("Loading context data...")
    data = _load_context_data(
        config=runtime_config,
        write_to_file=write_to_file,
        data_file=file_name,
    )
    typer.echo("Done")
    return data


@cli.command()
def send(
    password: Annotated[str, typer.Option(prompt=True, hide_input=True)],
    project: Annotated[str | None, typer.Option()] = None,
    data_file: Annotated[Path | None, typer.Option()] = None,
    limit: Annotated[int | None, typer.Option()] = None,
    to_file: Annotated[bool, typer.Option()] = True,
) -> None:
    """Render project emails and send or write them."""
    runtime_config = get_runtime_config(project)
    send_emails(
        config=runtime_config,
        data_file=data_file,
        password=password,
        limit=limit,
        to_file=to_file,
    )
    typer.echo("Done.")
