# 🔎 Information Retrieval Mini Search Engine

A search engine built from scratch in **Python** that allows users to upload PDF, Word, and text documents and search them using traditional information-retrieval techniques.

The system implements a **positional inverted index, TF-IDF ranking, Boolean retrieval, and exact phrase search** without relying on external search engines or vector databases.

An interactive **Streamlit web application** provides document upload, ranked search results, term-frequency statistics, page-level match locations, and relevant text excerpts.

## 🚀 Live Demo

**Try the application:** [Mini Search Engine](YOUR_STREAMLIT_APP_URL)

---

## 📖 Overview

This project implements the core components of a traditional search engine from scratch.

Users can upload multiple documents and perform different types of searches, including:

- Ranked free-text search
- Exact phrase search
- Boolean `AND`, `OR`, and `NOT` queries

The search engine tokenises uploaded documents, constructs a positional inverted index, calculates TF-IDF relevance scores, processes queries, and returns matching documents.

For each search result, the application can also display:

- Term occurrence counts
- PDF pages containing each search term
- Relevant text excerpts
- Search/match type
- TF-IDF relevance score for ranked searches

The project is intended to demonstrate the fundamental **data structures and algorithms underlying information retrieval systems**.

---

## ✨ Key Features

### 📄 Multi-Format Document Upload

Users can upload multiple documents directly through the web interface.

Supported formats:

- PDF (`.pdf`)
- Microsoft Word (`.docx`)
- Text (`.txt`)

No pre-existing document collection is required.

---

### 🔤 Tokenisation and Normalisation

Document text is converted into lowercase alphanumeric tokens before indexing.

For example:

```text
"London Clay is stiff."
```

becomes:

```text
["london", "clay", "is", "stiff"]
```

This provides a normalised representation of the document collection for indexing and retrieval.

---

### 🗂️ Positional Inverted Index

The engine builds an inverted index mapping each term to the documents and token positions where it occurs.

Conceptually:

```text
"clay"
    ├── Document 1 → [5, 19, 42]
    └── Document 3 → [7, 31]
```

This allows the engine to quickly determine:

- Which documents contain a term
- How many times a term occurs
- Where the term occurs
- Whether multiple terms occur consecutively

The positional information is also used to implement exact phrase search.

---

### 📊 TF-IDF Ranked Search

Normal queries are ranked using **Term Frequency–Inverse Document Frequency (TF-IDF)**.

For example:

```text
london clay
```

The words do not need to occur next to each other.

The engine calculates a relevance score for each matching document based on the importance of the query terms within that document and across the uploaded document collection.

A smoothed IDF calculation is used so that meaningful scores can still be produced when searching a small document collection.

---

### 🔍 Exact Phrase Search

Queries enclosed in quotation marks perform exact phrase searches.

For example:

```text
"london clay"
```

The engine uses the positional inverted index to determine whether `london` is immediately followed by `clay`.

Therefore:

```text
London Clay is stiff.
```

matches, while:

```text
London contains deposits of stiff clay.
```

does not.

---

### 🔀 Boolean Search

The engine supports Boolean query operators.

#### AND

```text
pile AND load
```

Returns only documents containing **both** `pile` and `load`.

#### OR

```text
pile OR raft
```

Returns documents containing **pile**, **raft**, or both.

#### NOT

```text
clay NOT sand
```

Returns documents containing **clay** while excluding documents that also contain **sand**.

Boolean operations are implemented using Python set operations such as intersection, union, and difference.

---

### 📈 Term Occurrence Statistics

For each returned document, the application displays statistics for the search terms.

For example:

| Term | Occurrences | Pages |
|---|---:|---|
| pile | 14 | 3, 7, 9, 12 |
| load | 8 | 4, 7, 12 |

This provides additional visibility into why a document matched the query.

---

### 📑 PDF Page Tracking

PDF documents are processed page by page during ingestion.

The application therefore retains the relationship between extracted text and the original PDF page number.

