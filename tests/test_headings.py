import pytest

from mrkdwnify import mrkdwnify


@pytest.mark.parametrize("level", range(1, 7))
def test_h1_through_h6(level: int):
    prefix = "#" * level
    assert mrkdwnify(f"{prefix} text") == "*text*\n\n"


def test_heading_with_strike():
    assert mrkdwnify("# ~~text~~") == "*~text~*\n\n"


def test_heading_with_link():
    assert mrkdwnify("# [t](http://x)") == "*<http://x|t>*\n\n"


def test_heading_with_inline_code():
    assert mrkdwnify("# `code`") == "*`code`*\n\n"


def test_heading_with_italic():
    assert mrkdwnify("# *em*") == "*_em_*\n\n"
