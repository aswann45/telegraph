import html2text


def html_to_plain(html: str) -> str:
    """
    Convert an HTML string to plain-text using html2text.

    Parameters
    ----------
    html : str
        The HTML string to convert to plaintext.

    Returns
    -------
        The converted plaintext string.
    """
    converter = html2text.HTML2Text()
    converter.ignore_images = True  # drop <img> tags
    converter.ignore_links = False  # keep URLs in the output
    converter.body_width = 0  # disable hard wraps

    text = converter.handle(html)
    return text.strip()
