"""
Template handling for Telegraph.

Defines:
- `EmailTemplate`: ties together subject/text/HTML template filenames with
context.
- `TemplateRenderer`: wraps Jinja2 environment setup.
- `render()` methods to produce `EmailContent` from templates.
"""

from __future__ import annotations

import datetime
from collections.abc import Sequence
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from pydantic import BaseModel, EmailStr, Field

from telegraph.models.email import Email
from telegraph.models.template_context import Context
from telegraph.util.template_handling import html_to_plain


class EmailTemplate(BaseModel):
    """
    Defines template filenames and context for rendering an email.

    Parameters
    ----------
    subject_template : str
        Filename of the Jinja template for the email subject.
    text_template : str | None
        Filename of the Jinja template for the plain-text body.
    html_template : str | None
        Filename of the Jinja template for the HTML body.
    context : TemplateContext
        Context data for rendering all templates.
    """

    subject_template: Path = Field(
        ..., description="Jinja template file for the email subject"
    )
    text_template: Path | None = Field(
        default=None, description="Jinja template file for the plain-text body"
    )
    html_template: Path | None = Field(
        default=None, description="Jinja template file for the HTML body"
    )
    context: Context = Field(
        ..., description="Context data for rendering templates"
    )

    @staticmethod
    def _template_exists(
        template_path: Path | None, renderer: TemplateRenderer
    ) -> bool:
        if template_path is None:
            return False
        if template_path.is_absolute():
            return template_path.exists()
        return (renderer.template_dir / template_path).exists()

    def render(
        self,
        renderer: TemplateRenderer,
        from_address: EmailStr,
        to_addresses: Sequence[EmailStr],
        cc: Sequence[EmailStr] | None = None,
        bcc: Sequence[EmailStr] | None = None,
        reply_to: Sequence[EmailStr] | None = None,
        attachments: Sequence[Path] | None = None,
        to_file: bool = False,
    ) -> Email:
        """
        Render subject, body, and optional HTML body into an Email.

        Parameters
        ----------
        renderer : TemplateRenderer
            The Jinja2 renderer instance.
        from_address : str
            Sender email address.
        to_addresses : list[str]
            List of recipient email addresses.
        cc : list[str] | None
            CC recipients.
        bcc : list[str] | None
            BCC recipients.
        reply_to : list[str] | None
            Reply-To addresses.
        attachments : list[Path] | None
            File paths to attach.
        to_file : bool
            Write rendered template to file. Default False.
        """
        subject = renderer.render_template(
            self.subject_template.name, self.context
        )
        body: str
        html_body: str | None = None

        if self.text_template is None and self.html_template is None:
            raise ValueError(
                "Need at least one of text_template or html_template"
            )

        if self._template_exists(self.html_template, renderer):
            html_body = renderer.render_template(
                self.html_template.name,
                self.context,
                to_file,
                extension=".html",
            )
        if self._template_exists(self.text_template, renderer):
            body = renderer.render_template(
                self.text_template.name,
                self.context,
                to_file,
                extension=".txt",
            )
        elif html_body:
            body = html_to_plain(html_body)

        return Email(
            subject=subject,
            body=body,
            html_body=html_body,
            from_address=from_address,
            to_addresses=to_addresses,
            cc=cc,
            bcc=bcc,
            reply_to=reply_to,
            attachments=attachments,
        )


class TemplateRenderer:
    """
    Renders Jinja templates from a given directory.

    Parameters
    ----------
    template_dir : Path
        Directory containing Jinja template files.
    """

    def __init__(self, template_dir: Path) -> None:
        self.template_dir = template_dir
        self.env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=select_autoescape(["html", "xml"]),
        )

    def render_template(
        self,
        template_name: str,
        context: Context,
        to_file: bool = False,
        extension: str | None = None,
    ) -> str:
        """
        Render a single Jinja template with the provided context.

        Parameters
        ----------
        template_name : str
            Filename of the template to render.
        context : TemplateContext
            Data context for rendering.
        to_file : bool
            Write rendered template to file. Default False.

        Returns
        -------
        str
            The rendered template string.
        """
        template = self.env.get_template(template_name)
        rendered_template = template.render(**context.model_dump())
        if to_file is True:
            if extension is None:
                raise ValueError(
                    "Must specify file extension when rendering to file."
                )
            build_dir: Path = self.template_dir.parent / "build"
            build_dir.mkdir(exist_ok=True)
            file_name = (
                context.subject
                + "_"
                + str(datetime.datetime.now(tz=datetime.UTC))
                + extension
            )
            with open(build_dir / file_name, "w") as outfile:
                outfile.write(rendered_template)
        return rendered_template


TemplateContext = Context

__all__ = ["EmailTemplate", "TemplateContext", "TemplateRenderer"]
