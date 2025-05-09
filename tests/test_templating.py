import re
from pathlib import Path

import pytest
from hypothesis import given
from hypothesis import strategies as st

from telegraph.models.templating import (
    EmailTemplate,
    TemplateContext,
    TemplateRenderer,
)
from telegraph.util.template_handling import html_to_plain

re_html_tag = re.compile(r"<[a-z]/?>")


@given(st.text())
def test_html_to_plain_returns_str_and_no_tags(s: str):
    """html_to_plain should never emit raw HTML tags."""
    out = html_to_plain(s)
    assert isinstance(out, str)
    # assert "<" not in out and ">" not in out
    assert re.search(re_html_tag, out) is None


def test_template_renderer_and_email_template(tmp_path: Path):
    # create a small template directory
    tpl_dir = tmp_path / "templates"
    tpl_dir.mkdir()
    (tpl_dir / "subject.j2").write_text("Hello {{ name }}")
    (tpl_dir / "body.txt.j2").write_text("Plain: {{ msg }}")
    (tpl_dir / "body.html.j2").write_text("<p>{{ msg }}</p>")

    ctx = TemplateContext.model_validate(dict(name="Alice", msg="Hi there"))
    renderer = TemplateRenderer(tpl_dir)

    # full text + html flow
    tpl = EmailTemplate(
        subject_template="subject.j2",
        text_template="body.txt.j2",
        html_template="body.html.j2",
        context=ctx,
    )
    assert tpl.html_template is not None
    email = tpl.render(
        renderer=renderer,
        from_address="from@example.com",
        to_addresses=["to1@example.com"],
        cc=["cc@example.com", "cc2@example.com"],
        bcc=["bcc@example.com", "bcc2@example.com"],
        reply_to=["reply@example.com"],
        attachments=[],
    )

    assert email.subject == "Hello Alice"
    assert email.body == "Plain: Hi there"
    assert email.html_body == "<p>Hi there</p>"
    assert email.from_address == "from@example.com"
    assert email.to_addresses == ["to1@example.com"]
    assert email.cc == ["cc@example.com", "cc2@example.com"]
    assert email.bcc == ["bcc@example.com", "bcc2@example.com"]
    assert email.reply_to == ["reply@example.com"]
    assert email.attachments == []


def test_email_template_fallback_html_to_plain(tmp_path: Path):
    tpl_dir = tmp_path / "templates"
    tpl_dir.mkdir()
    (tpl_dir / "subject.j2").write_text("Subject")
    (tpl_dir / "html.j2").write_text("<h1>Welcome!</h1>")

    ctx = TemplateContext()
    renderer = TemplateRenderer(tpl_dir)

    tpl = EmailTemplate(
        subject_template="subject.j2",
        text_template=None,
        html_template="html.j2",
        context=ctx,
    )
    email = tpl.render(
        renderer=renderer,
        from_address="a@b.com",
        to_addresses=["x@y.com"],
    )

    assert email.subject == "Subject"
    assert email.html_body == "<h1>Welcome!</h1>"
    # fallback should include the inner text
    assert "Welcome!" in email.body


def test_email_template_raises_value_error(tmp_path: Path):
    tpl_dir = tmp_path / "templates"
    tpl_dir.mkdir()
    (tpl_dir / "subject.j2").write_text("Subject")

    ctx = TemplateContext()
    renderer = TemplateRenderer(tpl_dir)

    tpl = EmailTemplate(
        subject_template="subject.j2",
        text_template=None,
        html_template=None,
        context=ctx,
    )
    with pytest.raises(ValueError):
        tpl.render(
            renderer=renderer,
            from_address="a@b.com",
            to_addresses=["x@y.com"],
        )
