"""
Base classes and functions for mail-merge pipelines.

Defines:
- `PipelineStep`, `Pipeline`, and `Context` abstractions.
- Common utilities for iterating through data records and rendering/sending emails.
"""


import json
from collections.abc import Sequence
from pathlib import Path
from typing import Annotated

import typer
from pydantic import BaseModel, ConfigDict
from rich.progress import track

from telegraph import (
    EmailTemplate,
    Settings,
    SMTPClient,
    TemplateContext,
    TemplateRenderer,
    read_file,
)

# add live addresses to cc and reply to here
CC_ADDRESSES: list[str] = []
REPLY_TO_ADDRESSES: list[str] = []

# add testing addresses to cc and reply to here
TEST_CC_ADDRESSES: list[str] = []
TEST_REPLY_TO_ADDRESSES: list[str] = []

cli = typer.Typer(no_args_is_help=True)

config = Settings()


class Context(BaseModel):
    """
    Class to handle loading context data. Define fields on this
    class to create the correct shape for your template context.
    """

    to_addresses: list[str]

    model_config = ConfigDict(extra="allow")


# try not to edit this or the other cli command functions
@cli.command()
def load_context_data(
    file_name: Annotated[str, typer.Argument()],
    write_to_file: Annotated[bool, typer.Option()] = True,
) -> list[Context]:
    typer.echo("Loading context data...")
    data = _load_context_data(data_filename=file_name, write_to_file=write_to_file)
    typer.echo("Done")
    return data


# try not to edit this or the other cli command functions
@cli.command()
def test_send_emails(
    data_filename: Annotated[str, typer.Argument()],
    test_to_addresses: Annotated[list[str], typer.Argument()],
) -> None:
    _test_send_emails(
        data_filename=data_filename,
        test_to_addresses=test_to_addresses,
        test_cc_addresses=TEST_CC_ADDRESSES,
        test_reply_to_addresses=TEST_REPLY_TO_ADDRESSES,
    )
    typer.echo("Done.")


# try not to edit this or the other cli command functions
@cli.command()
def send_emails(
    data_filename: Annotated[str, typer.Argument()],
) -> None:
    _send_emails(
        data_filename=data_filename,
        cc_addresses=CC_ADDRESSES,
        reply_to_addresses=REPLY_TO_ADDRESSES,
    )
    typer.echo("Done.")


"""
Edit the functions below to suit your needs. The _send_emails 
and _test_send_emails should have most of the boilerplate you'll
need for most circumstances.
"""


def _send_emails(
    data_filename: str,
    cc_addresses: list[str] | None = None,
    reply_to_addresses: list[str] | None = None,
) -> None:
    data = load_context_data(file_name=data_filename)
    template_path = Path(__file__).parent.resolve() / "templates"
    renderer = TemplateRenderer(template_path)
    with SMTPClient(config.smtp_config) as client:
        for d in track(data, description="Sending emails..."):
            context = TemplateContext.model_validate(d.model_dump())

            # include or exclude the html or plaintext templates
            # as your use case requires
            template = EmailTemplate(
                subject_template="subject.txt.j2",
                text_template="body.txt.j2",
                html_template="body.html.j2",
                context=context,
            )
            email_content = template.render(
                renderer=renderer,
                from_address=config.smtp_config.from_address,
                to_addresses=d.to_addresses,
                cc=[i for i in cc_addresses] if cc_addresses else None,
                reply_to=[i for i in reply_to_addresses]
                if reply_to_addresses
                else None,
            )
            client.send_email(email_content)


def _test_send_emails(
    data_filename: str,
    test_to_addresses: Sequence[str],
    test_cc_addresses: Sequence[str] | None = None,
    test_reply_to_addresses: Sequence[str] | None = None,
) -> None:
    data = load_context_data(file_name=data_filename)
    template_path = Path(__file__).parent.resolve() / "templates"
    renderer = TemplateRenderer(template_path)
    with SMTPClient(config.smtp_config) as client:
        for d in track(data, description="Sending test emails..."):
            context = TemplateContext.model_validate(d.model_dump())

            # include or exclude the html or plaintext templates
            # as your use case requires
            template = EmailTemplate(
                subject_template="subject.txt.j2",
                html_template="body.html.j2",
                context=context,
            )
            email_content = template.render(
                renderer=renderer,
                from_address=config.smtp_config.from_address,
                to_addresses=[i for i in test_to_addresses],
                cc=[i for i in test_cc_addresses] if test_cc_addresses else None,
                reply_to=[i for i in test_reply_to_addresses]
                if test_reply_to_addresses
                else None,
            )
            client.send_email(email_content)


def _load_context_data(data_filename: str, write_to_file: bool = True) -> list[Context]:
    project_dir = Path(__file__).parent.resolve()
    file_data = read_file(project_dir / "data" / data_filename)

    out_data = []

    for d in file_data:
        out_data.append(Context.model_validate(d))

    if write_to_file:
        with open((project_dir / "data" / "loaded_context_data.json"), "w") as outfile:
            json.dump([g.model_dump() for g in out_data], outfile, indent=2)

    return out_data


if __name__ == "__main__":
    cli()
