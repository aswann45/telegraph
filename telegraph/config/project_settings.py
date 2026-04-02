"""
Project-level configuration and resolution for Telegraph.

Provides:
- `ProjectSettings`, the project-scoped config model loaded from YAML.
- `ResolvedProjectSettings`, the fully merged runtime config.
- Helpers to locate, load, and resolve project config against app defaults.
"""

from collections.abc import Sequence
from pathlib import Path
from typing import Self

import yaml
from pydantic import BaseModel, EmailStr, model_validator

from .app_settings import AppSettings

app_settings = AppSettings()
DEFAULT_PROJECT_CONFIG_FILE = "telegraph-project-config.yaml"


class ProjectSettings(BaseModel):
    """
    Project-level configuration for Telegraph.

    Configuration for a single Telegraph project.

    This model reflects the user-editable project YAML file. Runtime code
    should use `ResolvedProjectSettings`, which merges these project values
    with `AppSettings` defaults and resolves file paths.

    Attributes
    ----------
    project_name : str
        User-facing name of the Telegraph project.
    username : str
        SMTP username used for authentication.
    use_tls : bool | None
        Project override for TLS behavior.
    host : str | None
        Project override for the SMTP host.
    port : int | None
        Project override for the SMTP port.
    from_address : EmailStr
        Default sender address for rendered mail.
    project_config_file : str | None
        Optional explicit path to the project YAML file.
    template_path : str | None
        Optional project-relative or absolute template directory.
    build_path : str | None
        Optional project-relative or absolute build directory.
    data_file : str | None
        Optional project-relative or absolute source data file.
    """

    project_name: str = "changethis"

    username: str = "changethis"

    use_tls: bool | None = None
    host: str | None = None
    port: int | None = None
    from_address: EmailStr = "changethis"

    project_config_file: str | None = None
    template_path: str | None = None
    build_path: str | None = None
    data_file: str | None = None

    subject: str | None = None
    cc: Sequence[EmailStr] | None = None
    bcc: Sequence[EmailStr] | None = None
    reply_to: Sequence[EmailStr] | None = None
    attachments: Sequence[Path] | None = None

    def _check_default_secret(self, var: str, value: str | None) -> None:
        if value == "changethis":
            message = (
                f'The value of "{var}" is set to "changethis". '
                f"Please change it."
            )
            print(message)

    @model_validator(mode="after")
    def _enforce_non_default_secrets(self) -> Self:
        """Warn when required project credentials use placeholder values."""
        self._check_default_secret("username", self.username)
        self._check_default_secret("from_address", self.from_address)
        return self


class ResolvedProjectSettings(BaseModel):
    """
    Fully resolved project settings for runtime use.

    This model merges project-level YAML with app defaults and normalizes
    project-relative paths into absolute `Path` values.

    Attributes
    ----------
    project_name : str
        User-facing name of the Telegraph project.
    username : str
        SMTP username used for authentication.
    use_tls : bool
        Effective TLS setting after project and app defaults are merged.
    host : str
        Effective SMTP host.
    port : int
        Effective SMTP port.
    from_address : EmailStr
        Effective sender address.
    project_config_file : Path
        Absolute path to the project YAML file used for resolution.
    project_dir : Path
        Absolute directory containing the project config file.
    template_path : Path
        Absolute directory containing the project's templates.
    build_path : Path
        Absolute build directory for generated artifacts.
    data_file : Path
        Absolute path to the default project data file.
    """

    project_name: str

    username: str

    use_tls: bool
    host: str
    port: int
    from_address: EmailStr

    project_config_file: Path
    project_dir: Path
    template_path: Path
    build_path: Path
    data_file: Path

    subject: str | None = None
    cc: Sequence[EmailStr] | None = None
    bcc: Sequence[EmailStr] | None = None
    reply_to: Sequence[EmailStr] | None = None
    attachments: Sequence[Path] | None = None


