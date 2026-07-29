import tempfile
from pathlib import Path

import streamlit as st
from PyPDF2 import PdfReader
import docx

from search_engine import SearchEngine


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Mini Search Engine",
    page_icon="🔎",
    layout="wide"
)

st.title("🔎 Mini Search Engine")

st.markdown(
    """
    Search uploaded documents using a search engine implemented
    from scratch in Python.

    **Supported retrieval methods:**  
    TF-IDF ranking • Boolean search • Phrase search • Positional indexing
    """
)


# =========================================================
# TEXT EXTRACTION
# =========================================================

def extract_txt(file):

    try:

        text = file.getvalue().decode(
            "utf-8",
            errors="ignore"
        )

        return text, {1: text}

    except Exception:

        return "", {}


def extract_pdf(file):

    try:

        reader = PdfReader(file)

        pages = {}
        full_text = []

        for page_number, page in enumerate(
            reader.pages,
            start=1
        ):

            text = page.extract_text()

            if text:
                pages[page_number] = text
                full_text.append(text)

        return "\n".join(
            full_text
        ), pages

    except Exception:

        return "", {}


def extract_docx(file):

    temp_path = None

    try:

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".docx"
        ) as temp_file:

            temp_file.write(
                file.getvalue()
            )

            temp_path = temp_file.name

        document = docx.Document(
            temp_path
        )

        paragraphs = [
            paragraph.text
            for paragraph
            in document.paragraphs
            if paragraph.text.strip()
        ]

        text = "\n".join(
            paragraphs
        )

        # DOCX does not expose reliable page
        # boundaries, so treat the file as one section.
        pages = {
            1: text
        }

        return text, pages

    except Exception:

        return "", {}

    finally:

        if temp_path:

            Path(
                temp_path
            ).unlink(
                missing_ok=True
            )


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.header(
    "Search Settings"
)

limit = st.sidebar.slider(
    "Maximum results",
    min_value=1,
    max_value=20,
    value=5
)


# =========================================================
# DOCUMENT UPLOAD
# =========================================================

st.header(
    "1. Upload Documents"
)

uploaded_files = st.file_uploader(
    "Upload TXT, PDF or Word documents",
    type=[
        "txt",
        "pdf",
        "docx"
    ],
    accept_multiple_files=True
)


# =========================================================
# BUILD INDEX
# =========================================================

if uploaded_files:

    engine = SearchEngine()

    indexed_documents = 0

    with st.spinner(
        "Extracting text and building search index..."
    ):

        for document_id, file in enumerate(
            uploaded_files
        ):

            file_name = (
                file.name.lower()
            )

            if file_name.endswith(
                ".txt"
            ):

                text, pages = (
                    extract_txt(
                        file
                    )
                )

            elif file_name.endswith(
                ".pdf"
            ):

                file.seek(0)

                text, pages = (
                    extract_pdf(
                        file
                    )
                )

            elif file_name.endswith(
                ".docx"
            ):

                text, pages = (
                    extract_docx(
                        file
                    )
                )

            else:

                continue

            if not text.strip():

                st.warning(
                    f"No readable text found in {file.name}"
                )

                continue

            engine.add_document(
                document_id=document_id,
                title=file.name,
                path=file.name,
                text=text,
                pages=pages
            )

            indexed_documents += 1

    st.session_state.engine = (
        engine
    )

    st.success(
        f"✅ Indexed {indexed_documents} document(s)."
    )


# =========================================================
# SEARCH
# =========================================================

