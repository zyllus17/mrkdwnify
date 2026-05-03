# mrkdwnify — TDD Upgrade Plan

> Working document. Complete modules in order. Mark done with `[x]`. After each module, run `uv run pytest tests/` — all tests must be green before moving on.

**Current:** v0.2.0 — 55 tests passing  
**Branch:** always work on `dev`, merge to `main` when a module is complete

---

## Confirmed Bugs (from live probing)

| # | Bug | Input | Bad Output | Expected |
|---|-----|-------|------------|----------|
| B1 | Multi-paragraph blockquote loses `> ` | `"> P1\n>\n> P2"` | `"> P1\nP2\n\n"` | `"> P1\n> P2\n\n"` |
| B2 | List inside blockquote loses `> ` | `"> - a\n> - b"` | `"> •   a\n•   b\n\n"` | `"> •   a\n> •   b\n\n"` |
| B3 | Horizontal rule silently dropped | `"---"` | `""` | `"────────────\n"` |
| B4 | Footnotes misread as links | `"x[^1]\n\n[^1]: note"` | `"x<note|^1>\n"` | `"x\n"` |
| B5 | `link_close` has unreachable branch | `content` on `link_close` is never set | dead code | simplify to `return ">"` |
| B6 | `escape_specials` O(n·m) loop | long text with mentions | slow | refactor to split-based O(n) |

---

## Module 1 — Escaping & Special Characters
**File:** `src/mrkdwnify/utils.py`  
**Status:** `[ ]`  
**Fixes:** B6

### What to change
Replace the character-by-character loop with a `re.split`-based approach that's O(n):

```python
def escape_specials(text: str) -> str:
    text = text.replace("&", "&amp;")
    parts = re.split(r"(<[@#!][^>]*>)", text)
    for i in range(0, len(parts), 2):          # even indices = non-mention segments
        parts[i] = parts[i].replace("<", "&lt;").replace(">", "&gt;")
    return "".join(parts)
```

### Tests to write (`tests/test_escape.py`)
```
test_escape_ampersand           "&"          → "&amp;"
test_escape_less_than           "<tag>"      → "&lt;tag&gt;"
test_escape_greater_than        "a > b"      → "a &gt; b"
test_preserve_user_mention      "<@U123>"    → "<@U123>"
test_preserve_channel_mention   "<#C123>"    → "<#C123>"
test_preserve_special_mention   "<!here>"    → "<!here>"
test_preserve_subteam           "<!subteam^S1|team>" → "<!subteam^S1|team>"
test_escape_does_not_double     "&amp;"      → "&amp;amp;"  (correct — re-escapes raw &)
test_empty_string               ""           → ""
test_mixed_mentions_and_text    "<@U1> & <tag>" → "<@U1> &amp; &lt;tag&gt;"
```

### How to verify in Slack
Send a message containing `&`, `<tag>`, `>` and Slack user mentions. Confirm the special chars render as literal text and the mentions trigger notifications normally.

---

## Module 2 — Inline Formatting
**File:** `src/mrkdwnify/converter.py`  
**Status:** `[ ]`  
**Fixes:** edge cases only — no known bugs, but gaps in coverage

### Known edge cases not yet tested
- Bold at start/end of sentence with punctuation: `**bold!**` → `*bold!*`
- Italic with underscore syntax: `_italic_` → `_italic_` (already passes as text)
- Nested formatting: `**_bold italic_**` → `*_bold italic_*`
- Strikethrough in a list: `- ~~done~~` → `•   ~done~`
- Inline code prevents formatting inside: `` `**not bold**` `` → `` `**not bold**` ``
- Empty bold/italic: `****` or `__` (edge case — markdown-it usually handles)

### Tests to write (`tests/test_inline.py`)
```
test_bold_with_punctuation      "**done!**"           → "*done!*\n"
test_nested_bold_italic         "**_bold italic_**"   → "*_bold italic_*\n"
test_italic_with_underscore     "_italic_"            → "_italic_\n"
test_strike_in_list             "- ~~done~~"          → "•   ~done~\n"
test_code_prevents_formatting   "`**not bold**`"      → "`**not bold**`\n"
test_all_three_inline           "**bold** _italic_ ~~strike~~" → "*bold* _italic_ ~strike~\n"
```

