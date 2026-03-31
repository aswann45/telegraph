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
    project_name: str = "Telegraph"
    stack_name: str = "telegraph"
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
        """Specify setttings sources."""
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
        self._check_default_secret("host", self.host)
        return self


if __name__ == "__main__":
    print(AppSettings().model_dump_json(indent=2))
