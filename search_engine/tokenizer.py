import re


def tokenize(text: str) -> list[str]:
    """
    Convert text into lowercase alphanumeric tokens.

    Example:
    "London Clay is stiff."
    becomes:
    ["london", "clay", "is", "stiff"]
    """
    return re.findall(r"\b[a-zA-Z0-9]+\b", text.lower())
