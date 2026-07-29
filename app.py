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
    Search your own documents using a search engine implemented
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
        return file.getvalue().decode("utf-8", errors="ignore")
    except Exception:
        return ""


def extract_pdf(file):
    try:
        reader = PdfReader(file)
        pages = []

        for page in reader.pages:
            text = page.extract_text()

            if text:
                pages.append(text)

        return "\n".join(pages)

    except Exception:
        return ""


def extract_docx(file):
    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".docx"
        ) as temp_file:

            temp_file.write(file.getvalue())
            temp_path = temp_file.name

        document = docx.Document(temp_path)

        text = "\n".join(
            paragraph.text
            for paragraph in document.paragraphs
            if paragraph.text.strip()
        )

        return text

    except Exception:
        return ""

    finally:
        if temp_path:
            Path(temp_path).unlink(missing_ok=True)


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.header("Search Settings")

limit = st.sidebar.slider(
    "Maximum results",
    min_value=1,
    max_value=20,
    value=5
)


# =========================================================
# DOCUMENT UPLOAD
# =========================================================

st.header("1. Upload Documents")

uploaded_files = st.file_uploader(
    "Upload TXT, PDF or Word documents",
    type=["txt", "pdf", "docx"],
    accept_multiple_files=True
)


# =========================================================
# BUILD SEARCH INDEX
# =========================================================

if uploaded_files:

    engine = SearchEngine()
    indexed_documents = 0

    with st.spinner(
        "Extracting text and building inverted index..."
    ):

        for document_id, file in enumerate(uploaded_files):

            file_name = file.name.lower()

            if file_name.endswith(".txt"):

                text = extract_txt(file)

            elif file_name.endswith(".pdf"):

                file.seek(0)
                text = extract_pdf(file)

            elif file_name.endswith(".docx"):

                text = extract_docx(file)

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
                text=text
            )

            indexed_documents += 1

    st.session_state.engine = engine

    st.success(
        f"✅ Indexed {indexed_documents} document(s)."
    )


# =========================================================
# SEARCH
# =========================================================

if "engine" in st.session_state:

    engine = st.session_state.engine

    st.divider()

    st.header("2. Search Documents")

    query = st.text_input(
        "Enter search query",
        placeholder='Examples: london clay | "london clay" | pile AND load'
    )

    st.markdown(
        """
        **Search examples**

        - `london clay` → TF-IDF ranked search
        - `"london clay"` → exact phrase search
        - `pile AND load` → both terms required
        - `pile OR raft` → either term
        - `clay NOT sand` → clay excluding sand
        """
    )

    if query:

        try:

            results = engine.search(
                query,
                limit=limit
            )

            st.divider()

            st.subheader("Search Results")

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
                        f"### {rank}. {result.title}"
                    )

                    col1, col2 = st.columns([1, 4])

                    with col1:

                        st.metric(
                            "Relevance Score",
                            f"{result.score:.4f}"
                        )

                    with col2:

                        st.caption(
                            f"Source: {result.path}"
                        )

                    st.write(
                        result.snippet
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

with st.expander("ℹ️ How does this search engine work?"):

    st.markdown(
        """
### 1. Tokenisation

Uploaded document text is converted into normalised lowercase tokens.

For example:

**London Clay is stiff**

becomes:

`["london", "clay", "is", "stiff"]`

### 2. Positional Inverted Index

The engine records:

- which terms occur in the document collection
- which documents contain each term
- the positions at which each term occurs

For example, the index may conceptually contain:

`"clay" → Document 1: [5, 19, 42]`

This means that the word **clay** occurs in Document 1 at word positions 5, 19 and 42.

### 3. TF-IDF Ranking

Normal text queries are ranked using **Term Frequency–Inverse Document Frequency (TF-IDF)**.

Terms that are important within a document but less common across the overall document collection receive greater weight.

### 4. Phrase Search

The positional index allows the search engine to determine whether words occur consecutively.

For example:

`"london clay"`

returns documents where **london** is immediately followed by **clay**.

### 5. Boolean Search

Boolean queries are processed using set operations:

- **AND** → intersection
- **OR** → union
- **NOT** → difference

The indexing, query processing and retrieval algorithms are implemented directly in Python rather than using an external search engine or vector database.
        """
    )
