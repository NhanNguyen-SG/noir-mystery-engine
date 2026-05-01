from dotenv import load_dotenv
load_dotenv()

from pydantic_ai import Agent
from pydantic import BaseModel
from src.rag.retriever import NightRetriever
from src.tools.web_search import web_search
import asyncio

class WitnessFindings(BaseModel):
    passages: list[str]
    sources: list[str]
    relevance_summary: str
    source_type: str  # "corpus" or "web"

retriever = NightRetriever(n_results=3)

witness = Agent(
    "openai:claude-sonnet-4-6",
    output_type=WitnessFindings,
    system_prompt="""You are a noir story witness — an archivist who retrieves relevant 
    passages from classic detective stories. Given clues from a crime scene, you find 
    the most relevant passages and explain how they connect to the current case.""",
)

def is_relevant(passages: list[dict], threshold: int = 50) -> bool:
    """Check if retrieved passages are relevant enough to use."""
    if not passages:
        return False
    # Check if passages have enough content
    avg_length = sum(len(p["text"]) for p in passages) / len(passages)
    return avg_length > threshold

async def retrieve_context(clue_summary: str) -> WitnessFindings:
    """
    Retrieve relevant passages — tries ChromaDB first, 
    falls back to web search if corpus results are weak.
    """
    # Try corpus first
    passages = retriever.query(clue_summary)

    if is_relevant(passages):
        print("📚 Witness pulling from local corpus...")
        passage_text = "\n\n".join(
            f"[{p['source']}]: {p['text'][:300]}" for p in passages
        )
        source_type = "corpus"
    else:
        # Fall back to web search
        print("🌐 Corpus weak — Witness switching to web search...")
        web_results = await web_search(clue_summary)
        passage_text = "\n\n".join(
            f"[{r['url']}]: {r['snippet']}" for r in web_results
        )
        passages = [{"text": r["snippet"], "source": r["url"]} for r in web_results]
        source_type = "web"

    result = await witness.run(
        f"Here are retrieved passages relevant to this crime:\n\n{passage_text}\n\n"
        f"Clue summary: {clue_summary}\n\n"
        f"Summarize how these passages connect to the current case."
    )

    output = result.output
    output.source_type = source_type
    return output


if __name__ == "__main__":
    findings = asyncio.run(retrieve_context(
        "locked room, open window, torn letter, trusted killer"
    ))
    print(f"Source type: {findings.source_type}")
    print(f"Relevance: {findings.relevance_summary}")