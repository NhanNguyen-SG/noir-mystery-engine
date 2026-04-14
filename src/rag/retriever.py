import chromadb
from sentence_transformers import SentenceTransformer
from pathlib import Path

CHROMA_DIR = Path("chroma_store")
COLLECTION_NAME = "noir_corpus"


class NightRetriever:
    """Retrieves relevant passages from the noir corpus given a query."""

    def __init__(self, n_results: int = 5):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        self.collection = self.client.get_collection(COLLECTION_NAME)
        self.n_results = n_results

    def query(self, text: str) -> list[dict]:
        """Return top n_results passages most relevant to the query text."""
        embedding = self.model.encode([text]).tolist()
        results = self.collection.query(
            query_embeddings=embedding,
            n_results=self.n_results,
        )
        passages = []
        for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
            passages.append({"text": doc, "source": meta["source"]})
        return passages


if __name__ == "__main__":
    retriever = NightRetriever()
    results = retriever.query("a body was found in the locked room")
    for r in results:
        print(f"[{r['source']}]\n{r['text'][:200]}\n")