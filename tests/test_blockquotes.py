from mrkdwnify import mrkdwnify


def test_single_line_blockquote():
    assert mrkdwnify("> text") == "> text\n\n"


def test_multiline_blockquote():
    assert mrkdwnify("> L1\n> L2\n> L3") == "> L1\n> L2\n> L3\n\n"


def test_multi_paragraph_blockquote():
    assert mrkdwnify("> P1\n>\n> P2") == "> P1\n> P2\n\n"


def test_list_inside_blockquote():
    assert mrkdwnify("> - a\n> - b") == "> •   a\n> •   b\n\n"


def test_blockquote_with_bold():
    assert mrkdwnify("> **bold** text") == "> *bold* text\n\n"


def test_blockquote_with_inline_code():
    assert mrkdwnify("> `code`") == "> `code`\n\n"


def test_blockquote_with_link():
    assert mrkdwnify("> [x](http://a.com)") == "> <http://a.com|x>\n\n"
