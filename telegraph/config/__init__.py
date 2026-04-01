"""
Configuration subpackage for Telegraph.

Contains Pydantic settings models for application-wide and SMTP configuration,
with support for environment variables, YAML files, and .env loading.
"""

from .app_settings import AppSettings
from .project_settings import (
    ProjectSettings,
    ResolvedProjectSettings,
    get_project_config_path,
    load_project_settings,
    resolve_project_settings,
)

__all__ = [
    "AppSettings",
    "ProjectSettings",
    "ResolvedProjectSettings",
    "get_project_config_path",
    "load_project_settings",
    "resolve_project_settings",
]
