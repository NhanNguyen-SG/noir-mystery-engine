from dotenv import load_dotenv
load_dotenv()
import argparse
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
def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Allows the user to provide a crime scene directly, 
    or load one from a file, or enter one interactively.
    """
    parser = argparse.ArgumentParser(description="Run the noir mystery engine")
    parser.add_argument("--scene", nargs="?", help="Crime scene description")
    parser.add_argument("--file", "-f", type=str, help="Path to a crime scene file")
    return parser.parse_args()
    
def get_scene(args: argparse.Namespace) -> str:
    """
    Get the crime scene from one of three places:

    1. A file, if --file is provided
    2. A command-line argument, if scene is provided
    3. Interactive input, if neither is provided
    """
    if args.file:
        return args.file.read_text(encoding="utf-8").strip()

    if args.scene:
        return args.scene.strip()

    return input("Enter the crime scene: ").strip()

def print_result(result: OrchestratorOutput, verbose: bool = False)-> None:
    """
    Print the result of the mystery engine.
    
    Args:
        result: OrchestratorOutput with the full story and summary info.
        verbose: Whether to print the full story.
    """

    print(f"\n{'='*60}")
    print(f"TITLE:    {result.story.title}")
    print(f"SUSPECT:  {result.prime_suspect}")
    print(f"TOP CLUE: {result.top_clue}")
    print(f"CLUES:    {result.clues_found} found")
    print(f"\nVERDICT: {result.story.verdict}")
    print(f"\n{result.story.full_story}")
    if verbose:
        print(f"\n{result.story.full_story}")
async def main() -> None:
    args = parse_args()
    scene = get_scene(args)

    if not scene:
        raise ValueError("Crime scene cannot be empty.")

    result = await run_mystery_engine(scene)
    print_result(result, verbose=args.verbose)        
    