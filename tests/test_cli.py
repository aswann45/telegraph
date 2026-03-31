from pathlib import Path

from typer.testing import CliRunner

import telegraph.cli as cli_module
from telegraph.cli import cli
from telegraph.config import ProjectSettings

runner = CliRunner()


def test_init_does_not_require_project_config(monkeypatch):
    called = {"app_setup": False}
    cli_module.config = None

    def fail_handle_project_config(project_name: str | None = None):
        raise AssertionError("handle_project_config should not be called")

    def fake_app_setup():
        called["app_setup"] = True

    monkeypatch.setattr(
        cli_module, "handle_project_config", fail_handle_project_config
    )
    monkeypatch.setattr(cli_module, "app_setup", fake_app_setup)

    result = runner.invoke(cli, ["init"])

    assert result.exit_code == 0
    assert called["app_setup"] is True


def test_new_project_does_not_require_project_config(monkeypatch):
    created: list[str] = []
    cli_module.config = None

    def fail_handle_project_config(project_name: str | None = None):
        raise AssertionError("handle_project_config should not be called")

    def fake_new_project_setup(project_name: str):
        created.append(project_name)

    monkeypatch.setattr(
        cli_module, "handle_project_config", fail_handle_project_config
    )
    monkeypatch.setattr(
        cli_module, "new_project_setup", fake_new_project_setup
    )

    result = runner.invoke(cli, ["new-project", "demo"])

    assert result.exit_code == 0
    assert created == ["demo"]


def test_load_context_data_requires_project_config(
    monkeypatch, tmp_path: Path
):
    cli_module.config = None
    config = ProjectSettings(
        project_name="demo_project",
        username="demo_user",
        host="smtp.example.com",
        from_address="sender@example.com",
    )
    observed: list[tuple[ProjectSettings, bool, Path | None]] = []

    def fake_handle_project_config(project_name: str | None = None):
        return config

    def fake_load_context_data(
        *,
        config: ProjectSettings,
        write_to_file: bool,
        data_file: Path | None,
    ):
        observed.append((config, write_to_file, data_file))
        return []

    data_file = tmp_path / "data.yaml"
    data_file.write_text("[]")

    monkeypatch.setattr(
        cli_module, "handle_project_config", fake_handle_project_config
    )
    monkeypatch.setattr(
        cli_module, "_load_context_data", fake_load_context_data
    )

    result = runner.invoke(
        cli,
        [
            "--project",
            "demo_project",
            "load-context-data",
            "--file-name",
            str(data_file),
        ],
    )

    assert result.exit_code == 0
    assert observed == [(config, True, data_file)]
