"""
Base classes and functions for mail-merge pipelines.

Defines:
- `PipelineStep`, `Pipeline`, and `Context` abstractions.
- Common utilities for iterating through data records and rendering/sending
emails.
"""

import json
from pathlib import Path

import typer
import yaml
from rich.progress import track

from telegraph.config import AppSettings, ProjectSettings
from telegraph.models import Context
from telegraph.smtp_client import SMTPClient
from telegraph.templating import EmailTemplate, TemplateRenderer
from telegraph.util import read_data_file

cli = typer.Typer(no_args_is_help=True)

APP_CONFIG = AppSettings()


def handle_project_config(project_name: str | None = None) -> ProjectSettings:
    """Use global settings for unset project config settings."""
    globals = APP_CONFIG.model_dump(include={"use_tls", "host", "port"})

    if project_name is None:
        conf_file_path = Path().cwd() / "telegraph-project-config.yaml"
    else:
        conf_file_path = (
            Path(APP_CONFIG.projects_dir)
            / project_name
            / "telegraph-project-config.yaml"
        )
    if conf_file_path.exists() is False:
        raise FileNotFoundError(
            "Could not find a config file for this project. "
            "Are you in the right directory or specify an existing project "
            "name?"
        )

    project_conf_dict = yaml.safe_load(conf_file_path.read_text())

    project_conf_dict = project_conf_dict | globals

    project_conf = ProjectSettings(**project_conf_dict)

    return project_conf


def send_emails(
    config: ProjectSettings,
    password: str,
    data_file: Path | None = None,
    limit: int | None = None,
    to_file: bool = False,
) -> None:
    if limit is not None and limit < 1:
        raise ValueError("limit must be at least 1")

    data = load_context_data(
        config=config, write_to_file=False, data_file=data_file
    )

    template_path = Path(config.template_path)
    renderer = TemplateRenderer(template_path)

    if limit is not None:
        limited_data = data[:limit]
    else:
        limited_data = data

    with SMTPClient(config, password) as client:
        # TODO: implement rate limit
        for context in track(limited_data, description="Sending emails..."):
            # TODO: check if html or plaintext templates exist and use if available, otherwise use one or the other
            # handled partially in the `render` function, but could be better implemented
            template = EmailTemplate(
                subject_template=template_path / "subject.txt.j2",
                html_template=template_path / "body.html.j2",
                text_template=template_path / "body.txt.j2",
                context=context,
            )
            email_content = template.render(
                renderer=renderer,
                from_address=config.from_address,
                to_addresses=context.to_addresses,
                cc=context.cc or config.cc,
                bcc=context.bcc or config.bcc,
                reply_to=context.reply_to or config.reply_to,
                attachments=context.attachments or config.attachments,
                to_file=to_file,
            )
            if to_file is False:
                # TODO: optionally show plaintext output in terminal as emails are sent
                # potentially the text of the email
                client.send_email(email_content)


def load_context_data(
    config: ProjectSettings,
    write_to_file: bool = True,
    data_file: Path | None = None,
) -> list[Context]:
    project_dir = Path(config.project_config_file).parent.resolve()

    if data_file is None:
        file_data = read_data_file(project_dir / "data.csv")
    else:
        file_data = read_data_file(data_file)

    out_data: list[Context] = []

    for d in file_data:
        for f in ["cc", "to_addresses", "reply_to", "attachments"]:
            if f in d.keys():
                if isinstance(d[f], list):
                    continue
                else:
                    d[f] = [d[f]]
            else:
                d[f] = getattr(config, f)

        out_data.append(Context.model_validate(d))

    if write_to_file:
        with open((project_dir / "build" / "context.json"), "w") as outfile:
            json.dump(
                [g.model_dump(exclude_none=True) for g in out_data],
                outfile,
                indent=2,
            )

    return out_data


if __name__ == "__main__":
    cli()
