"""
Utility functions and base classes for Telegraph.

Provides:
- File I/O helpers.
- Pipeline base classes for mail-merge workflows.
- Template discovery and rendering utilities.
"""

from .app_setup import initial_setup, new_project_setup
from .file_handling import read_file

__all__ = [
    "initial_setup",
    "new_project_setup",
    "read_file",
]
