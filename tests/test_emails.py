import smtplib
from pathlib import Path
from typing import Any

from telegraph.config import Settings
from telegraph.models.emails import (
    EmailContent,
    EmailMessage,
    SMTPClient,
    # SMTPConfig,
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

    def ehlo(self):
        self.ehlo_called = True

    def starttls(self, context=None):
        self.tls_started = True

    def login(self, username, password):
        self.logged_in = True

    def send_message(self, msg, from_addr, to_addrs):
        self.messages.append((msg, from_addr, to_addrs))

    def quit(self):
        self.quitted = True


def test_smtp_client_connect_send_and_disconnect(monkeypatch):
    # replace smtplib.SMTP with our dummy
    monkeypatch.setattr(smtplib, "SMTP", DummySMTP)

    smtp_cfg = dict(
        host="smtp.example.com",
        port=587,
        username="user",
        password="pass",
        use_tls=True,
        from_address="test@test.com",
    )
    cfg = Settings(smtp_config=smtp_cfg)
    with SMTPClient(cfg.smtp_config) as client:
        server = client._server
        assert isinstance(server, DummySMTP)
        assert server.ehlo_called
        assert server.tls_started
        assert server.logged_in

        # build a minimal EmailContent
        content = EmailContent(
            subject="Test",
            body="Test body",
            html_body=None,
            from_address=cfg.smtp_config.from_address,
            to_addresses=["to1@e.com"],
            cc=[],
            bcc=[],
            reply_to=None,
            attachments=[],
        )
        client.send_email(content)
        assert len(server.messages) == 1
        _, faddr, taddrs = server.messages[0]
        assert faddr == "test@test.com"
        assert "to1@e.com" in taddrs

        # client.disconnect()
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

    def ehlo(self):
        pass

    def starttls(self, context=None):
        self.tls_started = True

    def login(self, username, password):
        self.logged_in = True

    def send_message(self, msg: EmailMessage, from_addr: str, to_addrs: list[str]):
        self.sent_messages.append((msg, from_addr, to_addrs))

    def quit(self):
        self.quit_called = True


def test_attachment_handling(monkeypatch, tmp_path: Path):
    # Prepare dummy file
    file_path = tmp_path / "report.txt"
    file_path.write_text("Quarterly revenue report goes here.")

    # Monkeypatch the SMTP class
    dummy_instance = DummySMTPWithAttachmentCapture("ignored", 0)
    monkeypatch.setattr(smtplib, "SMTP", lambda host, port: dummy_instance)

    smtp_config = dict(
        host="smtp.test.com",
        port=587,
        username="test_user",
        password="test_pass",
        use_tls=True,
    )
    config = Settings.model_validate({"smtp_config": smtp_config})

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

    client = SMTPClient(config.smtp_config)
    client.connect()
    assert isinstance(client._server, DummySMTPWithAttachmentCapture)

    client.send_email(email)
    server = client._server
    assert server is not None
    assert len(server.sent_messages) == 1

    message, from_addr, to_addrs = server.sent_messages[0]
    assert from_addr == "sender@example.com"
    assert "recipient@example.com" in to_addrs

    # Verify attachment presence in MIME structure
    attachment_found = False
    for part in message.iter_attachments():
        if part.get_filename() == "report.txt":
            attachment_found = True
            assert part.get_content_type() == "text/plain"
            assert (
                part.get_payload(decode=True) == b"Quarterly revenue report goes here."
            )

    assert attachment_found, "Expected attachment was not found"

    client.disconnect()
    assert server.quit_called
