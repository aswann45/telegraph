"""
Project-level configuration for Telegraph.

Provides a Pydantic BaseSettings model that loads:
- Host, port, username, password, and TLS flags.
- Environment variables, YAML files, and file secrets.
"""

from collections.abc import Sequence
from pathlib import Path
from typing import Self

from pydantic import BaseModel, EmailStr, Field, model_validator

from telegraph.config import AppSettings

app_settings = AppSettings()


class ProjectSettings(BaseModel):
    """
    Project-level configuration for Telegraph.

    Configuration for SMTP server connection, supporting environment variables
    and YAML file loading. Setting values on this config for `use_tls`, `host`,
    `port`, and `from_address` will override values set in global app settings.
     Values for `subject`, `cc`, `bcc`, `reply_to`, and
     `attachments` will be overriden if set in project context data.

    Parameters
    ----------
    username : str
        Username for SMTP authentication.
    use_tls : bool | None
        Flag to use TLS (default True).
    host : str
        SMTP server hostname.
    port : int
        SMTP server port.
    """

    project_name: str = "changethis"

    username: str = "changethis"

    use_tls: bool = True
    host: str = "changethis"
    port: int = 587
    from_address: EmailStr = "changethis"

    project_config_file: str = Field(
        default_factory=lambda data: str(
            Path(app_settings.projects_dir)
            / data["project_name"]
            / "telegraph-project-config.yaml"
        )
    )
    template_path: str = Field(
        default_factory=lambda data: str(
            Path(app_settings.projects_dir)
            / data["project_name"]
            / "templates"
        )
    )

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
        self._check_default_secret("username", self.username)
        self._check_default_secret("from_address", self.from_address)
        return self


if __name__ == "__main__":
    print(ProjectSettings().model_dump_json(indent=2))
