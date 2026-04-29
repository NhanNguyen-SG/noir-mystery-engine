from dotenv import load_dotenv
load_dotenv()

from pydantic_ai import Agent
from pydantic import BaseModel
from src.rag.retriever import NightRetriever
from src.agents.model_config import build_model
from src.tools import file_reader
from pathlib import Path
from src.tools import web_search
class WitnessFindings(BaseModel):
    passages: list[str]
    sources: list[str]
    relevance_summary: str

retriever = NightRetriever(n_results=3)
CORPUS_DIR = Path("corpus")
witness = Agent(
    build_model(),
    output_type=WitnessFindings,
    system_prompt="""You are a noir story witness — an archivist who retrieves relevant 
passages from classic detective stories. Given clues from a crime scene, you find 
the most relevant passages and explain how they connect to the current case.

You have access to local case files through tools.

Use list_case_files when you need to see what .txt files exist in the corpus folder.
Use use_file_reader when the retrieved passages are weak, vague, irrelevant, or when
you need to inspect a specific local case file.

If you use a file, mention in your relevance summary that you consulted a local case file.""",
)


print("✅ Witness registered file_reader tools")

@witness.tool_plain
def list_case_files() -> list[str]:
    """
    List all available .txt files in the corpus folder.
    """
    print("👁️ WITNESS TOOL CALLED: list_case_files")

    if not CORPUS_DIR.exists():
        print("👁️ WITNESS: corpus folder does not exist")
        return []

    files = [file.name for file in CORPUS_DIR.glob("*.txt")]

    print(f"👁️ WITNESS FOUND CASE FILES: {files}")

    return files



@witness.tool_plain
def use_file_reader(filename: str) -> str:
    """
    Read a case file using the file_reader.py module.
    """
    print(f"👁️ WITNESS TOOL CALLED: use_file_reader({filename!r})")

    content = file_reader.read_case_file(filename)

    print(f"👁️ WITNESS READ {len(content)} characters from {filename!r}")
@witness.tool_plain
async def use_web_search(query: str, max_results: int = 3) -> list[dict]:
    """
    Search the web using web_search.py.
    """
    print(f"🌐 WITNESS TOOL CALLED: use_web_search({query!r}, max_results={max_results})")

    results = await web_search.web_search(query, max_results=max_results)

    print(f"🌐 WITNESS WEB SEARCH RETURNED {len(results)} results")

    return results


def retrieved_passages_are_weak(passages: list[dict], clue_summary: str) -> bool:
    """
    Basic check to decide whether RAG returned useful local Sherlock/noir context.
    """
    if not passages:
        print("👁️ WITNESS: No RAG passages found")
        return True

    combined_text = " ".join(
        str(p.get("text", "")) for p in passages
    ).lower()

    clue_words = [
        word.strip(".,!?;:()[]{}\"'").lower()
        for word in clue_summary.split()
        if len(word) > 6
    ]

    matches = [word for word in clue_words if word in combined_text]

    print(f"👁️ WITNESS RAG RELATED WORD MATCHES: {matches}")

    # If fewer than 2 meaningful words match, treat local corpus as weak.
    return len(matches) < 2


async def retrieve_context(clue_summary: str) -> WitnessFindings:
    """
    Retrieve relevant passages from the noir corpus for the given clues.

    If local Sherlock/noir text is not useful, force web_search.
    """
    print("👁️ WITNESS retrieve_context CALLED")
    print(f"👁️ CLUE SUMMARY: {clue_summary!r}")

    passages = retriever.query(clue_summary)

    print(f"📚 RAG RETRIEVER CALLED: returned {len(passages)} passages")

    passage_text = "\n\n".join(
        f"[{p['source']}]: {p['text'][:300]}" for p in passages
    )

    if retrieved_passages_are_weak(passages, clue_summary):
        print("🌐 LOCAL SHERLOCK/NOIR TEXT NOT RELATED — forcing Witness web_search")

        result = await witness.run(
            f"""
The local Sherlock/noir corpus did not return strong related passages.

You must call use_web_search before answering.

Search for useful outside context related to this clue summary:

{clue_summary}

Then return:
- passages: short useful findings from web results
- sources: URLs or source names from web results
- relevance_summary: explain how the web context connects to the current case
"""
        )

    else:
        print("📚 RELATED LOCAL SHERLOCK/NOIR TEXT FOUND — using RAG passages first")

        result = await witness.run(
            f"""
Here are retrieved passages relevant to this crime:

{passage_text}

Clue summary:
{clue_summary}

Summarize how these passages connect to the current case.

You may use your tools if these passages are still not enough.
"""
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
