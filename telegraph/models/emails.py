import mimetypes
import smtplib
import ssl
from collections.abc import Sequence
from email.message import EmailMessage
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from telegraph.config.smtp_settings import SMTPConfig


class EmailContent(BaseModel):
    """
    Data model for an email message.

    Parameters
    ----------
    subject : str
        Subject of the email.
    body : str
        Plain text body of the email.
    html_body : str | None
        HTML body of the email.
    from_address : str
        Sender email address.
    to_addresses : Sequence[str]
        List of recipient email addresses.
    cc : Sequence[str] | None
        List of CC recipient addresses.
    bcc : Sequence[str] | None
        List of BCC recipient addresses.
    reply_to : Sequence[str] | None
        List of Reply-To addresses.
    attachments : Sequence[Path] | None
        List of file paths to attach.
    """

    subject: str = Field(..., description="Subject of the email")
    body: str = Field(..., description="Plain text body of the email")
    html_body: str | None = Field(default=None, description="HTML body of the email")
    from_address: str = Field(..., description="Sender email address")
    to_addresses: Sequence[str] = Field(
        ..., description="List of recipient email addresses"
    )
    cc: Sequence[str] | None = Field(
        default=None, description="List of CC recipient addresses"
    )
    bcc: Sequence[str] | None = Field(
        default=None, description="List of BCC recipient addresses"
    )
    reply_to: Sequence[str] | None = Field(
        default=None, description="List of Reply-To addresses"
    )
    attachments: Sequence[Path] | None = Field(
        default=None, description="List of file paths to attach"
    )


class SMTPClient:
    """
    SMTP client for sending emails.

    Methods
    -------
    connect()
        Establishes connection and logs in.
    send_email(email: EmailContent)
        Sends an email using the established connection.
    disconnect()
        Closes the SMTP connection.
    """

    def __init__(self, config: SMTPConfig) -> None:
        """
        Initialize the SMTP client with given configuration.

        Parameters
        ----------
        config : SMTPConfig
            The SMTP server configuration.
        """
        self.config = config
        self._server: smtplib.SMTP | None = None

    def __enter__(self) -> "SMTPClient":
        """
        Enter the runtime context related to the SMTP connection.

        Returns
        -------
        SMTPClient
            The connected SMTP client instance.
        """
        self.connect()
        return self

    def __exit__(
        self,
        exc_type: type | None,
        exc_val: BaseException | None,
        exc_tb: Any | None,
    ) -> None:
        """
        Exit the runtime context and close the SMTP connection.
        """
        self.disconnect()

    def connect(self) -> None:
        """
        Establish a connection to the SMTP server and login if credentials are provided.
        Uses a secure SSL context for TLS if enabled.

        Raises
        ------
        smtplib.SMTPException
            If connection or login fails.
        """
        server = smtplib.SMTP(self.config.host, self.config.port)
        server.ehlo()
        if self.config.use_tls:
            context = ssl.create_default_context()
            server.starttls(context=context)
            server.ehlo()
        server.login(self.config.username, self.config.password)
        self._server = server

    def send_email(self, email: EmailContent) -> None:
        """
        Send an email message using the SMTP connection.

        Parameters
        ----------
        email : EmailContent
            The email content and recipients.

        Raises
        ------
        smtplib.SMTPException
            If sending the email fails or if the server is not connected.
        """
        if self._server is None:
            raise smtplib.SMTPException("SMTP server is not connected.")

        msg = EmailMessage()
        msg["Subject"] = email.subject
        msg["From"] = email.from_address
        msg["To"] = ", ".join(email.to_addresses)
        if email.cc:
            msg["Cc"] = ", ".join(email.cc)
        if email.bcc:
            msg["Bcc"] = ", ".join(email.bcc)
        if email.reply_to:
            msg["Reply-To"] = ", ".join(email.reply_to)

        # Set plain and HTML body
        msg.set_content(email.body)
        if email.html_body:
            msg.add_alternative(email.html_body, subtype="html")

        # Attach files
        if email.attachments:
            for path in email.attachments:
                content_type, _ = mimetypes.guess_type(path)
                maintype, subtype = (
                    content_type.split("/")
                    if content_type
                    else ("application", "octet-stream")
                )
                with open(path, "rb") as f:
                    data = f.read()
                msg.add_attachment(
                    data, maintype=maintype, subtype=subtype, filename=path.name
                )

        recipients: list[str] = (
            [e for e in email.to_addresses]
            + ([e for e in email.cc or []])
            + ([e for e in email.bcc or []])
        )
        self._server.send_message(
            msg, from_addr=email.from_address, to_addrs=recipients
        )

    def disconnect(self) -> None:
        """
        Close the SMTP connection.

        Raises
        ------
        smtplib.SMTPException
            If closing the connection fails.
        """
        if self._server is not None:
            self._server.quit()
            self._server = None
