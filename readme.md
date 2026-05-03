# mrkdwnify

[![PyPI version](https://badge.fury.io/py/mrkdwnify.svg)](https://pypi.org/project/mrkdwnify/)
[![PyPI Downloads](https://static.pepy.tech/badge/mrkdwnify)](https://pepy.tech/projects/mrkdwnify)
[![CI](https://github.com/zyllus17/mrkdwnify/actions/workflows/tests.yml/badge.svg)](https://github.com/zyllus17/mrkdwnify/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python library for converting standard Markdown into Slack's `mrkdwn` format — the exact syntax Slack uses to render bold, italic, links, code blocks, lists, and more.

Built specifically for **AI bots and Slack integrations** where LLM output (always in Markdown) needs to render correctly in Slack without manual post-processing.

## Installation

```bash
pip install mrkdwnify
```

## Quick Start

```python
from mrkdwnify import mrkdwnify

text = mrkdwnify("""
# Deploy Complete

**my-service** v1.2 is live in production.

Changes in this release:
- Fixed *authentication* bug
- Improved ~~old caching~~ new caching layer
- Added `health-check` endpoint

> Review the [full changelog](https://example.com/changelog)
""")

print(text)
```

Output (renders correctly in Slack):

```
*Deploy Complete*

*my-service* v1.2 is live in production.

Changes in this release:
•   Fixed _authentication_ bug
•   Improved ~old caching~ new caching layer
•   Added `health-check` endpoint

> Review the <https://example.com/changelog|full changelog>
```

## Conversion Reference

| Markdown | Slack mrkdwn |
|----------|--------------|
| `# Heading` | `*Heading*` |
| `**Bold**` | `*Bold*` |
| `*Italic*` | `_Italic_` |
| `~~Strike~~` | `~Strike~` |
| `` `code` `` | `` `code` `` |
| ` ``` block ``` ` | ` ``` block ``` ` |
| `[Link](https://example.com)` | `<https://example.com\|Link>` |
| `![img](https://example.com/img.png)` | `<https://example.com/img.png\|img>` |
| `> blockquote` | `> blockquote` |
| `- item` | `•   item` |
| `1. item` | `1.  item` |
| `<@U12345>` | `<@U12345>` (preserved) |
| `<#C12345\|general>` | `<#C12345\|general>` (preserved) |

## Features

- Converts all standard Markdown to valid Slack `mrkdwn`
- Preserves Slack-native mentions (`<@user>`, `<#channel>`, `<!here>`, `<!channel>`)
- Handles GFM strikethrough (`~~text~~` → `~text~`)
- Strips heading hierarchy (all headings become bold — Slack has no heading levels)
- Suppresses redundant bold markers inside headings to avoid double `**`
- Correctly escapes `&`, `<`, `>` as HTML entities where required by Slack
- Strips unsupported syntax cleanly (no broken output)
- Handles reference-style links and images
- Tested across Python 3.9–3.13

## Usage with AI Bots

LLMs output Markdown. Slack expects mrkdwn. `mrkdwnify` is the bridge:

```python
from mrkdwnify import mrkdwnify
import anthropic

client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Summarize today's deployments"}],
)

# Convert AI response (Markdown) to Slack-ready mrkdwn
slack_text = mrkdwnify(message.content[0].text)

# Post to Slack
slack_client.chat_postMessage(channel="#deployments", text=slack_text)
```

## Contributing

Contributions are welcome! Please open an issue first to discuss what you'd like to change.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes (`git commit -m 'Add my feature'`)
4. Push to the branch (`git push origin feature/my-feature`)
5. Open a Pull Request

## License

MIT License — see [LICENSE](LICENSE) for details.
