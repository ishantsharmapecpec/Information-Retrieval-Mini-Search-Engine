import re


def is_phrase_query(query: str) -> bool:
    query = query.strip()

    return (
        len(query) >= 2
        and query.startswith('"')
        and query.endswith('"')
    )


def parse_boolean_query(query: str):
    """
    Supports simple queries such as:

    london AND clay
    pile OR raft
    clay NOT sand
    """

    tokens = query.strip().split()

    upper_tokens = [token.upper() for token in tokens]

    if "AND" in upper_tokens:

        index = upper_tokens.index("AND")

        left = " ".join(tokens[:index])
        right = " ".join(tokens[index + 1:])

        return "AND", left, right

    if "OR" in upper_tokens:

        index = upper_tokens.index("OR")

        left = " ".join(tokens[:index])
        right = " ".join(tokens[index + 1:])

        return "OR", left, right

    if "NOT" in upper_tokens:

        index = upper_tokens.index("NOT")

        left = " ".join(tokens[:index])
        right = " ".join(tokens[index + 1:])

        return "NOT", left, right

    return None
