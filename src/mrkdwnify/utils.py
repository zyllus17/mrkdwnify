import re


def escape_specials(text: str) -> str:
    text = re.sub(r"&", r"&amp;", text)
    text = re.sub(r"<(?![@#!])", r"&lt;", text)

    slack_mentions = [(m.start(), m.end()) for m in re.finditer(r"<[@#!][^>]*>", text)]

    result = ""
    for i, char in enumerate(text):
        if char == ">":
            in_mention = any(start <= i < end for start, end in slack_mentions)
            result += ">" if in_mention else "&gt;"
        else:
            result += char

    return result
