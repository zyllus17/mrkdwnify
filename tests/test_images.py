from mrkdwnify import mrkdwnify


def test_image_in_list():
    assert mrkdwnify("- ![alt](http://x.com/i.png)") == "•   <http://x.com/i.png|alt>\n"


def test_image_in_blockquote():
    assert mrkdwnify("> ![alt](http://x.com/i.png)") == "> <http://x.com/i.png|alt>\n\n"


def test_image_no_alt_no_title():
    assert mrkdwnify("![](http://x.com/i.png)") == "<http://x.com/i.png>\n"
