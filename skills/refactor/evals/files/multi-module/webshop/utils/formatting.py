"""Money/string formatting helpers."""


def format_money(amount):
    return "{:,.2f}".format(amount)


def truncate(text, limit=80):
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."
