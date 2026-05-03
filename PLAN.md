# mrkdwnify — TDD Upgrade Plan

> Living document. Work modules in order 1 → 10. Mark done with `[x]`.
> After each module: `make check` must be green before moving on.
> Always work on `dev` branch, merge to `main` when a module is complete.

**Current:** v0.2.0 · 55 tests · 97% coverage  
**Commands:** `make test` · `make lint` · `make typecheck` · `make check`

---

## Known Bugs (fixed as we reach their module)

| ID | Module | Bug | Input | Bad Output | Expected |
|----|--------|-----|-------|------------|----------|
| B1 | 4 | Multi-paragraph blockquote loses `> ` | `"> P1\n>\n> P2"` | `"> P1\nP2\n\n"` | `"> P1\n> P2\n\n"` |
| B2 | 4 | List inside blockquote loses `> ` | `"> - a\n> - b"` | `"> •   a\n•   b\n\n"` | `"> •   a\n> •   b\n\n"` |
| B3 | 3 | Horizontal rule silently dropped | `"---"` | `""` | `"────────────────────\n\n"` |
| B4 | 2 | Footnotes misread as Slack links | `"x[^1]\n\n[^1]: note"` | `"x<note|^1>\n"` | `"x\n"` |
| B5 | 5 | `link_close` has unreachable dead branch | any link | silent | remove dead code |
| B6 | 1 | `escape_specials` O(n·m) loop | long text + mentions | slow | O(n) split-based |

---

## Module 1 — Escaping & Special Characters
**File:** `src/mrkdwnify/utils.py`  
**Status:** `[ ]`  
**Bug:** B6 · **Tests to add:** `tests/test_escape.py`

### What breaks today
`escape_specials` checks each character against every mention range — O(n·m).
Works correctly but is inefficient and harder to reason about than necessary.

### Implementation
Replace the loop with `re.split` — split on mention patterns, escape the non-mention parts:

```python
def escape_specials(text: str) -> str:
    text = text.replace("&", "&amp;")
    parts = re.split(r"(<[@#!][^>]*>)", text)
    for i in range(0, len(parts), 2):      # even indices = non-mention text
        parts[i] = parts[i].replace("<", "&lt;").replace(">", "&gt;")
    return "".join(parts)
```

### Tests (write these first — all must fail before implementation)
```
test_escape_ampersand               "&"                    → "&amp;"
test_escape_less_than               "<tag>"                → "&lt;tag&gt;"
test_escape_greater_than            "a > b"                → "a &gt; b"
test_preserve_user_mention          "<@U123>"              → "<@U123>"
test_preserve_channel_mention       "<#C123>"              → "<#C123>"
test_preserve_special_mention       "<!here>"              → "<!here>"
test_preserve_subteam               "<!subteam^S1|team>"   → "<!subteam^S1|team>"
test_mixed_mentions_and_text        "<@U1> & <tag>"        → "<@U1> &amp; &lt;tag&gt;"
test_empty_string                   ""                     → ""
test_multiple_mentions              "<@A> text <@B>"       → "<@A> text <@B>"
```

### How to verify in Slack
Post a message like: `Use <@U123> to mention someone, but <tag> is &not& a mention`.  
Confirm: mention renders as a real user ping, `<tag>` appears as literal text `<tag>`, `&` appears as `&`.

---

## Module 2 — Footnotes & Unsupported Syntax
**File:** `src/mrkdwnify/service.py` (pre-processing step)  
**Status:** `[ ]`  
**Bug:** B4 · **Tests to add:** `tests/test_footnotes.py`

### What breaks today
`markdown-it` has no footnote plugin. It treats `[^1]: note` as a reference-link definition
(label = `^1`, URL = `note`) and `[^1]` as a use of it, producing `<note|^1>` — a fake Slack link.
This is the most dangerous bug for AI-generated content, which frequently contains footnotes.

### Implementation
Pre-process in `service.py` before handing to the parser:

