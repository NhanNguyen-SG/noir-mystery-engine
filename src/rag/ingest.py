import os
import re
from pathlib import Path
import chromadb
from sentence_transformers import SentenceTransformer

CORPUS_DIR = Path("corpus")
CHROMA_DIR = Path("chroma_store")
COLLECTION_NAME = "noir_corpus"
CHUNK_SIZE = 400
CHUNK_OVERLAP = 50


def clean_text(text: str) -> str:
    """Remove Project Gutenberg headers/footers and clean whitespace."""
    # Strip Gutenberg header
    start = re.search(r"\*\*\* START OF", text)
    end = re.search(r"\*\*\* END OF", text)
    if start:
        text = text[start.end():]
    if end:
        text = text[:end.start()]
    # Clean whitespace
    text = re.sub(r"\r\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Split text into overlapping chunks by word count."""
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


def ingest_corpus():
    """Load all .txt files from corpus/, chunk them, embed, and store in ChromaDB."""
    print("Loading embedding model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    print("Setting up ChromaDB...")
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    # Delete existing collection if rebuilding
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    collection = client.create_collection(COLLECTION_NAME)

    txt_files = list(CORPUS_DIR.glob("*.txt"))
    if not txt_files:
        print("No .txt files found in corpus/ directory!")
        return

    all_chunks = []
    all_ids = []
    all_metadata = []

    for txt_file in txt_files:
        print(f"Processing {txt_file.name}...")
        raw = txt_file.read_text(encoding="utf-8", errors="ignore")
        cleaned = clean_text(raw)
        chunks = chunk_text(cleaned)

        for i, chunk in enumerate(chunks):
            all_chunks.append(chunk)
            all_ids.append(f"{txt_file.stem}_{i}")
            all_metadata.append({"source": txt_file.name, "chunk_index": i})

    print(f"Embedding {len(all_chunks)} chunks... this may take a minute!")
    embeddings = model.encode(all_chunks, show_progress_bar=True).tolist()

    print("Storing in ChromaDB...")
    # Insert in batches of 500
    batch_size = 500
    for i in range(0, len(all_chunks), batch_size):
        collection.add(
            documents=all_chunks[i:i+batch_size],
            embeddings=embeddings[i:i+batch_size],
            ids=all_ids[i:i+batch_size],
            metadatas=all_metadata[i:i+batch_size],
        )

    print(f"Done! {len(all_chunks)} chunks stored in ChromaDB.")


if __name__ == "__main__":
    ingest_corpus()