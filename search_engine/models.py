
from dataclasses import dataclass


@dataclass
class SearchResult:
    title: str
    path: str
    score: float
    snippet: str