```python
import re

def _strip_footnotes(text: str) -> str:
    text = re.sub(r"^\[\^[^\]]+\]:[ \t]*.+$", "", text, flags=re.MULTILINE)
    text = re.sub(r"\[\^[^\]]+\]", "", text)
    return text

def mrkdwnify(markdown: str) -> str:
    return MrkdwnConverter(_strip_footnotes(markdown)).convert()
```

### Tests (write first)
```
test_footnote_ref_stripped          "text[^1]\n\n[^1]: note"       → "text\n"
test_footnote_multi_stripped        "a[^1] b[^2]\n\n[^1]: x\n[^2]: y"  → "a b\n"
test_footnote_def_only_stripped     "[^1]: just a note"            → ""
test_footnote_no_corrupted_link     "text[^1]"                     → "text\n"  (no <...|^1>)
test_normal_link_preserved          "[normal](http://x.com)"       → "<http://x.com|normal>\n"
test_ref_link_preserved             "[text][id]\n\n[id]: http://x" → "<http://x|text>\n"
```

### How to verify in Slack
Take any AI-generated response that contains footnotes (e.g. from Claude or GPT).
Run it through `mrkdwnify`. Confirm: no `<note|^1>` artifacts appear, footnote markers
are cleanly removed, and the text reads naturally.

---

## Module 3 — Horizontal Rules
**File:** `src/mrkdwnify/converter.py`  
**Status:** `[ ]`  
**Bug:** B3 · **Tests to add:** `tests/test_misc.py`

### What breaks today
`hr` is not in `SUPPORTED_TOKENS` so `---`, `***`, `___` are silently dropped.
Slack has no native horizontal rule, but a visible separator is far better than nothing.

### Implementation
Add `"hr"` to `SUPPORTED_TOKENS` and add a handler:

```python
def hr(self, tokens: list[Token], idx: int, options: dict[str, Any], env: dict[str, Any]) -> str:
    return "────────────────────\n\n"
```

### Tests (write first)
```
test_hr_dash            "---"                   → "────────────────────\n\n"
test_hr_star            "***"                   → "────────────────────\n\n"
test_hr_underscore      "___"                   → "────────────────────\n\n"
test_hr_between_text    "above\n\n---\n\nbelow" → "above\n────────────────────\n\nbelow\n"
```

### How to verify in Slack
Send a message like `Section A\n\n---\n\nSection B`.
Confirm a visible line of `────` appears between the two sections.

---

## Module 4 — Blockquotes
**File:** `src/mrkdwnify/converter.py`  
**Status:** `[ ]`  
**Bugs:** B1, B2 · **Tests to add:** `tests/test_blockquotes.py`

### What breaks today
`blockquote_open` emits `"> "` for the opening, but every subsequent block inside
the quote (`paragraph_open`, `list_item_open`) returns `""` — so anything after
the first line loses its `> ` prefix entirely.

### Root cause & fix
Move `"> "` from `blockquote_open` → `paragraph_open` and `list_item_open`:

```python
def blockquote_open(self, ...) -> str:
    self._in_blockquote += 1
    return ""                               # was "> "

def paragraph_open(self, ...) -> str:
    if self._in_blockquote > 0 and self._list_depth == 0:
        return "> "
    return ""

def list_item_open(self, ...) -> str:
    prefix = "> " if self._in_blockquote > 0 else ""
    indent = "    " * (self._list_depth - 1)
    return (f"{prefix}{indent}{tokens[idx].info}.  "
            if tokens[idx].info else f"{prefix}{indent}•   ")
```

`softbreak` and `hardbreak` already return `"\n> "` inside blockquotes (v0.2.0).

### Tests (write first — starred ones are currently failing)
```
test_single_line_blockquote         "> text"                 → "> text\n\n"
test_multiline_blockquote           "> L1\n> L2\n> L3"       → "> L1\n> L2\n> L3\n\n"      (passing)
test_multi_paragraph_blockquote ★  "> P1\n>\n> P2"          → "> P1\n> P2\n\n"             (B1)
test_list_inside_blockquote ★      "> - a\n> - b"           → "> •   a\n> •   b\n\n"       (B2)
test_blockquote_with_bold           "> **bold** text"        → "> *bold* text\n\n"
test_blockquote_with_inline_code    "> `code`"               → "> `code`\n\n"
test_blockquote_with_link           "> [x](http://a.com)"   → "> <http://a.com|x>\n\n"
```

