def is_phrase_query(query: str) -> bool:
    query = query.strip()

    return (
        len(query) >= 2
        and query.startswith('"')
        and query.endswith('"')
    )


def parse_boolean_query(query: str):
    """
    Supports simple Boolean queries:

    pile AND load
    pile OR raft
    clay NOT sand
    """

    tokens = query.strip().split()
    upper_tokens = [token.upper() for token in tokens]

    for operator in ["AND", "OR", "NOT"]:

        if operator in upper_tokens:

            index = upper_tokens.index(operator)

            left = " ".join(tokens[:index]).strip()
            right = " ".join(tokens[index + 1:]).strip()

            if left and right:
                return operator, left, right

    return None
