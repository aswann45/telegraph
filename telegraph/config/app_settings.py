from pathlib import Path
from typing import Self

from pydantic import model_validator
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)

from telegraph.config.smtp_settings import SMTPConfig


class Settings(BaseSettings):
    project_name: str = "Telegraph"
    stack_name: str = "telegraph"
    app_dir: str = str(Path().cwd())
    working_dir: str = str(Path().home())
    projects_dir: str = str(Path(working_dir) / "telegraph_projects")
    config_dir: str = str(Path(working_dir) / ".telegraph")
    environment: str = "local"

    smtp_config: SMTPConfig = SMTPConfig()

    model_config = SettingsConfigDict(
        yaml_file=[
            "./telegraph-default-config.yaml",
            str(Path(config_dir) / "telegraph-config.yaml"),
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
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            YamlConfigSettingsSource(settings_cls),
            file_secret_settings,
        )

    def _check_default_secret(self, var: str, value: str | None) -> None:
        if value == "changethis":
            message = f'The value of "{var}" is set to "changethis". Please change it.'
            raise ValueError(message)

    @model_validator(mode="after")
    def _enforce_non_default_secrets(self) -> Self:
        self._check_default_secret("smtp_config.host", self.smtp_config.host)
        self._check_default_secret("smtp_config.username", self.smtp_config.username)
        self._check_default_secret("smtp_config.password", self.smtp_config.password)
        return self


if __name__ == "__main__":
    print(Settings().model_dump_json(indent=2))
