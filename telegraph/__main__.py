"""
Entry point for the Telegraph CLI.

Invokes the main application logic when running:
    python -m telegraph
"""

from telegraph.cli import cli

cli(prog_name="telegraph")
