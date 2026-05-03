from mrkdwnify.utils import escape_specials


def test_escape_ampersand():
    assert escape_specials("&") == "&amp;"


def test_escape_less_than():
    assert escape_specials("<tag>") == "&lt;tag&gt;"


def test_escape_greater_than():
    assert escape_specials("a > b") == "a &gt; b"


def test_preserve_user_mention():
    assert escape_specials("<@U123>") == "<@U123>"


def test_preserve_channel_mention():
    assert escape_specials("<#C123>") == "<#C123>"


def test_preserve_special_mention():
    assert escape_specials("<!here>") == "<!here>"


def test_preserve_subteam():
    assert escape_specials("<!subteam^S1|team>") == "<!subteam^S1|team>"


def test_mixed_mentions_and_text():
    assert escape_specials("<@U1> & <tag>") == "<@U1> &amp; &lt;tag&gt;"


def test_empty_string():
    assert escape_specials("") == ""


def test_multiple_mentions():
    assert escape_specials("<@A> text <@B>") == "<@A> text <@B>"
