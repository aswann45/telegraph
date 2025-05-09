Telegraph
================

Telegraph is a small Python package for generating and sending emails using templates. I created it so that I could handle more complicated mail merge projects than Outlook or Gmail can usually handle, particularly cc/bcc/reply-to settings and attachments. 

## Features
- Supports multiple file formats for data input (CSV, JSON, XLSX, YAML)
- Uses Jinja2 templating engine for customizable email templates
- Includes a command-line interface (CLI) for easy setup and usage
- Allows for arbitrary extra fields for template 
rendering

## Installation
To install Telegraph from PyPi, run the following commands:

```bash
pip install telegraph
telegraph init
```
Or from source:
```bash
git clone https://github.com/aswann45/telegraph.git
cd telegraph
scripts/install
telegraph init
```

This will create a couple of directories in your $HOME folder, including `.telegraph` and `telegraph_projects`. It will also create a `yaml` default configuratioan file in the project's root directory, where ever you installed it. To set your own configuration, copy that file (named `telegraph-default-config.yaml`) to `$HOME/.telegraph/telegraph-config.yaml` and edit away.

The `telegraph_projects` directory is where you'll work with your emailing projects and is explained in more detail below. 

## Usage

### Models
`telegraph` is built around several `pydantic` models that handle all data transformations, and are available as imports from the root package. The key models are:



**EmailTemplate**, **TemplateContext** and **TemplateRenderer**:
```python
from pathlib import Path
from telegraph import EmailTemplate, TemplateContext, TemplateRenderer

renderer = TemplateRenderer(Path("path/to/templates"))

ctx = TemplateContext.model_validate({"msg": "Hello!"}),

tpl = EmailTemplate(
    subject_template="subject.txt.j2",
    text_template="body.txt.j2",
    html_template="body.htmt.j2",
    context=ctx,
)

email_content = tpl.render(
    renderer=renderer,
    from_address="me@example.com",
    to_addresses=["you@example.com"],
)
```

and **SMTPClient**:
```python
from telegraph import Settings, SMTPClient

config = Settings()

with SMTPClient(config.smtp_config) as client:
    client.send_email(email_content)

```

Note that after calling `render()` on the EmailTemplate model, it returns the `EmailContent` model that `SMTPClient` expects for `send()`.


### Setting up a new project
In addition to using the base models included in the package, you can also use `telegraph` to create email project pipelines to handle most mail merge requirements. To set up a new project, use the following command:

```bash
telegraph new-project <project_name>
```
Replace <project_name> with the desired name for your project.

This will create a new directiory at `$HOME/telegraph_projects/<project_name>` with some subfolders, some Jinja templates, and a python file `pipeline.py`. For each new emailing project, you'll add your data to the `data` directory. It's not terribly important how you format the data, but the closer it resembles the context you'll need for your Jinja templates and the `telegraph` email models, the better. 

### Rendering templates
Telegraph uses Jinja2 templating engine to render templates. You can create your own templates using Jinja2 syntax. 

Each new project will create three base Jinja files in the `templates` directory: `subject.txt.j2`, `body.txt.j2`, and `body.html.j2`. The program expects you to have at least the subject template and one of the body templates. If you supply only an HTML template, `telegraph` will create a plaintext version when it sends any emails so recipient clients that prefer plaintext will have the option. If supply both an HTML and a plaintext template, `telegraph` will use the templates you provide and not do any conversion.

### Sending emails
At the moment, `telegraph`'s project workflow relies on sending emails using the `pipeline.py` file that is created with each new project. Eventually, the plan is to have control over each project's pipeline file from the `telegraph` CLI. But for now, to send emails you'll need to customize the `pipeline.py` file for your data and email templates, and then run the file from the command line:
```bash
python pipeline.py <command>
```
`telegraph` uses the `typer` package to handle CLI arguments, even in the `pipeline.py` files, which should produce useful documentation on how each command works. 

### Configuration
Telegraph uses Pydantic settings for configuration. As mentioned above, you can manage settings by copying the `telegraph-default-config.yaml` file created in the project's root directory (wherever you installed it) to `$HOME/.telegraph/telegraph-config.yaml`. **You will need to do this because the default configuration is all placeholder data and will not let you send any emails.**

## Contributing
Contributions to Telegraph are welcome. Please submit a pull request with your changes.

## License
Telegraph is licensed under the MIT License.
