"""
Application settings for Telegraph.

Defines Pydantic models that control:
- Template directory locations.
- Default rendering options.
- Pipeline behavior and defaults.
"""

from pathlib import Path
from typing import Self

from pydantic import model_validator
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)


class AppSettings(BaseSettings):
    """
    Application-wide defaults and directories for Telegraph.

    Attributes
    ----------
    app_dir : str
        Working source directory for the installed application.
    working_dir : str
        Base home directory used to derive Telegraph folders.
    projects_dir : str
        Directory containing Telegraph project workspaces.
    config_dir : str
        Directory containing the global Telegraph config file.
    app_config_file : str
        Path to the global Telegraph YAML configuration file.
    environment : str
        Free-form environment label for the current install.
    use_tls : bool
        Default TLS behavior for SMTP connections.
    host : str
        Default SMTP host.
    port : int
        Default SMTP port.
    """

    app_dir: str = str(Path().cwd())
    working_dir: str = str(Path().home())
    projects_dir: str = str(Path(working_dir) / "telegraph_projects")
    config_dir: str = str(Path(working_dir) / ".telegraph")
    app_config_file: str = str(Path(config_dir) / "telegraph-config.yaml")
    environment: str = "local"

    use_tls: bool = True
    host: str = "changethis"
    port: int = 587

    model_config = SettingsConfigDict(
        yaml_file=[
            app_config_file,
            "./telegraph-default-config.yaml",
            "./test_config.yaml",
        ],
        extra="ignore",
        env_prefix="TELEGRAPH_",
        env_nested_delimiter="_",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """
        Define the order of configuration sources.

        Parameters
        ----------
        settings_cls : type[BaseSettings]
            Settings class being initialized.
        init_settings : PydanticBaseSettingsSource
            Explicit constructor arguments.
        env_settings : PydanticBaseSettingsSource
            Environment-variable source.
        dotenv_settings : PydanticBaseSettingsSource
            Dotenv-file source.
        file_secret_settings : PydanticBaseSettingsSource
            File-secret source.

        Returns
        -------
        tuple[PydanticBaseSettingsSource, ...]
            Ordered settings sources, highest precedence first.
        """
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            YamlConfigSettingsSource(settings_cls),
            file_secret_settings,
        )

    def _check_default_secret(self, var: str, value: str | None) -> None:
        if value == "changethis":
            message = (
                f'The value of "{var}" is set to "changethis". '
                f"Please change it."
            )
            print(message)

    @model_validator(mode="after")
    def _enforce_non_default_secrets(self) -> Self:
        """Warn when the default placeholder SMTP host is still in use."""
        self._check_default_secret("host", self.host)
        return self


if __name__ == "__main__":
    print(AppSettings().model_dump_json(indent=2))
