"""
Email and templating models for Telegraph.

Defines:
- Data structures for email content (subject, body, recipients, attachments).
- Template context models supporting arbitrary extra fields.
- Factory methods to render models into EmailContent instances.
"""


from .emails import EmailContent, SMTPClient
from .templating import EmailTemplate, TemplateContext, TemplateRenderer

__all__ = [
    "EmailContent",
    "EmailTemplate",
    "SMTPClient",
    "TemplateContext",
    "TemplateRenderer",
]
