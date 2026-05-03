from mrkdwnify import mrkdwnify


def test_hr_dash():
    assert mrkdwnify("---") == "────────────────────\n\n"


def test_hr_star():
    assert mrkdwnify("***") == "────────────────────\n\n"


def test_hr_underscore():
    assert mrkdwnify("___") == "────────────────────\n\n"


def test_hr_between_text():
    assert mrkdwnify("above\n\n---\n\nbelow") == "above\n────────────────────\n\nbelow\n"
