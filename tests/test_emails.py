import smtplib
from email.message import EmailMessage
from pathlib import Path
from typing import Any

from telegraph.config import (
    AppSettings,
    ProjectSettings,
    resolve_project_settings,
)
from telegraph.models.email import EmailContent
from telegraph.smtp_client import SMTPClient


def make_runtime_config(tmp_path: Path):
    app_config = AppSettings(
        working_dir=str(tmp_path),
        projects_dir=str(tmp_path / "telegraph_projects"),
        config_dir=str(tmp_path / ".telegraph"),
        app_config_file=str(tmp_path / ".telegraph" / "telegraph-config.yaml"),
        host="smtp.example.com",
        port=587,
        use_tls=True,
    )
    project_dir = Path(app_config.projects_dir) / "demo_project"
    project_dir.mkdir(parents=True, exist_ok=True)
    return resolve_project_settings(
        app_config=app_config,
        project_settings=ProjectSettings(
            project_name="demo_project",
            username="user",
            from_address="test@test.com",
        ),
    )


class DummySMTP:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.ehlo_called = False
        self.tls_started = False
        self.logged_in = False
        self.messages: list[Any] = []
        self.quitted = False

    def ehlo(self) -> None:
        self.ehlo_called = True

    def starttls(self, context: Any | None = None) -> None:
        self.tls_started = True

    def login(self, username: Any, password: Any) -> None:
        self.logged_in = True

    def send_message(self, msg: Any, from_addr: Any, to_addrs: Any) -> None:
        self.messages.append((msg, from_addr, to_addrs))

    def quit(self) -> None:
        self.quitted = True


def test_smtp_client_connect_send_and_disconnect(
    monkeypatch: Any, tmp_path: Path
) -> None:
    monkeypatch.setattr(smtplib, "SMTP", DummySMTP)

    config = make_runtime_config(tmp_path)

    with SMTPClient(config, password="pass") as client:
        server = client._server
        assert isinstance(server, DummySMTP)
        assert server.ehlo_called
        assert server.tls_started
        assert server.logged_in

        content = EmailContent(
            subject="Test",
            body="Test body",
            html_body=None,
            from_address=config.from_address,
            to_addresses=["to1@e.com"],
            cc=[],
            bcc=[],
            reply_to=None,
            attachments=[],
        )
        client.send_email(content)
        assert len(server.messages) == 1
        message, from_addr, to_addrs = server.messages[0]
        assert from_addr == "test@test.com"
        assert "to1@e.com" in to_addrs
        assert "Bcc" not in message

    assert server.quitted
    assert client._server is None


class DummySMTPWithAttachmentCapture:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.sent_messages: list[Any] = []
        self.logged_in = False
        self.tls_started = False
        self.quit_called = False

    def ehlo(self) -> None:
        pass

    def starttls(self, context: Any | None = None) -> None:
        self.tls_started = True

    def login(self, username: Any, password: Any) -> None:
        self.logged_in = True

    def send_message(
        self, msg: EmailMessage, from_addr: str, to_addrs: list[str]
    ) -> None:
        self.sent_messages.append((msg, from_addr, to_addrs))

    def quit(self) -> None:
        self.quit_called = True


def test_attachment_handling(monkeypatch: Any, tmp_path: Path) -> None:
    file_path = tmp_path / "report.txt"
    file_path.write_text("Quarterly revenue report goes here.")

    dummy_instance = DummySMTPWithAttachmentCapture("ignored", 0)
    monkeypatch.setattr(smtplib, "SMTP", lambda host, port: dummy_instance)

    app_config = AppSettings(
        working_dir=str(tmp_path),
        projects_dir=str(tmp_path / "telegraph_projects"),
        config_dir=str(tmp_path / ".telegraph"),
        app_config_file=str(tmp_path / ".telegraph" / "telegraph-config.yaml"),
        host="smtp.test.com",
        port=587,
        use_tls=True,
    )
    project_dir = Path(app_config.projects_dir) / "demo_project"
    project_dir.mkdir(parents=True, exist_ok=True)
    config = resolve_project_settings(
        app_config=app_config,
        project_settings=ProjectSettings(
            project_name="demo_project",
            username="test_user",
            from_address="sender@example.com",
        ),
    )

    email = EmailContent(
        subject="Financial Report",
        body="See the attached report.",
        html_body="<p>See the attached report.</p>",
        from_address="sender@example.com",
        to_addresses=["recipient@example.com"],
        cc=[],
        bcc=[],
        reply_to=None,
        attachments=[file_path],
    )

    client = SMTPClient(config, password="test_pass")
    client.connect(password="test_pass")
    assert isinstance(client._server, DummySMTPWithAttachmentCapture)

    client.send_email(email)
    server = client._server
    assert server is not None
    assert len(server.sent_messages) == 1

    message, from_addr, to_addrs = server.sent_messages[0]
    assert from_addr == "sender@example.com"
    assert "recipient@example.com" in to_addrs

    attachment_found = False
    for part in message.iter_attachments():
        if part.get_filename() == "report.txt":
            attachment_found = True
            assert part.get_content_type() == "text/plain"
            assert (
                part.get_payload(decode=True)
                == b"Quarterly revenue report goes here."
            )

    assert attachment_found, "Expected attachment was not found"

    client.disconnect()
    assert server.quit_called
