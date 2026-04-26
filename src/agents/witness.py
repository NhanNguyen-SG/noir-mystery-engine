from dotenv import load_dotenv
load_dotenv()

from pydantic_ai import Agent
from pydantic import BaseModel
from src.rag.retriever import NightRetriever

class WitnessFindings(BaseModel):
    passages: list[str]
    sources: list[str]
    relevance_summary: str

retriever = NightRetriever(n_results=3)

witness = Agent(
    "anthropic:claude-sonnet-4-6",
    output_type=WitnessFindings,
    system_prompt="""You are a noir story witness — an archivist who retrieves relevant 
    passages from classic detective stories. Given clues from a crime scene, you find 
    the most relevant passages and explain how they connect to the current case.""",
)

async def retrieve_context(clue_summary: str) -> WitnessFindings:
    """Retrieve relevant passages from the noir corpus for the given clues."""
    passages = retriever.query(clue_summary)
    passage_text = "\n\n".join(
        f"[{p['source']}]: {p['text'][:300]}" for p in passages
    )
    result = await witness.run(
        f"Here are retrieved passages relevant to this crime:\n\n{passage_text}\n\n"
        f"Clue summary: {clue_summary}\n\n"
        f"Summarize how these passages connect to the current case."
    )
    return result.output


if __name__ == "__main__":
    import asyncio

    findings = asyncio.run(retrieve_context(
        "locked room, open window, torn letter, trusted killer"
    ))
    print(f"Relevance: {findings.relevance_summary}")
    for p, s in zip(findings.passages, findings.sources):
        print(f"\n[{s}] {p[:150]}")