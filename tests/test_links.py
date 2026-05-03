from mrkdwnify import mrkdwnify


def test_email_link():
    assert mrkdwnify("[e](mailto:a@b.com)") == "<mailto:a@b.com|e>\n"


def test_bold_inside_link():
    assert mrkdwnify("[**b**](http://x.com)") == "<http://x.com|*b*>\n"


def test_italic_inside_link():
    assert mrkdwnify("[_i_](http://x.com)") == "<http://x.com|_i_>\n"


def test_link_followed_by_punct():
    assert mrkdwnify("[a](http://x.com).") == "<http://x.com|a>.\n"


def test_link_display_with_amp():
    assert mrkdwnify("[a & b](http://x.com)") == "<http://x.com|a &amp; b>\n"


def test_link_close_no_dead_branch():
    result = mrkdwnify("[text](http://x.com)")
    assert ">: " not in result
