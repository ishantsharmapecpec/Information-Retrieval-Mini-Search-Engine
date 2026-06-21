# Mini Search Engine

A Python search engine built from scratch. It indexes text files, builds an inverted index, supports TF-IDF ranking, Boolean search, and phrase search.

This project is designed as a strong GitHub/CV project for an OMSCS application because it demonstrates data structures, algorithms, file I/O, ranking, and clean software design.

## Features

- Tokenization and text normalization
- Inverted index: term -> document -> word positions
- TF-IDF ranking
- Phrase search using positional indexes
- Boolean search: `AND`, `OR`, `NOT`
- Command-line interface
- Unit tests with `pytest`
- Sample documents included

## Project Structure

```text
mini_search_engine/
├── search_engine/
│   ├── __init__.py
│   ├── engine.py
│   ├── index.py
│   ├── models.py
│   ├── query_parser.py
│   └── tokenizer.py
├── data/
│   └── sample_docs/
├── tests/
│   └── test_search_engine.py
├── main.py
├── requirements.txt
├── .gitignore
└── README.md
```

## How to Run

Clone the repository and install requirements:

```bash
pip install -r requirements.txt
```

Run an interactive search session:

```bash
python main.py
```

Or run one query directly:

```bash
python main.py "london clay"
python main.py "\"inverted indexes\""
python main.py "clay NOT london"
python main.py "pile AND load"
```

## How It Works

### 1. Tokenization

The text is converted to lowercase word tokens. Punctuation is removed.

Example:

```text
"London Clay is stiff."
```

becomes:

```text
["london", "clay", "is", "stiff"]
```

### 2. Inverted Index

Instead of scanning every document for every search, the engine builds a dictionary like this:

```python
{
    "clay": {
        1: [1, 10, 25],
        3: [8, 33]
    }
}
```

This means the word `clay` appears in document 1 at positions 1, 10, and 25, and in document 3 at positions 8 and 33.

### 3. TF-IDF Ranking

TF-IDF gives higher scores to documents where the query term is important.

- TF = term frequency in the document
- IDF = inverse document frequency across all documents

Common words receive lower weight. More distinctive words receive higher weight.

### 4. Phrase Search

For a phrase such as:

```text
"london clay"
```

The engine checks whether `london` and `clay` appear next to each other using the stored word positions.

### 5. Boolean Search

Supported examples:

```text
london AND clay
pile OR raft
clay NOT sand
```

## Running Tests

```bash
pytest
```

## Example Output

```text
1. london_clay  score=4.3863
   data/sample_docs/london_clay.txt
   London Clay is a stiff overconsolidated clay found across large parts of London...
```

## Skills Demonstrated

- Python programming
- Object-oriented programming
- Hash maps / dictionaries
- Inverted index data structure
- Ranking algorithms
- Query parsing
- Unit testing
- Clean GitHub documentation

## Possible Improvements

These are good future extensions for the project:

- Add BM25 ranking
- Add stemming or lemmatization
- Add spelling correction
- Add web interface using Streamlit or Flask
- Add PDF parsing
- Add document upload feature
- Add autocomplete
- Add performance benchmarking
