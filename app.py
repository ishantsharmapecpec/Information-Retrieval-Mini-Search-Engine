from pathlib import Path
import tempfile

import streamlit as st

from search_engine import SearchEngine


st.set_page_config(
    page_title="Mini Search Engine",
    page_icon="🔎",
    layout="wide"
)

st.title("🔎 Mini Search Engine")

st.markdown(
    """
    A search engine built from scratch using:

    - Positional inverted indexing
    - TF-IDF ranking
    - Boolean search
    - Phrase search
    """
)


# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------

st.sidebar.header("Search Settings")

limit = st.sidebar.slider(
    "Maximum results",
    min_value=1,
    max_value=20,
    value=5
)


# ---------------------------------------------------------
# DOCUMENT SOURCE
# ---------------------------------------------------------

st.header("1. Select Documents")

source_option = st.radio(
    "Choose document source",
    [
        "Use sample documents",
        "Upload documents"
    ]
)


# ---------------------------------------------------------
# SAMPLE DOCUMENTS
# ---------------------------------------------------------

if source_option == "Use sample documents":

    docs_folder = Path("data/sample_docs")

    if docs_folder.exists():

        engine = SearchEngine.from_folder(docs_folder)

        st.success(
            f"Indexed {engine.index.document_count} sample documents."
        )

    else:

        st.error(
            "Sample document folder could not be found."
        )

        engine = None


# ---------------------------------------------------------
# UPLOADED DOCUMENTS
# ---------------------------------------------------------

else:

    uploaded_files = st.file_uploader(
        "Upload text documents",
        type=["txt"],
        accept_multiple_files=True
    )

    engine = None

    if uploaded_files:

        temp_dir = tempfile.TemporaryDirectory()

        temp_path = Path(temp_dir.name)

        for uploaded_file in uploaded_files:

            file_path = temp_path / uploaded_file.name

            file_path.write_bytes(
                uploaded_file.getvalue()
            )


        engine = SearchEngine.from_folder(temp_path)

        st.success(
            f"Indexed {engine.index.document_count} uploaded documents."
        )


# ---------------------------------------------------------
# SEARCH
# ---------------------------------------------------------

if engine is not None:

    st.divider()

    st.header("2. Search")


    query = st.text_input(
        "Enter your search query",
        placeholder='Examples: london clay | "london clay" | pile AND load'
    )


    st.caption(
        'Examples: `london clay`, `"london clay"`, '
        '`pile AND load`, `clay NOT sand`'
    )


    if query:

        results = engine.search(
            query,
            limit=limit
        )


        st.divider()

        st.subheader("Search Results")


        if not results:

            st.warning(
                "No results found."
            )


        else:

            st.write(
                f"Found {len(results)} result(s)."
            )


            for rank, result in enumerate(
                results,
                start=1
            ):

                st.markdown(
                    f"### {rank}. {result.title}"
                )


                col1, col2 = st.columns(
                    [1, 4]
                )


                with col1:

                    st.metric(
                        "TF-IDF Score",
                        result.score
                    )


                with col2:

                    st.caption(
                        f"Document: {result.path}"
                    )


                st.write(
                    result.snippet
                )


                st.divider()


else:

    st.info(
        "Select the sample documents or upload text files to begin."
    )
