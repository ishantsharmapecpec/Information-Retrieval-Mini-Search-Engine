from collections import defaultdict

from .tokenizer import tokenize


class InvertedIndex:

    def __init__(self):

        # term -> document_id -> [token positions]
        self.index = defaultdict(
            lambda: defaultdict(list)
        )

        # Basic document information
        self.documents = {}
        self.titles = {}
        self.paths = {}

        # document_id -> token list
        self.tokens = {}

        # document_id -> {page_number: page_text}
        self.pages = {}

    @property
    def document_count(self):
        return len(self.documents)

    def add_document(
        self,
        document_id: int,
        title: str,
        path: str,
        text: str,
        pages: dict[int, str] | None = None
    ):

        tokens = tokenize(text)

        self.documents[document_id] = text
        self.titles[document_id] = title
        self.paths[document_id] = path
        self.tokens[document_id] = tokens

        if pages is None:
            pages = {1: text}

        self.pages[document_id] = pages

        for position, token in enumerate(tokens):

            self.index[token][document_id].append(
                position
            )

    def documents_for_term(
        self,
        term: str
    ) -> set[int]:

        term = term.lower()

        if term not in self.index:
            return set()

        return set(
            self.index[term].keys()
        )

    def positions(
        self,
        term: str,
        document_id: int
    ) -> list[int]:

        term = term.lower()

        return self.index.get(
            term,
            {}
        ).get(
            document_id,
            []
        )

    def all_document_ids(self) -> set[int]:

        return set(
            self.documents.keys()
        )

    def get_term_count(
        self,
        document_id: int,
        term: str
    ) -> int:

        term = term.lower()

        return len(
            self.index.get(
                term,
                {}
            ).get(
                document_id,
                []
            )
        )

    def get_term_pages(
        self,
        document_id: int,
        term: str
    ) -> list[int]:

        term = term.lower()

        pages_found = []

        document_pages = self.pages.get(
            document_id,
            {}
        )

        for page_number, text in document_pages.items():

            page_tokens = tokenize(text)

            if term in page_tokens:
                pages_found.append(page_number)

        return pages_found

    def get_phrase_pages(
        self,
        document_id: int,
        phrase: str
    ) -> list[int]:

        phrase = phrase.lower()

        pages_found = []

        document_pages = self.pages.get(
            document_id,
            {}
        )

        for page_number, text in document_pages.items():

            if phrase in text.lower():
                pages_found.append(page_number)

        return pages_found

    def get_phrase_count(
        self,
        document_id: int,
        phrase: str
    ) -> int:

        phrase = phrase.lower()

        total = 0

        document_pages = self.pages.get(
            document_id,
            {}
        )

        for text in document_pages.values():

            total += text.lower().count(
                phrase
            )

        return total
