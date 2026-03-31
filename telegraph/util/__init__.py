"""
Utility functions and base classes for Telegraph.

Provides:
- File I/O helpers.
- Pipeline base classes for mail-merge workflows.
- Template discovery and rendering utilities.
"""

from .app_setup import app_setup, new_project_setup
from .file_handling import read_data_file

__all__ = [
    "app_setup",
    "new_project_setup",
    "read_data_file",
]
