from pathlib import Path

import yaml

from telegraph.config import (
    AppSettings,
    ProjectSettings,
    ResolvedProjectSettings,
    resolve_project_settings,
)


def test_app_settings_yaml_and_env(monkeypatch, tmp_path: Path):
    config_file = tmp_path / "test_config.yaml"
    config_file.write_text(
        yaml.dump(
            {
                "host": "smtp.yaml",
                "port": 1025,
                "use_tls": False,
            }
        )
    )

    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("TELEGRAPH_HOST", "smtp.env")

    config = AppSettings()

    assert config.host == "smtp.env"
    assert config.port == 1025
    assert config.use_tls is False


def test_project_settings_constructor_is_project_scoped():
    config = ProjectSettings(
        project_name="demo_project",
        username="demo_user",
        host="smtp.example.com",
        from_address="sender@example.com",
    )

    assert config.project_name == "demo_project"
    assert config.username == "demo_user"
    assert config.host == "smtp.example.com"
    assert config.port is None
    assert config.use_tls is None
    assert config.project_config_file is None
    assert config.template_path is None


def test_resolve_project_settings_merges_defaults_and_paths(tmp_path: Path):
    app_config = AppSettings(
        working_dir=str(tmp_path / "home"),
        projects_dir=str(tmp_path / "home" / "telegraph_projects"),
        config_dir=str(tmp_path / "home" / ".telegraph"),
        app_config_file=str(
            tmp_path / "home" / ".telegraph" / "telegraph-config.yaml"
        ),
        host="smtp.example.com",
        port=1025,
        use_tls=False,
    )
    project_dir = Path(app_config.projects_dir) / "demo_project"
    project_dir.mkdir(parents=True)

    project_config = ProjectSettings(
        project_name="demo_project",
        username="demo_user",
        from_address="sender@example.com",
        template_path="templates",
    )

    resolved = resolve_project_settings(
        app_config=app_config,
        project_settings=project_config,
    )

    assert isinstance(resolved, ResolvedProjectSettings)
    assert resolved.host == "smtp.example.com"
    assert resolved.port == 1025
    assert resolved.use_tls is False
    assert resolved.template_path == (project_dir / "templates").resolve()
    assert resolved.build_path == (project_dir / "build").resolve()
    assert resolved.data_file == (project_dir / "data.csv").resolve()
