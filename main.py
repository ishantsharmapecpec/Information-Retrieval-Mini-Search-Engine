"""Command-line interface for the Mini Search Engine."""

from __future__ import annotations

import argparse
from pathlib import Path

from search_engine import SearchEngine


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Mini Search Engine")
    parser.add_argument("query", nargs="?", help="Search query. Use quotes for phrase search.")
    parser.add_argument("--docs", default="data/sample_docs", help="Folder containing .txt documents")
    parser.add_argument("--limit", type=int, default=5, help="Maximum number of results")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    docs_folder = Path(args.docs)
    engine = SearchEngine.from_folder(docs_folder)

    if args.query:
        show_results(engine, args.query, args.limit)
        return

    print(f"Indexed {engine.index.document_count} documents from {docs_folder}")
    print("Type a query, or type 'exit' to quit. Examples:")
    print('  london clay')
    print('  "london clay"')
    print('  pile AND load')
    print('  clay NOT sand')

    while True:
        query = input("search> ").strip()
        if query.lower() in {"exit", "quit"}:
            break
        if not query:
            continue
        show_results(engine, query, args.limit)


def show_results(engine: SearchEngine, query: str, limit: int) -> None:
    results = engine.search(query, limit=limit)
    if not results:
        print("No results found.")
        return

    for rank, result in enumerate(results, start=1):
        print(f"\n{rank}. {result.title}  score={result.score}")
        print(f"   {result.path}")
        print(f"   {result.snippet}")


if __name__ == "__main__":
    main()
