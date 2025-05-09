"""
Entry point for the Telegraph CLI from Poetry.

Invokes the main application logic when running:
    telegraph
"""

from telegraph.cli import cli

cli()

if __name__ == "__main__":
    cli()
