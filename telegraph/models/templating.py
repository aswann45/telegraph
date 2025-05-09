from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from pydantic import BaseModel, ConfigDict, Field

from telegraph.models.emails import EmailContent
from telegraph.util.template_handling import html_to_plain


class TemplateContext(BaseModel):
    """
    Generic context data for Jinja templates.

    Allows arbitrary extra fields for template rendering.
    """

    model_config = ConfigDict(extra="allow")


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

    subject_template: str = Field(
        ..., description="Jinja template file for the email subject"
    )
    text_template: str | None = Field(
        default=None, description="Jinja template file for the plain-text body"
    )
    html_template: str | None = Field(
        default=None, description="Jinja template file for the HTML body"
    )
    context: TemplateContext = Field(
        ..., description="Context data for rendering templates"
    )

    def render(
        self,
        renderer: TemplateRenderer,
        from_address: str,
        to_addresses: list[str],
        cc: Sequence[str] | None = None,
        bcc: Sequence[str] | None = None,
        reply_to: Sequence[str] | None = None,
        attachments: Sequence[Path] | None = None,
    ) -> EmailContent:
        """
        Render subject, body, and optional HTML body into an EmailContent.

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
        """
        subject = renderer.render_template(self.subject_template, self.context)
        body: str
        html_body: str | None = None

        if self.text_template is None and self.html_template is None:
            raise ValueError("Need at least one of text_template or html_template")

        if self.html_template:
            html_body = renderer.render_template(self.html_template, self.context)
            body = html_to_plain(html_body)
        if self.text_template:
            body = renderer.render_template(self.text_template, self.context)

        return EmailContent(
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
        self.env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=select_autoescape(["html", "xml"]),
        )

    def render_template(self, template_name: str, context: TemplateContext) -> str:
        """
        Render a single Jinja template with the provided context.

        Parameters
        ----------
        template_name : str
            Filename of the template to render.
        context : TemplateContext
            Data context for rendering.

        Returns
        -------
        str
            The rendered template string.
        """
        template = self.env.get_template(template_name)
        return template.render(**context.model_dump())
