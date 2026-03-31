"""
Pydantic models for email content.

Includes:
- `Email`: subject, body (plain + HTML), recipients, CC/BCC, reply-to,
attachments.
- `SMTPClient`: Context manager for SMTP connection and sending email content.
- Validation logic for required fields and attachment paths.
"""

from collections.abc import Sequence
from pathlib import Path

from pydantic import BaseModel, EmailStr, Field


class Email(BaseModel):
    """
    Data model for an email message.

    Parameters
    ----------
    subject : str
        Subject of the email.
    body : str
        Plain text body of the email from rendered Jinja template.
    html_body : str | None
        HTML body of the email from rendered Jinja template.
    from_address : EmailStr
        Sender email address.
    to_addresses : Sequence[EmailStr]
        List of recipient email addresses.
    cc : Sequence[EmailStr] | None
        List of CC recipient addresses.
    bcc : Sequence[EmailStr] | None
        List of BCC recipient addresses.
    reply_to : Sequence[EmailStr] | None
        List of Reply-To addresses.
    attachments : Sequence[Path] | None
        List of file paths to attach.
    """

    subject: str = Field(..., description="Subject of the email")
    body: str = Field(
        ..., description="Plain text body of the email from rendered template."
    )
    html_body: str | None = Field(
        default=None,
        description="HTML body of the email from rendered template.",
    )
    from_address: EmailStr = Field(..., description="Sender email address")
    to_addresses: Sequence[EmailStr] = Field(
        ..., description="List of recipient email addresses"
    )
    cc: Sequence[EmailStr] | None = Field(
        default=None, description="List of CC recipient addresses"
    )
    bcc: Sequence[EmailStr] | None = Field(
        default=None, description="List of BCC recipient addresses"
    )
    reply_to: Sequence[EmailStr] | None = Field(
        default=None, description="List of Reply-To addresses"
    )
    attachments: Sequence[Path] | None = Field(
        default=None, description="List of file paths to attach"
    )


EmailContent = Email
