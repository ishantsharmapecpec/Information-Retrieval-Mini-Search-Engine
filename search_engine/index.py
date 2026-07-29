from collections import defaultdict
from pathlib import Path

from .tokenizer import tokenize


class InvertedIndex:

    def __init__(self):
        # term -> document_id -> [positions]
        self.index = defaultdict(lambda: defaultdict(list))

        # document_id -> full text
        self.documents = {}

        # document_id -> document title
        self.titles = {}

        # document_id -> source path/name
        self.paths = {}

        # document_id -> tokens
        self.tokens = {}

    @property
    def document_count(self):
        return len(self.documents)

    def add_document(
        self,
        document_id: int,
        title: str,
        path: str,
        text: str
    ):

        tokens = tokenize(text)

        self.documents[document_id] = text
        self.titles[document_id] = title
        self.paths[document_id] = path
        self.tokens[document_id] = tokens

        for position, token in enumerate(tokens):
            self.index[token][document_id].append(position)

    def documents_for_term(self, term: str) -> set[int]:

        term = term.lower()

        if term not in self.index:
            return set()

        return set(self.index[term].keys())

    def positions(self, term: str, document_id: int) -> list[int]:

        term = term.lower()

        return self.index.get(term, {}).get(
            document_id,
            []
        )

    def all_document_ids(self) -> set[int]:

        return set(self.documents.keys())
