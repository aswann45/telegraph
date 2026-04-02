from pathlib import Path

import pytest

from telegraph.config import (
    AppSettings,
    ProjectSettings,
    ResolvedProjectSettings,
    resolve_project_settings,
)
from telegraph.models import Context, Email
from telegraph.service import send_emails


class DummySMTPClient:
    sent: list[Email]

    def __init__(self, config: ResolvedProjectSettings, password: str):
        self.config = config
        self.password = password
        self.sent = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return None

    def send_email(self, email: Email) -> None:
        self.sent.append(email)


class DummyTemplateRenderer:
    def __init__(self, template_dir: Path):
        self.template_dir = template_dir


class DummyEmailTemplate:
    rendered_contexts: list[Context] = []

    def __init__(
        self,
        *,
        subject_template: Path,
        html_template: Path,
        text_template: Path,
        context: Context,
    ):
        self.context = context

    def render(
        self,
        *,
        renderer: DummyTemplateRenderer,
        from_address: str,
        to_addresses: list[str],
        cc=None,
        bcc=None,
        reply_to=None,
        attachments=None,
        to_file: bool = False,
    ) -> Email:
        self.__class__.rendered_contexts.append(self.context)
        return Email(
            subject=self.context.subject,
            body=f"body for {self.context.subject}",
            html_body=None,
            from_address=from_address,
            to_addresses=to_addresses,
            cc=cc,
            bcc=bcc,
            reply_to=reply_to,
            attachments=attachments,
        )


def make_runtime_config(tmp_path: Path) -> ResolvedProjectSettings:
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
            username="demo_user",
            from_address="sender@example.com",
        ),
    )


def test_send_emails_limit_sends_first_n(monkeypatch, tmp_path: Path):
    """send_emails should process only the first N contexts when limited."""
    config = make_runtime_config(tmp_path)
    contexts = [
        Context(subject="one", to_addresses=["one@example.com"]),
        Context(subject="two", to_addresses=["two@example.com"]),
        Context(subject="three", to_addresses=["three@example.com"]),
    ]
    smtp_client = DummySMTPClient(config, password="secret")

    monkeypatch.setattr(
        "telegraph.service.load_context_data",
        lambda **kwargs: contexts,
    )
    monkeypatch.setattr(
        "telegraph.service.TemplateRenderer", DummyTemplateRenderer
    )
    monkeypatch.setattr("telegraph.service.EmailTemplate", DummyEmailTemplate)
    monkeypatch.setattr(
        "telegraph.service.SMTPClient",
        lambda config, password: smtp_client,
    )
    DummyEmailTemplate.rendered_contexts = []

    send_emails(config=config, password="secret", limit=2)

    assert [email.subject for email in smtp_client.sent] == ["one", "two"]
    assert [
        context.subject for context in DummyEmailTemplate.rendered_contexts
    ] == ["one", "two"]


def test_send_emails_rejects_non_positive_limit(tmp_path: Path):
    """send_emails should reject zero or negative limits."""
    config = make_runtime_config(tmp_path)

    with pytest.raises(ValueError, match="limit must be at least 1"):
        send_emails(config=config, password="secret", limit=0)
