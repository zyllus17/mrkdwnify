from mrkdwnify import mrkdwnify


def test_empty_fence():
    assert mrkdwnify("```\n```") == "```\n```\n"


def test_fence_preserves_special_chars():
    assert mrkdwnify("```\nfoo & <bar>\n```") == "```\nfoo & <bar>\n```\n"


def test_inline_code_preserves_specials():
    assert mrkdwnify("`foo & <bar>`") == "`foo & <bar>`\n"


def test_inline_code_not_formatted():
    assert mrkdwnify("`**not bold**`") == "`**not bold**`\n"


def test_fence_with_emoji():
    assert mrkdwnify("```\n:wave:\n```") == "```\n:wave:\n```\n"
