import re


def tokenize(text: str) -> list[str]:
   

    return re.findall(r"\b[a-zA-Z0-9]+\b", text.lower())
