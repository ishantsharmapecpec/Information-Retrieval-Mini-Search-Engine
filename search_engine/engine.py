import math

from .index import InvertedIndex
from .models import SearchResult
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
        text: str
    ):
        self.index.add_document(
            document_id=document_id,
            title=title,
            path=path,
            text=text
        )

    def search(
        self,
        query: str,
        limit: int = 5
    ) -> list[SearchResult]:

        query = query.strip()

        if not query:
            return []

        # -----------------------------------------
        # Phrase Search
        # -----------------------------------------

        if is_phrase_query(query):

            phrase = query[1:-1]

            document_ids = self.phrase_search(
                phrase
            )

            return self._build_results(
                document_ids,
                query,
                limit
            )

        # -----------------------------------------
        # Boolean Search
        # -----------------------------------------

        boolean_query = parse_boolean_query(query)

        if boolean_query:

            operator, left, right = boolean_query

            document_ids = self.boolean_search(
                operator,
                left,
                right
            )

            return self._build_results(
                document_ids,
                query,
                limit
            )

        # -----------------------------------------
        # Ranked TF-IDF Search
        # -----------------------------------------

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

        total_documents = self.index.document_count

        if total_documents == 0:
            return []

        for term in query_tokens:

            documents = self.index.documents_for_term(
                term
            )

            document_frequency = len(documents)

            if document_frequency == 0:
                continue

            idf = math.log(
                total_documents /
                document_frequency
            )

            for document_id in documents:

                tokens = self.index.tokens[
                    document_id
                ]

                term_frequency = tokens.count(term)

                tf = (
                    term_frequency /
                    len(tokens)
                    if tokens
                    else 0
                )

                score = tf * idf

                scores[document_id] = (
                    scores.get(document_id, 0)
                    + score
                )

        ranked = sorted(
            scores.items(),
            key=lambda item: item[1],
            reverse=True
        )

        results = []

        for document_id, score in ranked[:limit]:

            results.append(
                SearchResult(
                    title=self.index.titles[document_id],
                    path=self.index.paths[document_id],
                    score=round(score, 4),
                    snippet=self._create_snippet(
                        document_id,
                        query_tokens
                    )
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

        left_docs = self.index.documents_for_term(
            left_tokens[0]
        )

        if not right_tokens:
            return left_docs

        right_docs = self.index.documents_for_term(
            right_tokens[0]
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

                    if required_position not in token_positions:
                        matched = False
                        break

                if matched:
                    matches.add(document_id)
                    break

        return matches

    def _build_results(
        self,
        document_ids: set[int],
        query: str,
        limit: int
    ) -> list[SearchResult]:

        query_tokens = tokenize(query)

        results = []

        for document_id in list(document_ids)[:limit]:

            results.append(
                SearchResult(
                    title=self.index.titles[document_id],
                    path=self.index.paths[document_id],
                    score=1.0,
                    snippet=self._create_snippet(
                        document_id,
                        query_tokens
                    )
                )
            )

        return results

    def _create_snippet(
        self,
        document_id: int,
        query_tokens: list[str],
        length: int = 300
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
            return text[:length].strip()

        start = max(
            0,
            position - 100
        )

        end = min(
            len(text),
            position + length
        )

        snippet = text[start:end].strip()

        if start > 0:
            snippet = "..." + snippet

        if end < len(text):
            snippet = snippet + "..."

        return snippet
