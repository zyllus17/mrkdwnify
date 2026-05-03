# Changelog

All notable changes to this project will be documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

## [0.2.0] – 2025-05-03

### Fixed
- Nested lists now indent sub-items by 4 spaces per depth level
- Multi-line blockquotes prefix every line with `> ` via softbreak/hardbreak handling
- Links with a `title` attribute but no display text now render as `<url|title>`

### Added
- 6 new tests covering all three fixes (55 tests total)

### Changed
- Dropped Python 3.8 support (EOL Oct 2024) — now supports 3.9–3.13
- Updated CI: `actions/checkout` v3 → v4, `setup-python` v4 → v5

## [0.1.0] – 2025-05-03

### Added
- Initial release as `mrkdwnify` (forked and rebranded from `slackify-markdown`)
- Converts Markdown to Slack `mrkdwn` format: headings, bold, italic, strikethrough,
  inline code, fenced code blocks, links, images, lists, blockquotes
- Preserves Slack-native mentions (`<@user>`, `<#channel>`, `<!here>`, etc.)
- 49 passing tests ported from the original project
