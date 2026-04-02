"""
Entry point for the Telegraph CLI from Poetry.

Invokes the `telegraph` command-line interface when the installed console
script entrypoint is executed.
"""

from telegraph.cli import cli

cli()

if __name__ == "__main__":
    cli()
