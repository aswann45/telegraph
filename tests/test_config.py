from pathlib import Path

import yaml

from telegraph.config import AppSettings, ProjectSettings


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


def test_project_settings_constructor_and_default_paths():
    config = ProjectSettings(
        project_name="demo_project",
        username="demo_user",
        host="smtp.example.com",
        from_address="sender@example.com",
    )

    assert config.project_name == "demo_project"
    assert config.username == "demo_user"
    assert config.host == "smtp.example.com"
    assert config.port == 587
    assert config.use_tls is True
    assert (
        Path(config.project_config_file).name
        == "telegraph-project-config.yaml"
    )
    assert Path(config.template_path).name == "templates"
    assert "demo_project" in config.project_config_file
    assert "demo_project" in config.template_path