if "engine" in st.session_state:

    engine = (
        st.session_state.engine
    )

    st.divider()

    st.header(
        "2. Search Documents"
    )

    query = st.text_input(
        "Enter search query",
        placeholder=(
            'Examples: london clay | '
            '"london clay" | '
            'pile AND load'
        )
    )

    st.markdown(
        """
        **Search examples**

        - `london clay` → TF-IDF ranked search
        - `"london clay"` → exact phrase search
        - `pile AND load` → both terms required
        - `pile OR raft` → either term may be present
        - `clay NOT sand` → clay must be present and sand absent
        """
    )

    if query:

        try:

            results = engine.search(
                query,
                limit=limit
            )

            st.divider()

            st.subheader(
                "Search Results"
            )

            if not results:

                st.warning(
                    "No matching documents found."
                )

            else:

                st.caption(
                    f"{len(results)} result(s)"
                )

                for rank, result in enumerate(
                    results,
                    start=1
                ):

                    st.markdown(
                        f"## {rank}. {result.title}"
                    )

                    st.caption(
                        f"Search type: {result.match_type}"
                    )

                    # =====================================
                    # SCORE
                    # =====================================

                    if (
                        result.match_type
                        == "TF-IDF Ranked Search"
                    ):

                        st.metric(
                            "TF-IDF Relevance Score",
                            f"{result.score:.6f}"
                        )

                    else:

                        st.success(
                            "Search condition matched"
                        )

                    # =====================================
                    # TERM STATISTICS
                    # =====================================

                    st.markdown(
                        "### Match Statistics"
                    )

                    if result.term_matches:

                        rows = []

                        for match in result.term_matches:

                            if match.pages:

                                page_text = ", ".join(
                                    str(page)
                                    for page
                                    in match.pages
                                )

                            else:

                                page_text = (
                                    "Not present"
                                )

                            rows.append(
                                {
                                    "Term / Phrase":
                                        match.term,

                                    "Occurrences":
                                        match.count,

                                    "Pages":
                                        page_text
                                }
                            )

                        st.table(
                            rows
                        )

                    # =====================================
                    # BOOLEAN EXPLANATION
                    # =====================================

                    if result.match_type.startswith(
                        "Boolean"
                    ):

                        st.markdown(
                            "### Boolean Match Details"
                        )

                        for match in result.term_matches:

                            if match.count > 0:

                                st.write(
                                    f"✅ `{match.term}` "
                                    f"found {match.count} time(s)"
                                )

                            else:

                                st.write(
                                    f"❌ `{match.term}` "
                                    "not present"
                                )

                    # =====================================
                    # SNIPPET
                    # =====================================

                    st.markdown(
                        "### Relevant Excerpt"
                    )

                    st.write(
                        result.snippet
                    )

                    st.caption(
                        f"Source: {result.path}"
                    )

                    st.divider()

        except Exception as e:

            st.error(
                f"Search failed: {e}"
            )


else:

    st.info(
        "👆 Upload one or more documents to begin."
    )


# =========================================================
# HOW IT WORKS
# =========================================================

st.divider()

with st.expander(
    "ℹ️ How does this search engine work?"
):

    st.markdown(
        """
### 1. Tokenisation

Document text is converted into lowercase word tokens.

For example:

`London Clay is stiff`

becomes:

`["london", "clay", "is", "stiff"]`

### 2. Positional Inverted Index

The engine stores:

- which documents contain each term
- how many times the term occurs
- the token positions where it occurs

This supports fast lookup and phrase searching.

### 3. TF-IDF Ranked Search

A normal query such as:

`london clay`

uses TF-IDF to rank documents according to the importance of the query terms.

### 4. Exact Phrase Search

A query such as:

`"london clay"`

uses stored token positions to determine whether the words appear consecutively.

### 5. Boolean Search

Queries may use:

- `AND`
- `OR`
- `NOT`

Examples:

`pile AND load`

requires both terms.

`pile OR raft`

returns documents containing either term or both.

`clay NOT sand`

returns documents containing clay while excluding documents containing sand.

### 6. Match Statistics

For each result, the application also shows:

- number of term occurrences
- page numbers where the term occurs
- relevant source excerpt

For PDF files, actual PDF page numbers are retained during indexing.

DOCX and TXT files do not provide reliable page boundaries, so they are currently treated as a single searchable section.
        """
    )
