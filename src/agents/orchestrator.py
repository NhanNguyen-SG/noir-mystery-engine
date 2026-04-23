from dotenv import load_dotenv
load_dotenv()

import asyncio
from pydantic_ai import Agent
from pydantic import BaseModel
from src.agents.detective import investigate
from src.agents.witness import retrieve_context
from src.agents.narrator import narrate
from src.agents.narrator import StoryReport
from src.tools.clue_scorer import score_clues
from src.tools.file_reader import read_case_file

class OrchestratorOutput(BaseModel):
    story: StoryReport
    clues_found: int
    top_clue: str
    prime_suspect: str

async def run_mystery_engine(scene: str) -> OrchestratorOutput:
    """
    Orchestrate all agents to produce a full noir mystery story.

    Args:
        scene: Crime scene description from the user.

    Returns:
        OrchestratorOutput with the full story and summary info.
    """
    print("🔍 Detective investigating the scene...")
    clues = await investigate(scene)

    print("📚 Witness retrieving archive context...")
    clue_text = " ".join(c.description for c in clues.clues)
    witness_findings = await retrieve_context(clue_text)

    print("📋 Scoring clues by importance...")
    scored = score_clues([c.description for c in clues.clues])

    print("✍️  Narrator writing the story...")
    story = await narrate(scene, clues, witness_findings)

    return OrchestratorOutput(
        story=story,
        clues_found=len(clues.clues),
        top_clue=scored[0].description if scored else "none",
        prime_suspect=clues.prime_suspect,
    )


if __name__ == "__main__":
    scene = """
    A wealthy banker was found dead in his locked study at midnight.
    The window was open despite the rain. A half-empty glass of whiskey
    sat on the desk next to a torn letter. The butler claims he heard
    nothing but the cook saw a shadow near the garden at 11pm.
    """

    result = asyncio.run(run_mystery_engine(scene))
    print(f"\n{'='*60}")
    print(f"TITLE:    {result.story.title}")
    print(f"SUSPECT:  {result.prime_suspect}")
    print(f"TOP CLUE: {result.top_clue}")
    print(f"CLUES:    {result.clues_found} found")
    print(f"\nVERDICT: {result.story.verdict}")
    print(f"\n{result.story.full_story}")