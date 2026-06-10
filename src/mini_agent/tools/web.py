"""网页抓取相关工具。"""

from __future__ import annotations

from html.parser import HTMLParser
from urllib.request import Request, urlopen


class _ContentExtractor(HTMLParser):
    """提取网页正文文本，跳过明显的非正文标签。"""

    _skip_tags = {"script", "style", "nav", "header", "footer", "iframe", "noscript"}
    _block_tags = {
        "article",
        "aside",
        "blockquote",
        "br",
        "div",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "li",
        "main",
        "p",
        "section",
        "tr",
    }

    def __init__(self) -> None:
        super().__init__()
        self._skip_depth = 0
        self._parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in self._skip_tags:
            self._skip_depth += 1
            return
        if self._skip_depth == 0 and tag in self._block_tags:
            self._parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in self._skip_tags and self._skip_depth > 0:
            self._skip_depth -= 1
            return
        if self._skip_depth == 0 and tag in self._block_tags:
            self._parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self._skip_depth > 0:
            return
        text = " ".join(data.split())
        if text:
            self._parts.append(text)

    def get_text(self) -> str:
        lines = [" ".join(line.split()) for line in "".join(self._parts).splitlines()]
        cleaned_lines = [line for line in lines if line]
        return "\n".join(cleaned_lines)


def _fetch_html(url: str, timeout: int = 10) -> str:
    if not url.startswith(("http://", "https://")):
        raise ValueError("url 必须以 http:// 或 https:// 开头")

    request = Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
            )
        },
    )
    with urlopen(request, timeout=timeout) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="ignore")


def _clean_html_to_text(html: str) -> str:
    parser = _ContentExtractor()
    parser.feed(html)
    parser.close()
    return parser.get_text()


def get_page_content(url: str, max_chars: int = 5000) -> str:
    """抓取网页正文文本，并限制返回长度，避免上下文过载。"""

    html = _fetch_html(url)
    text = _clean_html_to_text(html)
    return text[:max_chars]
