import re

from mrkdwnify.converter import MrkdwnConverter


def _strip_footnotes(text: str) -> str:
    text = re.sub(r"^\[\^[^\]]+\]:[ \t]*.+$", "", text, flags=re.MULTILINE)
    text = re.sub(r"\[\^[^\]]+\]", "", text)
    return text


def mrkdwnify(markdown: str) -> str:
    """Convert Markdown to Slack-compatible mrkdwn formatting."""
    return MrkdwnConverter(_strip_footnotes(markdown)).convert()