### How to verify in Slack
Post a message with bold, italic, strikethrough, and inline code. Confirm each renders correctly and that text inside backticks is not formatted.

---

## Module 3 — Headings
**File:** `src/mrkdwnify/converter.py`  
**Status:** `[ ]`  
**Fixes:** edge cases only

### Known edge cases not yet tested
- All six heading levels (h1–h6 all → bold, already works)
- Heading with strikethrough: `# ~~text~~` → `*~text~*` (currently works but untested)
- Heading with link: `# [title](url)` → `*<url|title>*` (currently works but untested)
- Empty heading: `#` or `# ` (markdown-it may skip or produce empty bold)
- Heading with only a code span: `# \`code\`` (code inside heading)

### Tests to write (`tests/test_headings.py`)
```
test_h1_through_h6              all six levels → "*text*\n\n"
test_heading_with_strike        "# ~~text~~"       → "*~text~*\n\n"
test_heading_with_link          "# [t](http://x)"  → "*<http://x|t>*\n\n"
test_heading_with_code          "# `code`"         → "*`code`*\n\n"
```

### How to verify in Slack
Send a message with multiple heading levels and formatting inside headings. Confirm all headings appear as bold text in Slack regardless of level.

---

## Module 4 — Links
**File:** `src/mrkdwnify/converter.py`  
**Status:** `[ ]`  
**Fixes:** B5 (dead code cleanup)

### What to change — cleanup
`link_close` has an unreachable branch (`content` is never set on `link_close` tokens in markdown-it). Simplify:
```python
def link_close(self, ...):
    return ">"
```

### Known edge cases not yet tested
- Email link: `[email](mailto:foo@bar.com)` → `<mailto:foo@bar.com|email>`
- Bold text inside link: `[**bold**](url)` → `<url|*bold*>` (currently works, needs test)
- Link immediately followed by punctuation: `[a](url).` → `<url|a>.`
- Link with special chars in display text: `[foo & bar](url)` → `<url|foo &amp; bar>`
- Empty href: `[text]()` (edge case)

### Tests to write (add to `tests/test_links.py`)
```
test_email_link                 "[e](mailto:a@b.com)"       → "<mailto:a@b.com|e>\n"
test_bold_inside_link           "[**b**](http://x.com)"     → "<http://x.com|*b*>\n"
test_link_with_punctuation      "[a](http://x.com)."        → "<http://x.com|a>.\n"
test_link_display_with_amp      "[a & b](http://x.com)"     → "<http://x.com|a &amp; b>\n"
```

### How to verify in Slack
Send messages with formatted links. Confirm they are clickable and display text renders correctly including bold formatting inside link text.

---

## Module 5 — Images
**File:** `src/mrkdwnify/converter.py`  
**Status:** `[ ]`  
**Fixes:** edge cases only — current coverage is solid

### Known edge cases not yet tested
- Image inside a list item
- Image inside a blockquote
- Image with special chars in alt text

### Tests to write (add to `tests/test_images.py`)
```
test_image_in_list              "- ![alt](http://x.com/i.png)"  → "•   <http://x.com/i.png|alt>\n"
test_image_in_blockquote        "> ![alt](http://x.com/i.png)"  → "> <http://x.com/i.png|alt>\n\n"
test_image_alt_with_amp         "![a & b](http://x.com/i.png)"  → "<http://x.com/i.png|a & b>\n"
```

### How to verify in Slack
Send a message with an image URL. Confirm it renders as a clickable link (Slack renders linked images as previews in some contexts).

---

## Module 6 — Code Blocks
**File:** `src/mrkdwnify/converter.py`  
**Status:** `[ ]`  
**Fixes:** edge cases only

