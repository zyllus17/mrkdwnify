from mrkdwnify import mrkdwnify


def test_bold_with_punctuation():
    assert mrkdwnify("**done!**") == "*done!*\n"


def test_nested_bold_italic():
    assert mrkdwnify("**_both_**") == "*_both_*\n"


def test_strike_in_list():
    assert mrkdwnify("- ~~done~~") == "•   ~done~\n"


def test_formatting_with_specials():
    assert mrkdwnify("**foo & bar**") == "*foo &amp; bar*\n"


def test_all_three_inline():
    assert mrkdwnify("**b** _i_ ~~s~~") == "*b* _i_ ~s~\n"


def test_mid_word_bold():
    assert mrkdwnify("he**l**lo") == "he*l*lo\n"
