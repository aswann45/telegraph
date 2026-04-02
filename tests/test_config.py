from pathlib import Path

import json

import yaml
import pytest

from telegraph.config import (
    AppSettings,
    get_project_config_path,
    load_project_settings,
    ProjectSettings,
    ResolvedProjectSettings,
    resolve_project_settings,
)


def test_app_settings_yaml_and_env(monkeypatch, tmp_path: Path):
    """Environment variables should override YAML-backed app settings."""
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
    """ProjectSettings should keep runtime defaults unset until resolution."""
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
    """Resolved settings should merge app defaults and derived paths."""
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


def test_get_project_config_path_uses_cwd_when_project_is_omitted(
    monkeypatch, tmp_path: Path
):
    """Project config lookup should fall back to the current directory."""
    monkeypatch.chdir(tmp_path)

    path = get_project_config_path()

    assert path == (tmp_path / "telegraph-project-config.yaml").resolve()


def test_load_project_settings_raises_for_missing_file(tmp_path: Path):
    """Missing project config files should raise FileNotFoundError."""
    app_config = AppSettings(
        working_dir=str(tmp_path / "home"),
        projects_dir=str(tmp_path / "home" / "telegraph_projects"),
        config_dir=str(tmp_path / "home" / ".telegraph"),
        app_config_file=str(
            tmp_path / "home" / ".telegraph" / "telegraph-config.yaml"
        ),
    )

    with pytest.raises(FileNotFoundError, match="Could not find a config file"):
        load_project_settings("missing_project", app_config=app_config)


def test_load_project_settings_rejects_non_mapping_yaml_root(tmp_path: Path):
    """Project config YAML roots must be mappings."""
    app_config = AppSettings(
        working_dir=str(tmp_path / "home"),
        projects_dir=str(tmp_path / "home" / "telegraph_projects"),
        config_dir=str(tmp_path / "home" / ".telegraph"),
        app_config_file=str(
            tmp_path / "home" / ".telegraph" / "telegraph-config.yaml"
        ),
    )
    project_dir = Path(app_config.projects_dir) / "demo_project"
    project_dir.mkdir(parents=True)
    (project_dir / "telegraph-project-config.yaml").write_text(
        yaml.dump(["not", "a", "mapping"])
    )

    with pytest.raises(ValueError, match="Project config must contain a YAML mapping"):
        load_project_settings("demo_project", app_config=app_config)


def test_load_project_settings_uses_cwd_when_project_is_omitted(
    monkeypatch, tmp_path: Path
):
    """Project settings should load from cwd when no project name is given."""
    monkeypatch.chdir(tmp_path)
    config_path = tmp_path / "telegraph-project-config.yaml"
    config_path.write_text(
        yaml.dump(
            {
                "project_name": "cwd_project",
                "username": "demo_user",
                "from_address": "sender@example.com",
            }
        )
    )

    config = load_project_settings()

    assert config.project_name == "cwd_project"
    assert config.project_config_file == str(config_path.resolve())


def test_resolve_project_settings_respects_absolute_paths(tmp_path: Path):
    """Absolute custom paths should be preserved during resolution."""
    app_config = AppSettings(
        working_dir=str(tmp_path / "home"),
        projects_dir=str(tmp_path / "home" / "telegraph_projects"),
        config_dir=str(tmp_path / "home" / ".telegraph"),
        app_config_file=str(
            tmp_path / "home" / ".telegraph" / "telegraph-config.yaml"
        ),
        host="smtp.example.com",
        port=587,
        use_tls=True,
    )
    project_dir = Path(app_config.projects_dir) / "demo_project"
    project_dir.mkdir(parents=True)

    template_dir = tmp_path / "absolute_templates"
    build_dir = tmp_path / "absolute_build"
    data_file = tmp_path / "absolute_data.json"
    template_dir.mkdir()
    build_dir.mkdir()
    data_file.write_text(json.dumps([{"name": "Alice"}]))

    resolved = resolve_project_settings(
        app_config=app_config,
        project_settings=ProjectSettings(
            project_name="demo_project",
            username="demo_user",
            from_address="sender@example.com",
            template_path=str(template_dir),
            build_path=str(build_dir),
            data_file=str(data_file),
        ),
    )

    assert resolved.template_path == template_dir.resolve()
    assert resolved.build_path == build_dir.resolve()
    assert resolved.data_file == data_file.resolve()
