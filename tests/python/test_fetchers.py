"""Unit tests for the read skill's platform fetchers.

Network paths stay untested by design; these cover the pure seams (URL
parsing, block-to-Markdown transforms, frontmatter rendering) and setup-error
guidance without requiring optional dependencies or credentials.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "skills" / "read" / "scripts"))

import fetch_feishu  # noqa: E402
import fetch_weixin  # noqa: E402
import fetch_local  # noqa: E402


def test_fetch_local_bypasses_system_proxy_env(monkeypatch):
    """The local tier's privacy contract is "the URL never leaves the machine":
    a system proxy is a third party too, so http_proxy/https_proxy env must be
    bypassed (urllib would honor them silently via getproxies)."""
    monkeypatch.setenv("http_proxy", "http://127.0.0.1:1")
    monkeypatch.setenv("https_proxy", "http://127.0.0.1:1")

    captured = {}

    class _FakeResponse:
        headers = {"Content-Type": "text/html"}

        def read(self):
            return b"<html></html>"

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    class _FakeOpener:
        def open(self, req, timeout):
            return _FakeResponse()

    real_build_opener = fetch_local.urllib.request.build_opener

    def spy_build_opener(*handlers):
        for h in handlers:
            if isinstance(h, fetch_local.urllib.request.ProxyHandler):
                captured["proxies"] = h.proxies
        return _FakeOpener()

    monkeypatch.setattr(
        fetch_local.urllib.request, "build_opener", spy_build_opener
    )
    try:
        fetch_local.fetch_html("https://example.com")
    finally:
        monkeypatch.setattr(
            fetch_local.urllib.request, "build_opener", real_build_opener
        )

    assert captured.get("proxies") == {}, "local tier must bypass system proxy env"



def test_feishu_parse_url_variants():
    assert fetch_feishu.parse_url("https://x.feishu.cn/docx/AbC123") == ("AbC123", "docx")
    assert fetch_feishu.parse_url("https://x.feishu.cn/wiki/W1k1") == ("W1k1", "wiki")
    assert fetch_feishu.parse_url("https://x.feishu.cn/docs/Legacy9") == ("Legacy9", "legacy_doc")
    assert fetch_feishu.parse_url("https://a.larksuite.com/docx/L4rk") == ("L4rk", "docx")
    # Unrecognized input falls through as a raw docx id.
    assert fetch_feishu.parse_url("PlainToken") == ("PlainToken", "docx")


def test_feishu_extract_text_styles_and_mentions():
    elements = [
        {"text_run": {"content": "bold", "text_element_style": {"bold": True}}},
        {"text_run": {"content": "code", "text_element_style": {"inline_code": True}}},
        {
            "text_run": {
                "content": "link",
                "text_element_style": {"link": {"url": "https%3A%2F%2Fexample.com"}},
            }
        },
        {"mention_user": {"user_id": "u42"}},
        {"equation": {"content": "x^2"}},
    ]
    assert (
        fetch_feishu.extract_text(elements)
        == "**bold**`code`[link](https://example.com)@u42$x^2$"
    )


def test_feishu_blocks_to_md_core_block_types():
    blocks = [
        {"block_type": 3, "heading1": {"elements": [{"text_run": {"content": "Title"}}]}},
        {"block_type": 2, "text": {"elements": [{"text_run": {"content": "para"}}]}},
        {"block_type": 10, "bullet": {"elements": [{"text_run": {"content": "item"}}]}},
        {"block_type": 11, "parent_id": "p1", "ordered": {"elements": [{"text_run": {"content": "one"}}]}},
        {"block_type": 11, "parent_id": "p1", "ordered": {"elements": [{"text_run": {"content": "two"}}]}},
        {
            "block_type": 12,
            "code": {"elements": [{"text_run": {"content": "print()"}}], "style": {"language": 50}},
        },
        {"block_type": 15, "todo": {"elements": [{"text_run": {"content": "done it"}}], "style": {"done": True}}},
        {"block_type": 16},
        {"block_type": 17, "image": {"token": "tok9"}},
    ]
    md = fetch_feishu.blocks_to_md(blocks)
    assert "# Title" in md
    assert "para" in md
    assert "- item" in md
    assert "1. one" in md and "2. two" in md
    assert "```python" in md and "print()" in md
    assert "- [x] done it" in md
    assert "---" in md
    assert "![image](feishu-image://tok9)" in md


def test_feishu_get_token_without_credentials_is_offline(monkeypatch):
    monkeypatch.delenv("FEISHU_APP_ID", raising=False)
    monkeypatch.delenv("FEISHU_APP_SECRET", raising=False)
    token, err = fetch_feishu.get_token()
    assert token is None
    assert "not set" in err
    assert "lark-cli auth login" in err


def test_feishu_get_token_without_requests_names_both_paths(monkeypatch):
    monkeypatch.setattr(fetch_feishu, "requests", None)
    monkeypatch.setenv("FEISHU_APP_ID", "app")
    monkeypatch.setenv("FEISHU_APP_SECRET", "secret")
    token, err = fetch_feishu.get_token()
    assert token is None
    assert "pip install requests" in err
    assert "lark-cli docs +fetch" in err


def test_weixin_to_markdown_frontmatter():
    md = fetch_weixin.to_markdown(
        {"title": "T", "author": "A", "date": "2020-01-01", "url": "https://u", "content": "body"}
    )
    assert md.startswith("---\n")
    assert 'title: "T"' in md
    assert 'author: "A"' in md
    assert "# T" in md
    assert md.endswith("body")


def test_weixin_to_markdown_error_dict():
    assert fetch_weixin.to_markdown({"error": "boom"}) == "Error: boom"
