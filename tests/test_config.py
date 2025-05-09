from pathlib import Path

import yaml

from telegraph.config import Settings


def test_smtp_config_yaml_and_env(monkeypatch, tmp_path: Path):
    # write a YAML config file
    smtp_config = {
        "host": "smtp.yaml",
        "port": 1025,
        "username": "yaml_user",
        "password": "yaml_pass",
        "use_tls": False,
        "from_address": "yaml@test.com",
    }
    cfg = {"smtp_config": smtp_config}
    yaml_file = tmp_path / "test_config.yaml"
    yaml_file.write_text(yaml.dump(cfg))

    # point to it, and override one field via env var
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("TELEGRAPH_SMTP_CONFIG_USERNAME", "env_user")

    config = Settings()
    # YAML fills in host/port/password/use_tls
    assert config.smtp_config.host == "smtp.yaml"
    assert config.smtp_config.port == 1025
    assert config.smtp_config.password == "yaml_pass"
    assert config.smtp_config.use_tls is False
    assert config.smtp_config.from_address == "yaml@test.com"
    # environment should override username
    assert config.smtp_config.username == "env_user"

    # ctor kwargs always override
    override = Settings.model_validate(
        {
            "smtp_config": dict(
                host="ctor_host",
                port=999,
                username="ctor_user",
                password="ctor_pass",
                use_tls=True,
                from_address="ctor_from@test.net",
            )
        }
    )
    assert override.smtp_config.host == "ctor_host"
    assert override.smtp_config.port == 999
    assert override.smtp_config.username == "ctor_user"
    assert override.smtp_config.password == "ctor_pass"
    assert override.smtp_config.use_tls is True
    assert override.smtp_config.from_address == "ctor_from@test.net"