### How to verify in Slack
Post:
```
> This is paragraph one of a blockquote.
>
> This is paragraph two — it must also have the grey left border.
```
Confirm **both** paragraphs render with Slack's grey left-border, not just the first.
Then post a blockquote containing a list and confirm each bullet is also quoted.

---

## Module 5 — Links
**File:** `src/mrkdwnify/converter.py`  
**Status:** `[ ]`  
**Bug:** B5 · **Tests to add:** `tests/test_links.py`

### What breaks today
`link_close` has a dead branch: `tokens[idx].content` is never set on a `link_close`
token in markdown-it, so `f">: {content}\n"` never executes. Misleading dead code.

### Implementation
Simplify `link_close` to just `return ">"`.

Then add tests for edge cases not yet covered:

### Tests (write first)
```
test_email_link                 "[e](mailto:a@b.com)"           → "<mailto:a@b.com|e>\n"
test_bold_inside_link           "[**b**](http://x.com)"         → "<http://x.com|*b*>\n"
test_italic_inside_link         "[_i_](http://x.com)"           → "<http://x.com|_i_>\n"
test_link_followed_by_punct     "[a](http://x.com)."            → "<http://x.com|a>.\n"
test_link_display_with_amp      "[a & b](http://x.com)"         → "<http://x.com|a &amp; b>\n"
test_link_close_simplified      any link                        → no ">: content" ever appears
```

### How to verify in Slack
Post `[**bold link**](https://example.com)` converted via `mrkdwnify`.
Confirm it renders as a clickable link with **bold** display text in Slack.

---

## Module 6 — Code Blocks
**File:** `src/mrkdwnify/converter.py`  
**Status:** `[ ]`  
**Tests to add:** `tests/test_code.py`

### What works, what's missing
Current code handles: fenced blocks, language stripping, `#!` shebang removal, inline code.  
Missing tests for: special chars inside code (must NOT be HTML-escaped), empty blocks, indented code.

### Tests (write first)
```
test_empty_fence                    "```\n```"                       → "```\n```\n"
test_fence_preserves_special_chars  "```\nfoo & <bar>\n```"          → "```\nfoo & <bar>\n```\n"
test_inline_code_preserves_specials "`foo & <bar>`"                  → "`foo & <bar>`\n"
test_inline_code_not_formatted      "`**not bold**`"                 → "`**not bold**`\n"
test_fence_with_emoji               "```\n:wave:\n```"               → "```\n:wave:\n```\n"
```

### How to verify in Slack
Post a code block containing `&`, `<`, `>`. Confirm they appear as literal characters
inside the code block, not as HTML entities.

---

## Module 7 — Inline Formatting
**File:** `src/mrkdwnify/converter.py`  
**Status:** `[ ]`  
**Tests to add:** `tests/test_inline.py`

### What works, what's missing
Core formatting (bold, italic, strike, inline code) all work.
Missing edge case coverage.

### Tests (write first)
```
test_bold_with_punctuation          "**done!**"                 → "*done!*\n"
test_nested_bold_italic             "**_both_**"                → "*_both_*\n"
test_strike_in_list                 "- ~~done~~"                → "•   ~done~\n"
test_formatting_with_specials       "**foo & bar**"             → "*foo &amp; bar*\n"
test_all_three_inline               "**b** _i_ ~~s~~"           → "*b* _i_ ~s~\n"
test_mid_word_bold                  "he**l**lo"                 → "he*l*lo\n"  (passing)
```

### How to verify in Slack
Post a message containing bold, italic, and strikethrough in the same line.
Confirm all three render correctly without interfering with each other.

---

