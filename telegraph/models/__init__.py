"""
Email and templating models for Telegraph.

Defines:
- Data structures for email content (subject, body, recipients, attachments).
- Template context models supporting arbitrary extra fields.
- Factory methods to render models into EmailContent instances.
"""

from .email import Email, EmailContent
from .template_context import Context, TemplateContext

__all__ = [
    "Email",
    "EmailContent",
    "Context",
    "TemplateContext",
]
