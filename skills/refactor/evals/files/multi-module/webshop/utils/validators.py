"""Validation helpers available project-wide."""

import re

EMAIL_RE = re.compile(r"^[\w.+-]+@[\w-]+\.[\w.]+$")


def is_valid_email(value):
    return bool(value) and bool(EMAIL_RE.match(value))


def is_valid_phone(value):
    digits = re.sub(r"\D", "", value or "")
    return 9 <= len(digits) <= 11


def normalize_phone(value):
    return re.sub(r"\D", "", value or "")