### Known edge cases not yet tested
- Empty code block: ` ``` ``` ` → ` ```\n``` `
- Code block with special chars: ` ``` foo & <bar> ``` ` → content untouched (no escaping inside code)
- Inline code with backtick inside: `` ` ` ``
- Code block inside a list item (indented code)
- Very long code block (no truncation issues)

### Tests to write (add to `tests/test_code.py`)
```
test_empty_fence                "```\n```"            → "```\n```\n"
test_fence_no_escaping          "```\nfoo & <bar>\n```"  → "```\nfoo & <bar>\n```\n"
test_inline_code_no_escaping    "`foo & <bar>`"       → "`foo & <bar>`\n"
```

### How to verify in Slack
Send a message with a code block containing HTML entities. Confirm they appear as literal characters, not HTML-rendered.

---

## Module 7 — Lists
**File:** `src/mrkdwnify/converter.py`  
**Status:** `[ ]`  
**Fixes:** edge cases only — nested lists fixed in v0.2.0

### Known edge cases not yet tested
- Three-level deep nesting (currently works, needs test)
- List item with inline formatting at each depth
- Ordered list starting from a number other than 1: `3. item` (markdown-it may reset to 1)
- Mixed nesting (ordered → unordered → ordered)

### Tests to write (add to `tests/test_lists.py`)
```
test_three_level_nesting        "- A\n  - B\n    - C"     → "•   A\n    •   B\n        •   C\n"
test_list_item_with_formatting  "- **bold** and _italic_" → "•   *bold* and _italic_\n"
test_deeply_nested_mixed        "1. A\n   - B\n     1. C" → "1.  A\n    •   B\n        1.  C\n"
```

### How to verify in Slack
Send a message with nested lists (2-3 levels). Confirm sub-items appear visually indented under parent items.

---

## Module 8 — Blockquotes ⚠️ Contains active bugs
**File:** `src/mrkdwnify/converter.py`  
**Status:** `[ ]`  
**Fixes:** B1, B2

### Root cause
`blockquote_open` emits `"> "` for the first line but `paragraph_open` (and `list_item_open`) return `""` unconditionally, so any content after the first paragraph/list item loses the `> ` prefix.

### What to change
1. `blockquote_open` — return `""` (stop emitting `"> "` here)
2. `paragraph_open` — return `"> "` when `_in_blockquote > 0` AND `_list_depth == 0`
3. `list_item_open` — prepend `"> "` when `_in_blockquote > 0`
4. Keep `softbreak`/`hardbreak` → `"\n> "` when `_in_blockquote` (already done)

```python
def blockquote_open(self, ...):
    self._in_blockquote += 1
    return ""

def paragraph_open(self, ...):
    return "> " if self._in_blockquote > 0 and self._list_depth == 0 else ""

def list_item_open(self, ...):
    prefix = "> " if self._in_blockquote > 0 else ""
    indent = "    " * (self._list_depth - 1)
    return (f"{prefix}{indent}{tokens[idx].info}.  "
            if tokens[idx].info else f"{prefix}{indent}•   ")
```

### Tests to write (add to `tests/test_blockquotes.py`)
```
test_single_line_blockquote     "> text"                    → "> text\n\n"
test_multiline_blockquote       "> L1\n> L2\n> L3"          → "> L1\n> L2\n> L3\n\n"  (already passing)
test_multi_paragraph_blockquote "> P1\n>\n> P2"             → "> P1\n> P2\n\n"         (B1 — currently failing)
test_list_inside_blockquote     "> - item1\n> - item2"      → "> •   item1\n> •   item2\n\n"  (B2 — currently failing)
test_blockquote_with_bold       "> **bold** text"           → "> *bold* text\n\n"
test_blockquote_with_code       "> `inline code`"           → "> `inline code`\n\n"
```

### How to verify in Slack
Send a multi-paragraph blockquote. Confirm ALL paragraphs show the grey left-border in Slack, not just the first one. Also confirm a list inside a quote is fully quoted.

---

