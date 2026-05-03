import re
from typing import Any
from urllib.parse import urlparse

from markdown_it import MarkdownIt
from markdown_it.renderer import RendererHTML
from markdown_it.token import Token

from mrkdwnify.utils import escape_specials


class MrkdwnConverter(RendererHTML):
    SUPPORTED_TOKENS = [
        "text",
        "inline",
        "strong_open",
        "strong_close",
        "em_open",
        "em_close",
        "s_open",
        "s_close",
        "link_open",
        "link_close",
        "code_inline",
        "code_block",
        "bullet_list_open",
        "bullet_list_close",
        "ordered_list_open",
        "ordered_list_close",
        "list_item_open",
        "list_item_close",
        "paragraph_open",
        "paragraph_close",
        "blockquote_open",
        "blockquote_close",
        "image",
        "heading_open",
        "heading_close",
        "fence",
        "table_open",
        "table_close",
        "td_open",
        "td_close",
        "th_open",
        "th_close",
        "tr_open",
        "tr_close",
        "hardbreak",
        "softbreak",
    ]

    def __init__(self, markdown_text: str = ""):
        super().__init__()
        self.markdown_text = markdown_text
        self._in_heading = False
        self._list_depth = 0
        self._in_blockquote = 0

    def render(self, tokens: list[Token], options: dict[str, Any], env: dict[str, Any]) -> str:
        final_tokens = [t for t in tokens if t.type in self.SUPPORTED_TOKENS]
        return super().render(final_tokens, options, env)

    def convert(self) -> str:
        md = MarkdownIt(
            "gfm-like",
            renderer_cls=type(self),
            options_update={
                "html": False,
                "linkify": False,
                "breaks": False,
            },
        ).disable("table")
        return md.render(self.markdown_text)

    def hardbreak(
        self, tokens: list[Token], idx: int, options: dict[str, Any], env: dict[str, Any]
    ) -> str:
        return "\n> " if self._in_blockquote else "\n"

    def softbreak(
        self, tokens: list[Token], idx: int, options: dict[str, Any], env: dict[str, Any]
    ) -> str:
        return "\n> " if self._in_blockquote else "\n"

    def text(
        self, tokens: list[Token], idx: int, options: dict[str, Any], env: dict[str, Any]
    ) -> str:
        return escape_specials(tokens[idx].content)

    def heading_open(
        self, tokens: list[Token], idx: int, options: dict[str, Any], env: dict[str, Any]
    ) -> str:
        self._in_heading = True
        return "*"

    def heading_close(
        self, tokens: list[Token], idx: int, options: dict[str, Any], env: dict[str, Any]
    ) -> str:
        self._in_heading = False
        return "*\n\n"

    def strong_open(
        self, tokens: list[Token], idx: int, options: dict[str, Any], env: dict[str, Any]
    ) -> str:
        return "" if self._in_heading else "*"

    def strong_close(
        self, tokens: list[Token], idx: int, options: dict[str, Any], env: dict[str, Any]
    ) -> str:
        return "" if self._in_heading else "*"

    def em_open(
        self, tokens: list[Token], idx: int, options: dict[str, Any], env: dict[str, Any]
    ) -> str:
        return "_"

    def em_close(
        self, tokens: list[Token], idx: int, options: dict[str, Any], env: dict[str, Any]
    ) -> str:
        return "_"

    def s_open(
        self, tokens: list[Token], idx: int, options: dict[str, Any], env: dict[str, Any]
    ) -> str:
        return "~"

    def s_close(
        self, tokens: list[Token], idx: int, options: dict[str, Any], env: dict[str, Any]
    ) -> str:
        return "~"

    def link_open(
        self, tokens: list[Token], idx: int, options: dict[str, Any], env: dict[str, Any]
    ) -> str:
        href = tokens[idx].attrs.get("href", "")
        title = tokens[idx].attrs.get("title", "")
        only_link = tokens[idx + 1].nesting == -1
        if only_link:
            return f"<{href}|{title}" if title else f"<{href}"
        return f"<{href}|"

    def link_close(
        self, tokens: list[Token], idx: int, options: dict[str, Any], env: dict[str, Any]
    ) -> str:
        content = tokens[idx].content
        return f">: {content}\n" if content else ">"

    def code_inline(
        self, tokens: list[Token], idx: int, options: dict[str, Any], env: dict[str, Any]
    ) -> str:
        return f"`{tokens[idx].content}`"

    def code_block(
        self, tokens: list[Token], idx: int, options: dict[str, Any], env: dict[str, Any]
    ) -> str:
        content = re.sub(r"^#!.*?\n", "", tokens[idx].content)
        return f"```\n{content}```\n"

    def fence(
        self, tokens: list[Token], idx: int, options: dict[str, Any], env: dict[str, Any]
    ) -> str:
        content = re.sub(r"^#!.*?\n", "", tokens[idx].content)
        return f"```\n{content}```\n"

    def bullet_list_open(
        self, tokens: list[Token], idx: int, options: dict[str, Any], env: dict[str, Any]
    ) -> str:
        self._list_depth += 1
        return ""

    def bullet_list_close(
        self, tokens: list[Token], idx: int, options: dict[str, Any], env: dict[str, Any]
    ) -> str:
        self._list_depth -= 1
        return ""

    def list_item_open(
        self, tokens: list[Token], idx: int, options: dict[str, Any], env: dict[str, Any]
    ) -> str:
        indent = "    " * (self._list_depth - 1)
        return f"{indent}{tokens[idx].info}.  " if tokens[idx].info else f"{indent}•   "

    def list_item_close(
        self, tokens: list[Token], idx: int, options: dict[str, Any], env: dict[str, Any]
    ) -> str:
        return ""

    def ordered_list_open(
        self, tokens: list[Token], idx: int, options: dict[str, Any], env: dict[str, Any]
    ) -> str:
        self._list_depth += 1
        return ""

    def ordered_list_close(
        self, tokens: list[Token], idx: int, options: dict[str, Any], env: dict[str, Any]
    ) -> str:
        self._list_depth -= 1
        return ""

    def paragraph_open(
        self, tokens: list[Token], idx: int, options: dict[str, Any], env: dict[str, Any]
    ) -> str:
        return ""

    def paragraph_close(
        self, tokens: list[Token], idx: int, options: dict[str, Any], env: dict[str, Any]
    ) -> str:
        return "\n"

    def blockquote_open(
        self, tokens: list[Token], idx: int, options: dict[str, Any], env: dict[str, Any]
    ) -> str:
        self._in_blockquote += 1
        return "> "

    def blockquote_close(
        self, tokens: list[Token], idx: int, options: dict[str, Any], env: dict[str, Any]
    ) -> str:
        self._in_blockquote -= 1
        return "\n"

    def image(
        self, tokens: list[Token], idx: int, options: dict[str, Any], env: dict[str, Any]
    ) -> str:
        src = tokens[idx].attrs.get("src", "")
        title = tokens[idx].attrs.get("title", "")
        display_text = tokens[idx].content or title

        parsed_url = urlparse(src)
        if parsed_url.scheme and parsed_url.netloc:
            output = "<" + src
            if display_text:
                output += "|" + display_text
            output += ">"
            return output
        return display_text
