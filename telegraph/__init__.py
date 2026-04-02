"""
Telegraph — a lightweight Jinja2-based email templating and sending library.

The top-level package re-exports the main public models, config helpers,
template utilities, and setup functions used by Telegraph applications and
CLI workflows.
"""

from .config import (
    AppSettings,
    ProjectSettings,
    ResolvedProjectSettings,
    resolve_project_settings,
)
from .models import (
    Context,
    Email,
    EmailContent,
    TemplateContext,
)
from .smtp_client import SMTPClient
from .templating import EmailTemplate, TemplateRenderer
from .util import (
    app_setup,
    new_project_setup,
    read_data_file,
)

initial_setup = app_setup

__all__ = [
    "Email",
    "EmailContent",
    "EmailTemplate",
    "AppSettings",
    "ProjectSettings",
    "ResolvedProjectSettings",
    "SMTPClient",
    "Context",
    "TemplateContext",
    "TemplateRenderer",
    "initial_setup",
    "app_setup",
    "new_project_setup",
    "read_data_file",
    "resolve_project_settings",
]