For a search such as:

```text
pile AND load
```

the application can report:

```text
pile → 14 occurrences → Pages 3, 7, 9, 12
load → 8 occurrences  → Pages 4, 7, 12
```

This allows users to locate relevant information directly within the source document.

> **Note:** Reliable page boundaries are available for PDFs. DOCX and TXT files are currently treated as a single searchable section because they do not provide reliable fixed page boundaries during text extraction.

---

### 📝 Relevant Excerpts

Each search result includes a text excerpt surrounding one of the matched query terms.

This allows users to quickly inspect the context of the match without manually searching through the entire document.

---

## 🏗️ System Architecture

```text
             User Uploads Documents
              PDF / DOCX / TXT
                      │
                      ▼
               Text Extraction
                      │
                      ▼
                 Tokenisation
                      │
                      ▼
          Positional Inverted Index
                      │
                      ▼
                 User Query
                      │
          ┌───────────┼───────────┐
          │           │           │
          ▼           ▼           ▼
       TF-IDF      Boolean      Phrase
       Ranking      Search       Search
          │           │           │
          └───────────┼───────────┘
                      ▼
                Matching Documents
                      │
                      ▼
             Term/Page Statistics
                      │
                      ▼
              Relevant Excerpts
                      │
                      ▼
               Streamlit UI
```

---

## 🔎 Supported Query Types

| Query | Search Type | Behaviour |
|---|---|---|
| `london clay` | TF-IDF | Finds and ranks documents containing relevant query terms |
| `"london clay"` | Phrase | Finds the exact consecutive phrase |
| `pile AND load` | Boolean AND | Requires both terms |
| `pile OR raft` | Boolean OR | Requires either term or both |
| `clay NOT sand` | Boolean NOT | Requires clay and excludes documents containing sand |

---

## ⚙️ How It Works

### 1. Document Ingestion

The user uploads one or more PDF, DOCX, or TXT files through the Streamlit interface.

### 2. Text Extraction

Text is extracted using:

- `PyPDF2` for PDF files
- `python-docx` for Word documents
- Standard Python decoding for TXT files

PDF text is retained separately for each page to support page-level search statistics.

### 3. Tokenisation

Extracted text is normalised and split into lowercase alphanumeric tokens.

### 4. Index Construction

The application constructs a positional inverted index.

For every term, the index records:

```text
term → document → token positions
```

### 5. Query Processing

The query parser determines whether the user has entered:

- A standard ranked query
- An exact phrase query
- A Boolean query

### 6. Retrieval

The appropriate retrieval algorithm is executed.

Standard queries use TF-IDF ranking, phrase queries use positional information, and Boolean queries use document-set operations.

### 7. Result Analysis

For each result, the engine calculates:

- Term frequency
- Occurrence count
- Matching PDF pages
- Relevant text excerpt

### 8. Result Presentation

The Streamlit interface displays the results and supporting search statistics.

---

## 🛠️ Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| Web Interface | Streamlit |
| Search Index | Custom Positional Inverted Index |
| Ranking Algorithm | TF-IDF |
| Query Processing | Custom Python Query Parser |
| Boolean Retrieval | Python Set Operations |
| PDF Processing | PyPDF2 |
| Word Processing | python-docx |
| Testing | pytest |
| Deployment | Streamlit Community Cloud |

The core retrieval algorithms are implemented directly in Python rather than using Elasticsearch, Solr, FAISS, LangChain, or an external search API.

---

## 📁 Project Structure

```text
Information-Retrieval-Mini-Search-Engine/
│
├── app.py
├── main.py
├── requirements.txt
├── README.md
├── .gitignore
│
└── search_engine/
    ├── __init__.py
    ├── engine.py
    ├── index.py
    ├── models.py
    ├── query_parser.py
    └── tokenizer.py
```

### Main Components

**`app.py`**  
Streamlit web interface, document upload, text extraction, and result presentation.

