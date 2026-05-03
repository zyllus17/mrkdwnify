from mrkdwnify import mrkdwnify


def test_three_level_nesting():
    assert mrkdwnify("- A\n  - B\n    - C") == "•   A\n    •   B\n        •   C\n"


def test_list_item_with_formatting():
    assert mrkdwnify("- **bold** and _italic_") == "•   *bold* and _italic_\n"


def test_deeply_nested_mixed():
    assert mrkdwnify("1. A\n   - B\n     1. C") == "1.  A\n    •   B\n        1.  C\n"


def test_ordered_with_formatting():
    assert mrkdwnify("1. **Item**\n2. _Item_") == "1.  *Item*\n2.  _Item_\n"
