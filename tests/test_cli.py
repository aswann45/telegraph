import importlib
import json
from pathlib import Path

import yaml
from typer.testing import CliRunner

import telegraph.cli as cli_module
import telegraph.config.project_settings as project_settings_module
import telegraph.service as service_module
from telegraph.cli import cli
from telegraph.config import (
    AppSettings,
    ProjectSettings,
    ResolvedProjectSettings,
    resolve_project_settings,
)

runner = CliRunner()
app_setup_module = importlib.import_module("telegraph.util.app_setup")


def configure_test_app(monkeypatch, tmp_path: Path) -> AppSettings:
    home_dir = tmp_path / "home"
    app_dir = tmp_path / "workspace"
    app_dir.mkdir()

    app_config = AppSettings(
        app_dir=str(app_dir),
        working_dir=str(home_dir),
        projects_dir=str(home_dir / "telegraph_projects"),
        config_dir=str(home_dir / ".telegraph"),
        app_config_file=str(home_dir / ".telegraph" / "telegraph-config.yaml"),
        host="smtp.example.com",
        port=587,
        use_tls=True,
    )

    monkeypatch.setattr(app_setup_module, "AppSettings", lambda: app_config)
    monkeypatch.setattr(service_module, "APP_CONFIG", app_config)
    monkeypatch.setattr(project_settings_module, "app_settings", app_config)

    return app_config


def test_init_does_not_require_project_config(monkeypatch):
    called = {"app_setup": False}

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
    raw_config = ProjectSettings(
        project_name="demo_project",
        username="demo_user",
        from_address="sender@example.com",
    )
    config = resolve_project_settings(
        app_config=AppSettings(
            host="smtp.example.com",
            port=587,
            use_tls=True,
        ),
        project_settings=raw_config,
    )
    observed: list[tuple[ResolvedProjectSettings, bool, Path | None]] = []

    def fake_handle_project_config(project_name: str | None = None):
        return config

    def fake_load_context_data(
        *,
        config: ResolvedProjectSettings,
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
            "load-context-data",
            "--project",
            "demo_project",
            "--file-name",
            str(data_file),
        ],
    )

    assert result.exit_code == 0
    assert observed == [(config, True, data_file)]


def test_show_config_uses_resolved_project_config(monkeypatch):
    config = ResolvedProjectSettings(
        project_name="demo_project",
        username="demo_user",
        use_tls=True,
        host="smtp.example.com",
        port=587,
        from_address="sender@example.com",
        project_config_file=Path("/tmp/demo/telegraph-project-config.yaml"),
        project_dir=Path("/tmp/demo"),
        template_path=Path("/tmp/demo/templates"),
        build_path=Path("/tmp/demo/build"),
        data_file=Path("/tmp/demo/data.csv"),
        cc=["cc@example.com"],
    )

    def fake_handle_project_config(project_name: str | None = None):
        return config

    monkeypatch.setattr(
        cli_module, "handle_project_config", fake_handle_project_config
    )

    result = runner.invoke(cli, ["show-config", "--project", "demo_project"])

    assert result.exit_code == 0
    assert "project_name: demo_project" in result.output
    assert "host: smtp.example.com" in result.output
    assert "template_path: /tmp/demo/templates" in result.output
    assert "data_file: /tmp/demo/data.csv" in result.output


def test_show_config_accepts_project_after_subcommand(monkeypatch):
    config = ResolvedProjectSettings(
        project_name="demo_project",
        username="demo_user",
        use_tls=True,
        host="smtp.example.com",
        port=587,
        from_address="sender@example.com",
        project_config_file=Path("/tmp/demo/telegraph-project-config.yaml"),
        project_dir=Path("/tmp/demo"),
        template_path=Path("/tmp/demo/templates"),
        build_path=Path("/tmp/demo/build"),
        data_file=Path("/tmp/demo/data.csv"),
    )
    observed: list[str | None] = []

    def fake_handle_project_config(project_name: str | None = None):
        observed.append(project_name)
        return config

    monkeypatch.setattr(
        cli_module, "handle_project_config", fake_handle_project_config
    )

    result = runner.invoke(cli, ["show-config", "--project", "demo_project"])

    assert result.exit_code == 0
    assert observed[-1] == "demo_project"
    assert "project_name: demo_project" in result.output


def test_new_project_end_to_end(monkeypatch, tmp_path: Path):
    app_config = configure_test_app(monkeypatch, tmp_path)

    init_result = runner.invoke(cli, ["init"])
    assert init_result.exit_code == 0

    result = runner.invoke(cli, ["new-project", "demo"])

    assert result.exit_code == 0

    project_dir = Path(app_config.projects_dir) / "demo"
    assert (project_dir / "telegraph-project-config.yaml").exists()
    assert (project_dir / "templates" / "subject.txt.j2").exists()
    assert (project_dir / "templates" / "body.txt.j2").exists()
    assert (project_dir / "templates" / "body.html.j2").exists()
    assert (project_dir / "build").exists()


def test_load_context_data_end_to_end(monkeypatch, tmp_path: Path):
    app_config = configure_test_app(monkeypatch, tmp_path)

    project_dir = Path(app_config.projects_dir) / "demo"
    (project_dir / "build").mkdir(parents=True)
    (project_dir / "templates").mkdir()

    project_config = ProjectSettings(
        project_name="demo",
        username="demo_user",
        from_address="sender@example.com",
    )
    (project_dir / "telegraph-project-config.yaml").write_text(
        yaml.dump(project_config.model_dump())
    )
    (project_dir / "data.csv").write_text(
        "to_addresses,subject,name\nalice@example.com,Hello,Alice\n"
    )

    result = runner.invoke(cli, ["load-context-data", "--project", "demo"])

    assert result.exit_code == 0

    context_path = project_dir / "build" / "context.json"
    assert context_path.exists()

    loaded = json.loads(context_path.read_text())
    assert loaded == [
        {
            "name": "Alice",
            "subject": "Hello",
            "to_addresses": ["alice@example.com"],
        }
    ]


def test_show_config_end_to_end(monkeypatch, tmp_path: Path):
    app_config = configure_test_app(monkeypatch, tmp_path)

    project_dir = Path(app_config.projects_dir) / "demo"
    project_dir.mkdir(parents=True)

    project_config = ProjectSettings(
        project_name="demo",
        username="demo_user",
        from_address="sender@example.com",
        template_path="custom_templates",
        build_path="custom_build",
        data_file="custom.csv",
    )
    (project_dir / "telegraph-project-config.yaml").write_text(
        yaml.dump(project_config.model_dump(exclude_none=True))
    )

    result = runner.invoke(cli, ["show-config", "--project", "demo"])

    assert result.exit_code == 0
    assert "project_name: demo" in result.output
    assert "host: smtp.example.com" in result.output
    assert (
        f"template_path: {project_dir / 'custom_templates'}" in result.output
    )
    assert f"build_path: {project_dir / 'custom_build'}" in result.output
    assert f"data_file: {project_dir / 'custom.csv'}" in result.output
