"""
Template loading and rendering utilities.

Provides:
- Functions to auto-discover templates in a directory.
- Helpers to convert rendered HTML to plain-text when needed.
"""

from pathlib import Path

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


def discover_templates(
    template_dir: Path,
    suffixes: list[str] | None = None,
    recursive: bool = True,
) -> list[str]:
    """
    Discover Jinja template files in a directory.

    Searches for files matching the given suffixes and returns their
    paths relative to the template directory.

    Parameters
    ----------
    template_dir : Path
        Directory in which to search for templates.
    suffixes : list of str, optional
        File extensions to include (including the dot). Defaults to [".j2", ".jinja2"].
    recursive : bool, optional
        Whether to search subdirectories recursively. Defaults to True.

    Returns
    -------
    list of str
        Template paths relative to `template_dir` in POSIX style,
        suitable for passing to Jinja2 `Environment.get_template`.
    """
    if suffixes is None:
        suffixes = [".j2", ".jinja2"]

    # Choose glob method based on recursion flag
    files = template_dir.rglob("*") if recursive else template_dir.glob("*")

    templates: list[str] = []
    for file in files:
        if file.is_file() and file.suffix in suffixes:
            # Compute path relative to template_dir
            relative_path = file.relative_to(template_dir).as_posix()
            templates.append(relative_path)

    return sorted(templates)
