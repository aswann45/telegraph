"""
Entry point for the Telegraph CLI.

Invokes the Telegraph command-line interface when the package is executed with
`python -m telegraph`.
"""

from telegraph.cli import cli

cli(prog_name="telegraph")
