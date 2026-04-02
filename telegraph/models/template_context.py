"""
Template context models for Telegraph.

Provides a flexible context object for Jinja rendering along with email
delivery fields such as recipients and attachments.
"""

from collections.abc import Sequence
from pathlib import Path

from pydantic import BaseModel, ConfigDict, EmailStr


class Context(BaseModel):
    """
    Generic context data for Jinja templates.

    Attributes
    ----------
    subject : str
        Default subject value available to templates and rendered output.
    to_addresses : Sequence[EmailStr]
        Primary email recipients for the rendered message.
    cc : Sequence[EmailStr] | None
        Optional carbon-copy recipients.
    bcc : Sequence[EmailStr] | None
        Optional blind-carbon-copy recipients.
    reply_to : Sequence[EmailStr] | None
        Optional reply-to addresses.
    attachments : Sequence[Path] | None
        Optional file attachments for the rendered message.

    Notes
    -----
    Extra fields are allowed so arbitrary template variables can be supplied
    alongside the built-in email routing fields.
    """

    subject: str = "(no subject)"
    to_addresses: Sequence[EmailStr]
    cc: Sequence[EmailStr] | None = None
    bcc: Sequence[EmailStr] | None = None
    reply_to: Sequence[EmailStr] | None = None
    attachments: Sequence[Path] | None = None

    model_config = ConfigDict(extra="allow")


TemplateContext = Context