**`engine.py`**  
Coordinates TF-IDF ranking, Boolean retrieval, phrase search, and result generation.

**`index.py`**  
Implements the positional inverted index and document/term lookup operations.

**`query_parser.py`**  
Identifies and parses phrase and Boolean queries.

**`tokenizer.py`**  
Performs text normalisation and tokenisation.

**`models.py`**  
Defines structured search-result and term-match data models.

---

## 💻 Running Locally

### 1. Clone the Repository

```bash
git clone https://github.com/ishantsharmapecpec/Information-Retrieval-Mini-Search-Engine.git

cd Information-Retrieval-Mini-Search-Engine
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Start the Streamlit Application

```bash
streamlit run app.py
```

The application will open in your browser.

Upload PDF, Word, or TXT documents and begin searching.

---

## 📦 Requirements

```text
streamlit
PyPDF2
python-docx
pytest==8.2.2
```

---

## 💡 Example Searches

### Ranked Search

```text
foundation settlement
```

Returns matching documents ranked using TF-IDF.

### Exact Phrase Search

```text
"london clay"
```

Returns documents containing the exact phrase.

### Boolean AND

```text
pile AND load
```

Returns only documents containing both terms.

### Boolean OR

```text
pile OR raft
```

Returns documents containing either term or both.

### Boolean NOT

```text
clay NOT sand
```

Returns documents containing `clay` but excludes documents containing `sand`.

---

## 🧠 Computer Science Concepts Demonstrated

This project demonstrates practical implementation of:

- Information Retrieval
- Data Structures
- Hash Maps / Dictionaries
- Sets
- Positional Inverted Indexes
- TF-IDF Ranking
- Boolean Retrieval
- Set Intersection, Union and Difference
- Phrase Search
- Query Parsing
- Tokenisation
- File I/O
- Object-Oriented Programming
- Modular Software Design
- Document Processing
- Algorithm Implementation
- Web Application Development
- Cloud Deployment

---

## ⚠️ Current Limitations

- Scanned/image-only PDFs require OCR and are not currently supported.
- DOCX and TXT files do not provide reliable fixed page boundaries and are therefore treated as single searchable sections.
- The Boolean parser currently targets simple `AND`, `OR`, and `NOT` expressions rather than arbitrarily complex nested expressions.
- Tokenisation currently performs lowercase alphanumeric normalisation without stemming or lemmatisation.
- Ranking uses TF-IDF rather than more advanced ranking functions such as BM25.
- The index is created dynamically from uploaded documents and is not persisted between application sessions.
- PDF tables, images, drawings, and diagrams are not interpreted semantically.

---

## 🔮 Future Enhancements

Potential improvements include:

- BM25 ranking
- Stemming and lemmatisation
- Stop-word filtering
- Spelling correction
- Query autocomplete
- Complex Boolean expression parsing
- Parenthesised Boolean queries
- Search-term highlighting
- OCR support for scanned PDFs
- Persistent indexes
- Performance benchmarking on large document collections
- Indexing-time and query-time analysis
- Precision and recall evaluation
- Additional document formats

---

## 🎯 Project Purpose

The objective of this project is to explore the fundamental algorithms and data structures behind search engines and information-retrieval systems.

Rather than relying on an existing search platform, the core indexing, ranking, Boolean retrieval, phrase matching, and query-processing functionality is implemented directly in Python.

This provides a practical demonstration of how documents can be transformed from raw text into searchable data structures and how different retrieval algorithms can be used to identify and rank relevant information.

---

## 🔐 Data and Privacy

Uploaded documents are processed by the running application to construct the search index.

This repository contains no confidential client documents, proprietary project information, or API credentials.

Users should avoid uploading confidential or sensitive documents to a public deployment unless appropriate data-handling controls are in place.

---

## 👤 Author

**Ishant Sharma**

Interests:

- Computer Science
- Software Engineering
- Information Retrieval
- Algorithms and Data Structures
- Artificial Intelligence
- Machine Learning
