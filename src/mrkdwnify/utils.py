import re


def escape_specials(text: str) -> str:
    text = text.replace("&", "&amp;")
    parts = re.split(r"(<[@#!][^>]*>)", text)
    for i in range(0, len(parts), 2):  # even indices = non-mention text
        parts[i] = parts[i].replace("<", "&lt;").replace(">", "&gt;")
    return "".join(parts)
