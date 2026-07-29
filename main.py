from pathlib import Path

from search_engine import SearchEngine


def load_txt_folder(
    folder: Path
) -> SearchEngine:

    engine = SearchEngine()

    files = sorted(
        folder.glob("*.txt")
    )

    for document_id, file_path in enumerate(
        files
    ):

        text = file_path.read_text(
            encoding="utf-8",
            errors="ignore"
        )

        engine.add_document(
            document_id=document_id,
            title=file_path.name,
            path=str(file_path),
            text=text,
            pages={1: text}
        )

    return engine


def show_results(
    engine: SearchEngine,
    query: str,
    limit: int
):

    results = engine.search(
        query,
        limit=limit
    )

    if not results:

        print(
            "No results found."
        )

        return

    for rank, result in enumerate(
        results,
        start=1
    ):

        print(
            f"\n{rank}. {result.title}"
        )

        print(
            f"Search type: "
            f"{result.match_type}"
        )

        print(
            f"Score: "
            f"{result.score}"
        )

        for match in result.term_matches:

            print(
                f"{match.term}: "
                f"{match.count} occurrence(s), "
                f"pages={match.pages}"
            )

        print(
            result.snippet
        )


def main():

    docs_folder = Path(
        "data/sample_docs"
    )

    if not docs_folder.exists():

        print(
            "Folder data/sample_docs "
            "was not found."
        )

        return

    engine = load_txt_folder(
        docs_folder
    )

    print(
        f"Indexed "
        f"{engine.index.document_count} "
        f"documents."
    )

    while True:

        query = input(
            "search> "
        ).strip()

        if query.lower() in {
            "exit",
            "quit"
        }:

            break

        if not query:
            continue

        show_results(
            engine,
            query,
            5
        )


if __name__ == "__main__":
    main()
