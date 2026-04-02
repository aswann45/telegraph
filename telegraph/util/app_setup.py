"""
Application setup utilities for Telegraph.

Contains functions to:
- Initialize application state.
- Load configuration.
- Prepare template and output directories.
"""

from pathlib import Path

import typer
import yaml
from pydantic import BaseModel
from pydantic_settings import BaseSettings

from telegraph.config import AppSettings, ProjectSettings


def make_yaml_config_file(
    settings: BaseSettings | BaseModel, location: Path
) -> None:
    """
    Create YAML config files for given settings class.

    Will create a default configuration file for the application in the
    application directory if it does not exist. The file will contain a
    header warning not to edit it and a dump of the settings class.

    The file is written in YAML format.

    Parameters
    ----------
    settings : type[BaseSettings]
        The settings class to create the config file for.

    Returns
    -------
    None
    """
    if not location.exists():
        location.parent.mkdir(parents=True, exist_ok=True)
        with open(location, "a") as f:
            yaml.dump(settings.model_dump(exclude_none=True), f)
            typer.echo(f"Created config file at {str(location)}.")
    else:
        typer.echo(f"File {str(location)} already exists. Skipping.")
    typer.echo("Done.")


def app_setup() -> None:
    """
    Create Telegraph application directories and global config.

    Creates the default projects directory, config directory, and global YAML
    config file when they do not already exist.
    """
    config = AppSettings()

    # create default directories
    typer.echo("Creating default directories.")
    Path(config.projects_dir).mkdir(exist_ok=True, parents=True)
    Path(config.config_dir).mkdir(exist_ok=True, parents=True)
    typer.echo("Done.")

    # create default config file
    typer.echo("Creating global app config.")
    make_yaml_config_file(
        settings=config, location=Path(config.app_config_file)
    )
    typer.echo("Done.")

    typer.echo("Initial setup complete.")


def new_project_setup(project_name: str) -> None:
    """
    Create a new Telegraph project scaffold.

    Parameters
    ----------
    project_name : str
        Name of the project directory to create under the projects root.
    """
    app_config = AppSettings()

    typer.echo("Setting up new project.")
    typer.echo("Creating new project directories.")
    project_dir = Path(app_config.projects_dir) / project_name
    project_dir.mkdir()

    dirs = [
        "templates",
        "build",
    ]

    for d in dirs:
        (project_dir / d).mkdir()

    typer.echo("Done.")

    typer.echo("Creating project config.")
    config = ProjectSettings(
        project_name=project_name,
        template_path="templates",
        build_path="build",
        data_file="data.csv",
    )
    make_yaml_config_file(
        settings=config,
        location=project_dir / "telegraph-project-config.yaml",
    )
    typer.echo("Done.")

    typer.echo("Creating template base files.")
    template_dir = project_dir / "templates"

    # TODO: make more fleshed out sample template files
    (template_dir / "body.html.j2").touch()
    (template_dir / "body.txt.j2").touch()
    (template_dir / "subject.txt.j2").touch()
    typer.echo("Done.")

    typer.echo(f"{project_name} project setup complete.")
