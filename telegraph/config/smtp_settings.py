from pydantic_settings import BaseSettings, SettingsConfigDict


class SMTPConfig(BaseSettings):
    """
    Configuration for the SMTP server connection, supporting environment variables
    and YAML file loading via a classmethod customisation.

    Parameters
    ----------
    host : str
        SMTP server hostname.
    port : int
        SMTP server port.
    username : str
        Username for SMTP authentication.
    password : str
        Password for SMTP authentication.
    use_tls : bool
        Flag to use TLS (default is True).
    """

    host: str = "changethis"
    port: int = 587
    username: str = "changethis"
    password: str = "changethis"
    use_tls: bool = True
    from_address: str = "changethis"

    model_config = SettingsConfigDict(
        extra="ignore",
    )
