import math

from .index import InvertedIndex
from .models import SearchResult, TermMatch
from .query_parser import (
    is_phrase_query,
    parse_boolean_query
)
from .tokenizer import tokenize


class SearchEngine:

    def __init__(self):

        self.index = InvertedIndex()

    def add_document(
        self,
        document_id: int,
        title: str,
        path: str,
        text: str,
        pages: dict[int, str] | None = None
    ):

        self.index.add_document(
            document_id=document_id,
            title=title,
            path=path,
            text=text,
            pages=pages
        )

    def search(
        self,
        query: str,
        limit: int = 5
    ) -> list[SearchResult]:

        query = query.strip()

        if not query:
            return []

        # -----------------------------
        # PHRASE SEARCH
        # -----------------------------

        if is_phrase_query(query):

            phrase = query[1:-1]

            document_ids = self.phrase_search(
                phrase
            )

            return self._build_phrase_results(
                document_ids,
                phrase,
                limit
            )

        # -----------------------------
        # BOOLEAN SEARCH
        # -----------------------------

        boolean_query = parse_boolean_query(
            query
        )

        if boolean_query:

            operator, left, right = boolean_query

            document_ids = self.boolean_search(
                operator,
                left,
                right
            )

            return self._build_boolean_results(
                document_ids,
                operator,
                left,
                right,
                limit
            )

        # -----------------------------
        # TF-IDF SEARCH
        # -----------------------------

        return self.tfidf_search(
            query,
            limit
        )

    def tfidf_search(
        self,
        query: str,
        limit: int
    ) -> list[SearchResult]:

        query_tokens = tokenize(query)

        scores = {}

        total_documents = (
            self.index.document_count
        )

        if total_documents == 0:
            return []

        for term in query_tokens:

            documents = (
                self.index.documents_for_term(
                    term
                )
            )

            document_frequency = len(
                documents
            )

            if document_frequency == 0:
                continue

            # Smoothed IDF so a single-document
            # search does not produce score 0
            idf = math.log(
                (total_documents + 1)
                /
                (document_frequency + 1)
            ) + 1

            for document_id in documents:

                tokens = self.index.tokens[
                    document_id
                ]

                if not tokens:
                    continue

                term_frequency = (
                    tokens.count(term)
                    /
                    len(tokens)
                )

                score = (
                    term_frequency * idf
                )

                scores[document_id] = (
                    scores.get(
                        document_id,
                        0
                    )
                    + score
                )

        ranked = sorted(
            scores.items(),
            key=lambda item: item[1],
            reverse=True
        )

        results = []

        for document_id, score in ranked[:limit]:

            term_matches = []

            for term in query_tokens:

                count = (
                    self.index.get_term_count(
                        document_id,
                        term
                    )
                )

                pages = (
                    self.index.get_term_pages(
                        document_id,
                        term
                    )
                )

                term_matches.append(
                    TermMatch(
                        term=term,
                        count=count,
                        pages=pages
                    )
                )

            results.append(
                SearchResult(
                    document_id=document_id,
                    title=self.index.titles[
                        document_id
                    ],
                    path=self.index.paths[
                        document_id
                    ],
                    score=round(
                        score,
                        6
                    ),
                    snippet=self._create_snippet(
                        document_id,
                        query_tokens
                    ),
                    term_matches=term_matches,
                    match_type="TF-IDF Ranked Search"
                )
            )

        return results

    def boolean_search(
        self,
        operator: str,
        left: str,
        right: str
    ) -> set[int]:

        left_tokens = tokenize(left)
        right_tokens = tokenize(right)

        if not left_tokens:
            return set()

        left_docs = (
            self.index.documents_for_term(
                left_tokens[0]
            )
        )

        if not right_tokens:
            return left_docs

        right_docs = (
            self.index.documents_for_term(
                right_tokens[0]
            )
        )

        if operator == "AND":
            return left_docs & right_docs

        if operator == "OR":
            return left_docs | right_docs

        if operator == "NOT":
            return left_docs - right_docs

        return set()

    def phrase_search(
        self,
        phrase: str
    ) -> set[int]:

        phrase_tokens = tokenize(phrase)

        if not phrase_tokens:
            return set()

        candidate_documents = (
            self.index.documents_for_term(
                phrase_tokens[0]
            )
        )

        for token in phrase_tokens[1:]:

            candidate_documents &= (
                self.index.documents_for_term(
                    token
                )
            )

        matches = set()

        for document_id in candidate_documents:

            first_positions = (
                self.index.positions(
                    phrase_tokens[0],
                    document_id
                )
            )

            for start_position in first_positions:

                matched = True

                for offset, token in enumerate(
                    phrase_tokens[1:],
                    start=1
                ):

                    required_position = (
                        start_position + offset
                    )

                    token_positions = (
                        self.index.positions(
                            token,
                            document_id
                        )
                    )

                    if (
                        required_position
                        not in token_positions
                    ):
                        matched = False
                        break

                if matched:
                    matches.add(
                        document_id
                    )
                    break

        return matches

    def _build_boolean_results(
        self,
        document_ids: set[int],
        operator: str,
        left: str,
        right: str,
        limit: int
    ) -> list[SearchResult]:

        results = []

        left_tokens = tokenize(left)
        right_tokens = tokenize(right)

        terms = []

        if left_tokens:
            terms.append(left_tokens[0])

        if right_tokens:
            terms.append(right_tokens[0])

        for document_id in list(
            document_ids
        )[:limit]:

            term_matches = []

            for term in terms:

                count = (
                    self.index.get_term_count(
                        document_id,
                        term
                    )
                )

                pages = (
                    self.index.get_term_pages(
                        document_id,
                        term
                    )
                )

                term_matches.append(
                    TermMatch(
                        term=term,
                        count=count,
                        pages=pages
                    )
                )

            results.append(
                SearchResult(
                    document_id=document_id,
                    title=self.index.titles[
                        document_id
                    ],
                    path=self.index.paths[
                        document_id
                    ],
                    score=1.0,
                    snippet=self._create_snippet(
                        document_id,
                        terms
                    ),
                    term_matches=term_matches,
                    match_type=(
                        f"Boolean {operator}"
                    )
                )
            )

        return results

    def _build_phrase_results(
        self,
        document_ids: set[int],
        phrase: str,
        limit: int
    ) -> list[SearchResult]:

        results = []

        for document_id in list(
            document_ids
        )[:limit]:

            phrase_count = (
                self.index.get_phrase_count(
                    document_id,
                    phrase
                )
            )

            phrase_pages = (
                self.index.get_phrase_pages(
                    document_id,
                    phrase
                )
            )

            term_matches = [
                TermMatch(
                    term=f'"{phrase}"',
                    count=phrase_count,
                    pages=phrase_pages
                )
            ]

            results.append(
                SearchResult(
                    document_id=document_id,
                    title=self.index.titles[
                        document_id
                    ],
                    path=self.index.paths[
                        document_id
                    ],
                    score=1.0,
                    snippet=self._create_snippet(
                        document_id,
                        tokenize(phrase)
                    ),
                    term_matches=term_matches,
                    match_type="Exact Phrase Search"
                )
            )

        return results

    def _create_snippet(
        self,
        document_id: int,
        query_tokens: list[str],
        length: int = 350
    ) -> str:

        text = self.index.documents[
            document_id
        ]

        lower_text = text.lower()

        position = -1

        for token in query_tokens:

            position = lower_text.find(
                token.lower()
            )

            if position != -1:
                break

        if position == -1:

            return text[
                :length
            ].strip()

        start = max(
            0,
            position - 120
        )

        end = min(
            len(text),
            position + length
        )

        snippet = text[
            start:end
        ].strip()

        if start > 0:
            snippet = "..." + snippet

        if end < len(text):
            snippet = snippet + "..."

        return snippet
