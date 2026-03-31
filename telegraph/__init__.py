"""
Telegraph — a lightweight Jinja2-based email templating and sending library.

This package provides:
- Pydantic models to define email content and configuration.
- Utilities for loading/rendering Jinja templates.
- An SMTP client for sending messages.
- A CLI for mail-merge workflows.
"""

from .config import AppSettings, ProjectSettings
from .models import (
    Context,
    Email,
)
from .smtp_client import SMTPClient
from .templating import EmailTemplate, TemplateRenderer
from .util import (
    app_setup,
    new_project_setup,
    read_data_file,
)

__all__ = [
    "Email",
    "EmailTemplate",
    "AppSettings",
    "ProjectSettings",
    "SMTPClient",
    "Context",
    "TemplateRenderer",
    "initial_setup",
    "new_project_setup",
    "read_data_file",
    "app_setup",
]