## Module 8 — Headings
**File:** `src/mrkdwnify/converter.py`  
**Status:** `[ ]`  
**Tests to add:** `tests/test_headings.py`

### What works, what's missing
All heading levels → bold works. Missing coverage for formatting inside headings.

### Tests (write first)
```
test_h1_through_h6              h1…h6 all produce  "*text*\n\n"
test_heading_with_strike        "# ~~text~~"        → "*~text~*\n\n"
test_heading_with_link          "# [t](http://x)"   → "*<http://x|t>*\n\n"
test_heading_with_inline_code   "# `code`"          → "*`code`*\n\n"
test_heading_with_italic        "# *em*"            → "*_em_*\n\n"  (passing)
```

### How to verify in Slack
Post several heading levels with different inline formatting inside.
Confirm all headings appear as bold in Slack regardless of heading level,
and that formatting inside the heading (italic, code) renders correctly.

---

## Module 9 — Lists
**File:** `src/mrkdwnify/converter.py`  
**Status:** `[ ]`  
**Tests to add:** `tests/test_lists.py`

### What works, what's missing
Nested lists (2 levels) fixed in v0.2.0. Missing tests for 3+ levels and mixed nesting.

### Tests (write first)
```
test_three_level_nesting        "- A\n  - B\n    - C"       → "•   A\n    •   B\n        •   C\n"
test_list_item_with_formatting  "- **bold** and _italic_"   → "•   *bold* and _italic_\n"
test_deeply_nested_mixed        "1. A\n   - B\n     1. C"   → "1.  A\n    •   B\n        1.  C\n"
test_ordered_with_formatting    "1. **Item**\n2. _Item_"    → "1.  *Item*\n2.  _Item_\n"
```

### How to verify in Slack
Post a 3-level nested list. Confirm each level is visually indented further right,
and that formatting inside list items (bold, italic) renders correctly.

---

## Module 10 — Images
**File:** `src/mrkdwnify/converter.py`  
**Status:** `[ ]`  
**Tests to add:** `tests/test_images.py`

### What works, what's missing
All reference-style and inline image variants are tested. Missing: images inside other blocks.

### Tests (write first)
```
test_image_in_list              "- ![alt](http://x.com/i.png)"   → "•   <http://x.com/i.png|alt>\n"
test_image_in_blockquote        "> ![alt](http://x.com/i.png)"   → "> <http://x.com/i.png|alt>\n\n"
test_image_no_alt_no_title      "![](http://x.com/i.png)"        → "<http://x.com/i.png>\n"  (passing)
```

### How to verify in Slack
Post a message containing an image URL formatted as `<url|alt>`. Confirm Slack
shows a link (and in some views, an image preview) with the correct alt text.

---

## Completion Checklist

| # | Module | Bug fixed | Tests | Status |
|---|--------|-----------|-------|--------|
| 1 | Escaping & Special Characters | B6 | `test_escape.py` | `[ ]` |
| 2 | Footnotes & Unsupported Syntax | B4 | `test_footnotes.py` | `[ ]` |
| 3 | Horizontal Rules | B3 | `test_misc.py` | `[ ]` |
| 4 | Blockquotes | B1, B2 | `test_blockquotes.py` | `[ ]` |
| 5 | Links | B5 | `test_links.py` | `[ ]` |
| 6 | Code Blocks | — | `test_code.py` | `[ ]` |
| 7 | Inline Formatting | — | `test_inline.py` | `[ ]` |
| 8 | Headings | — | `test_headings.py` | `[ ]` |
| 9 | Lists | — | `test_lists.py` | `[ ]` |
| 10 | Images | — | `test_images.py` | `[ ]` |

---

## Version Targets

| Version | Modules completed | Notes |
|---------|-------------------|-------|
| **v0.3.0** | 1–5 | All known bugs fixed — publish to PyPI |
| **v0.4.0** | 6–10 | Full edge case coverage |
| **v1.0.0** | — | Block Kit output: `mrkdwnify(text, output="blocks")` |
| **v1.1.0** | — | AI templates + prompt helpers |
