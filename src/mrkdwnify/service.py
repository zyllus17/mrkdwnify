from mrkdwnify.converter import MrkdwnConverter


def mrkdwnify(markdown: str) -> str:
    """Convert Markdown to Slack-compatible mrkdwn formatting."""
    return MrkdwnConverter(markdown).convert()
