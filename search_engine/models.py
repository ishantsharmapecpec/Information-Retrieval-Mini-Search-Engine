from dataclasses import dataclass, field


@dataclass
class TermMatch:
    term: str
    count: int
    pages: list[int] = field(default_factory=list)


@dataclass
class SearchResult:
    document_id: int
    title: str
    path: str
    score: float
    snippet: str
    term_matches: list[TermMatch] = field(default_factory=list)
    match_type: str = ""
