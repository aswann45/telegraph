from collections.abc import Sequence
from pathlib import Path

from pydantic import BaseModel, ConfigDict, EmailStr


class Context(BaseModel):
    """
    Generic context data for Jinja templates.

    Allows arbitrary extra fields for template rendering.
    """

    subject: str = "(no subject)"
    to_addresses: Sequence[EmailStr]
    cc: Sequence[EmailStr] | None = None
    bcc: Sequence[EmailStr] | None = None
    reply_to: Sequence[EmailStr] | None = None
    attachments: Sequence[Path] | None = None

    model_config = ConfigDict(extra="allow")