def get_project_config_path(
    project_name: str | None = None,
    app_config: AppSettings | None = None,
) -> Path:
    """
    Return the expected config-file path for a project.

    Parameters
    ----------
    project_name : str | None, optional
        Name of the project to locate. When omitted, Telegraph looks for a
        config file in the current working directory.
    app_config : AppSettings | None, optional
        Application defaults used to derive the projects directory.

    Returns
    -------
    Path
        Absolute path to the expected project configuration file.
    """
    config = app_config or AppSettings()

    if project_name is None:
        return (Path.cwd() / DEFAULT_PROJECT_CONFIG_FILE).resolve()

    return (
        Path(config.projects_dir) / project_name / DEFAULT_PROJECT_CONFIG_FILE
    ).resolve()


def load_project_settings(
    project_name: str | None = None,
    app_config: AppSettings | None = None,
) -> ProjectSettings:
    """
    Load raw project settings from YAML.

    Parameters
    ----------
    project_name : str | None, optional
        Name of the project to load. When omitted, Telegraph loads the config
        file from the current working directory.
    app_config : AppSettings | None, optional
        Application defaults used to derive the project path.

    Returns
    -------
    ProjectSettings
        Parsed project-scoped settings from YAML.

    Raises
    ------
    FileNotFoundError
        If the expected project config file does not exist.
    ValueError
        If the YAML root is not a mapping.
    """
    project_config_file = get_project_config_path(
        project_name=project_name,
        app_config=app_config,
    )

    if project_config_file.exists() is False:
        raise FileNotFoundError(
            "Could not find a config file for this project. "
            "Are you in the right directory or specify an existing project "
            "name?"
        )

    project_config = yaml.safe_load(project_config_file.read_text()) or {}
    if not isinstance(project_config, dict):
        raise ValueError("Project config must contain a YAML mapping.")

    project_config.setdefault(
        "project_name",
        project_name or project_config_file.parent.name,
    )
    project_config["project_config_file"] = str(project_config_file)

    return ProjectSettings.model_validate(project_config)


def _resolve_project_path(
    path_value: str | None,
    *,
    project_dir: Path,
    default_path: Path,
) -> Path:
    if path_value is None:
        return default_path.resolve()

    path = Path(path_value)
    if path.is_absolute():
        return path.resolve()
    return (project_dir / path).resolve()


def resolve_project_settings(
    project_name: str | None = None,
    *,
    app_config: AppSettings | None = None,
    project_settings: ProjectSettings | None = None,
) -> ResolvedProjectSettings:
    """
    Merge app defaults with project settings into runtime config.

    Parameters
    ----------
    project_name : str | None, optional
        Project name to resolve. Ignored when `project_settings` is provided.
    app_config : AppSettings | None, optional
        Application defaults to use during resolution.
    project_settings : ProjectSettings | None, optional
        Raw project settings to resolve directly.

    Returns
    -------
    ResolvedProjectSettings
        Runtime-ready settings with merged defaults and absolute paths.
    """
    config = app_config or AppSettings()
    project = project_settings or load_project_settings(
        project_name=project_name,
        app_config=config,
    )

    project_config_file = (
        Path(project.project_config_file).resolve()
        if project.project_config_file is not None
        else get_project_config_path(project.project_name, config)
    )
    project_dir = project_config_file.parent.resolve()

    return ResolvedProjectSettings(
        project_name=project.project_name,
        username=project.username,
        use_tls=project.use_tls
        if project.use_tls is not None
        else config.use_tls,
        host=project.host or config.host,
        port=project.port if project.port is not None else config.port,
        from_address=project.from_address,
        project_config_file=project_config_file,
        project_dir=project_dir,
        template_path=_resolve_project_path(
            project.template_path,
            project_dir=project_dir,
            default_path=project_dir / "templates",
        ),
        build_path=_resolve_project_path(
            project.build_path,
            project_dir=project_dir,
            default_path=project_dir / "build",
        ),
        data_file=_resolve_project_path(
            project.data_file,
            project_dir=project_dir,
            default_path=project_dir / "data.csv",
        ),
        subject=project.subject,
        cc=project.cc,
        bcc=project.bcc,
        reply_to=project.reply_to,
        attachments=project.attachments,
    )


if __name__ == "__main__":
    print(ProjectSettings().model_dump_json(indent=2))