## Module 9 — Horizontal Rules
**File:** `src/mrkdwnify/converter.py`  
**Status:** `[ ]`  
**Fixes:** B3

### Root cause
`hr` token is not in `SUPPORTED_TOKENS` so it is silently filtered out. Slack has no native `---` rule, but a decorative line is better than nothing.

### What to change
Add `"hr"` to `SUPPORTED_TOKENS` and add a handler:
```python
def hr(self, tokens, idx, options, env):
    return "────────────────────\n\n"
```

### Tests to write (add to `tests/test_misc.py`)
```
test_horizontal_rule            "---"       → "────────────────────\n\n"
test_hr_between_paragraphs      "a\n\n---\n\nb" → "a\n────────────────────\n\nb\n"
test_hr_variants                "***" / "___"   → same as "---"
```

### How to verify in Slack
Send a message with `---` separator. Confirm a visual divider line appears between sections in Slack.

---

## Module 10 — Footnotes & Unsupported Syntax
**File:** `src/mrkdwnify/service.py` (pre-processing)  
**Status:** `[ ]`  
**Fixes:** B4

### Root cause
`markdown-it` in `gfm-like` mode has no footnote plugin. It treats `[^1]: note` as a reference link definition (label `^1`, URL `note`) and `[^1]` as a use of that reference — producing `<note|^1>` in output. This is a major correctness bug for AI-generated content which commonly includes footnotes.

### What to change
Add a pre-processing step in `service.py` before markdown-it parsing:
```python
import re

def _preprocess(text: str) -> str:
    # Strip footnote definitions: [^label]: content (full line)
    text = re.sub(r"^\[\^[^\]]+\]:[ \t]*.+$", "", text, flags=re.MULTILINE)
    # Strip footnote references: [^label]
    text = re.sub(r"\[\^[^\]]+\]", "", text)
    return text
```

Apply in `MrkdwnConverter.convert()` before `md.render(...)`.

### Tests to write (add to `tests/test_misc.py`)
```
test_footnote_ref_stripped          "text[^1]\n\n[^1]: note"   → "text\n"
test_footnote_multi_stripped        "a[^1] b[^2]\n\n[^1]: x\n[^2]: y"  → "a b\n"
test_footnote_def_only_stripped     "[^1]: just a note"        → ""
test_non_footnote_link_preserved    "[normal](http://x.com)"   → "<http://x.com|normal>\n"
```

### How to verify in Slack
Ask an AI (Claude, GPT) to generate a response with footnotes and run it through `mrkdwnify`. Confirm footnote markers and definitions are cleanly removed and the message reads naturally.

---

## Completion Checklist

| Module | Description | Status | Tests Added | Merged to main |
|--------|-------------|--------|-------------|----------------|
| 1 | Escaping & Special Characters | `[ ]` | `[ ]` | `[ ]` |
| 2 | Inline Formatting | `[ ]` | `[ ]` | `[ ]` |
| 3 | Headings | `[ ]` | `[ ]` | `[ ]` |
| 4 | Links | `[ ]` | `[ ]` | `[ ]` |
| 5 | Images | `[ ]` | `[ ]` | `[ ]` |
| 6 | Code Blocks | `[ ]` | `[ ]` | `[ ]` |
| 7 | Lists | `[ ]` | `[ ]` | `[ ]` |
| 8 | Blockquotes ⚠️ | `[ ]` | `[ ]` | `[ ]` |
| 9 | Horizontal Rules | `[ ]` | `[ ]` | `[ ]` |
| 10 | Footnotes & Unsupported Syntax | `[ ]` | `[ ]` | `[ ]` |

---

## Version Targets

| Version | Modules | Notes |
|---------|---------|-------|
| v0.2.x | Fixes from modules 1, 8, 9, 10 | Critical bug fixes — release to PyPI |
| v0.3.0 | Modules 2–7 | Full edge case coverage |
| v1.0.0 | Block Kit output mode | `mrkdwnify(text, output="blocks")` |
| v1.1.0 | AI templates + prompt helpers | `render_ai_blocks(intent)` |
