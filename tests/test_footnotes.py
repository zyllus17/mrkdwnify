from mrkdwnify import mrkdwnify


def test_footnote_ref_stripped():
    assert mrkdwnify("text[^1]\n\n[^1]: note") == "text\n"


def test_footnote_multi_stripped():
    assert mrkdwnify("a[^1] b[^2]\n\n[^1]: x\n[^2]: y") == "a b\n"


def test_footnote_def_only_stripped():
    assert mrkdwnify("[^1]: just a note") == ""


def test_footnote_no_corrupted_link():
    result = mrkdwnify("text[^1]")
    assert result == "text\n"
    assert "|^1>" not in result


def test_normal_link_preserved():
    assert mrkdwnify("[normal](http://x.com)") == "<http://x.com|normal>\n"


def test_ref_link_preserved():
    assert mrkdwnify("[text][id]\n\n[id]: http://x") == "<http://x|text>\n"
