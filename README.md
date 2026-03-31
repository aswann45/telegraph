Telegraph
================

Telegraph is a small Python package for generating and sending templated emails. It is designed for mail-merge style workflows that need structured context data, Jinja templates, and SMTP features like cc, bcc, reply-to, and attachments.

## Features
- Supports multiple file formats for data input (CSV, JSON, XLSX, YAML)
- Uses Jinja2 templating engine for customizable email templates
- Includes a command-line interface (CLI) for easy setup and usage
- Allows for arbitrary extra fields for template 
rendering

## Installation
To install Telegraph from PyPI:

```bash
pip install telegraph-emails
telegraph init
```

From source in this repo, use the local virtualenv or install the package into one:

```bash
.venv/bin/python -m telegraph --help
```

Running `telegraph init` creates:

- `$HOME/.telegraph/telegraph-config.yaml`
- `$HOME/telegraph_projects/`

The global config file is intentionally created with placeholder values, so you will need to edit it before sending real email.

## Usage

### Models
The main public models are available from the package root.

`Context`, `EmailTemplate`, and `TemplateRenderer` handle template rendering:

```python
from pathlib import Path
from telegraph import Context, EmailTemplate, TemplateRenderer

renderer = TemplateRenderer(Path("path/to/templates"))

ctx = Context.model_validate(
    {
        "subject": "Hello",
        "to_addresses": ["you@example.com"],
        "msg": "Hello!",
    }
)

tpl = EmailTemplate(
    subject_template="subject.txt.j2",
    text_template="body.txt.j2",
    html_template="body.html.j2",
    context=ctx,
)

email = tpl.render(
    renderer=renderer,
    from_address="me@example.com",
    to_addresses=ctx.to_addresses,
)
```

`SMTPClient` sends the rendered `Email`:

```python
from telegraph import ProjectSettings, SMTPClient

config = ProjectSettings(
    project_name="demo_project",
    username="smtp-user",
    host="smtp.example.com",
    from_address="me@example.com",
)

with SMTPClient(config, password="secret") as client:
    client.send_email(email)

```

For compatibility with older code, `TemplateContext` and `EmailContent` are still available as aliases for `Context` and `Email`.

### Setting up a new project
To scaffold a project workspace:

```bash
telegraph new-project <project_name>
```

This creates a directory at `$HOME/telegraph_projects/<project_name>` with:

- `telegraph-project-config.yaml`
- `templates/subject.txt.j2`
- `templates/body.txt.j2`
- `templates/body.html.j2`
- `build/`

Put your source data in that project directory. The current workflow expects `data.csv` by default, or you can pass `--file-name` to `load-context-data` or `send`.

### Rendering templates
Telegraph uses Jinja2 templates for the subject and body.

Each project starts with three template files in `templates/`. You need a subject template and at least one body template. If only an HTML body exists, Telegraph will derive a plain-text version automatically when rendering.

### CLI workflow
The current CLI flow is:

```bash
.venv/bin/telegraph init
.venv/bin/telegraph new-project my_project
.venv/bin/telegraph --project my_project load-context-data
.venv/bin/telegraph --project my_project send --password '...'
```

Useful notes:

- `load-context-data` reads project data and writes `build/context.json`
- `send` renders messages and either writes output files or sends through SMTP
- `send --limit N` processes the first `N` rows
- `python -m telegraph --help` shows the current commands

### Configuration
Telegraph uses two related configuration models:

- `AppSettings` for global defaults such as the projects directory and default SMTP host/port
- `ProjectSettings` for per-project settings such as username, sender address, template path, and optional defaults for cc/bcc/reply-to/attachments

The generated YAML files are placeholders by default, so you will need to replace values like `host`, `username`, and `from_address` before sending real mail.

## Contributing
Contributions to Telegraph are welcome. Please submit a pull request with your changes.

## License
Telegraph is licensed under the MIT License.
