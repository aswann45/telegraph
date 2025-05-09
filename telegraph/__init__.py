"""
Telegraph — a lightweight Jinja2-based email templating and sending library.

This package provides:
- Pydantic models to define email content and configuration.
- Utilities for loading/rendering Jinja templates.
- An SMTP client for sending messages.
- A CLI for mail-merge workflows.
"""


from .config import Settings
from .models import (
    EmailContent,
    EmailTemplate,
    SMTPClient,
    TemplateContext,
    TemplateRenderer,
)
from .util import (
    initial_setup,
    new_project_setup,
    read_file,
)

__all__ = [
    "EmailContent",
    "EmailTemplate",
    "Settings",
    "SMTPClient",
    "TemplateContext",
    "TemplateRenderer",
    "initial_setup",
    "new_project_setup",
    "read_file",
]
