from dotenv import load_dotenv
load_dotenv()
from pydantic_ai import Agent
from pydantic_ai.messages import ModelMessagesTypeAdapter
from src.models.clue_finding import ClueFinding
import json
from pathlib import Path

MEMORY_FILE = Path("detective_memory.json")

detective = Agent(
    "openai:claude-sonnet-4-6",
    output_type=ClueFinding,
    system_prompt="""You are a hard-boiled noir detective. You reason through crime scenes 
    step by step, identifying clues, suspects, and motives. Be specific and analytical. 
    Always reference physical evidence. Speak like a 1940s detective.""",
)

def load_memory() -> list:
    """Load conversation history from disk."""
    if MEMORY_FILE.exists():
        data = json.loads(MEMORY_FILE.read_text())
        return ModelMessagesTypeAdapter.validate_python(data)
    return []

def save_memory(messages: list) -> None:
    """Save conversation history to disk."""
    MEMORY_FILE.write_text(
        json.dumps(
            ModelMessagesTypeAdapter.dump_python(messages),
            default=str
        )
    )

async def investigate(scene: str) -> ClueFinding:
    """Run the detective agent on a crime scene description."""
    history = load_memory()
    result = await detective.run(scene, message_history=history)
    save_memory(result.all_messages())
    return result.output


if __name__ == "__main__":
    import asyncio

    scene = """
    A wealthy banker was found dead in his locked study at midnight. 
    The window was open despite the rain. A half-empty glass of whiskey 
    sat on the desk next to a torn letter. The butler claims he heard 
    nothing but the cook saw a shadow near the garden at 11pm.
    """

    result = asyncio.run(investigate(scene))
    print(f"Clues found: {len(result.clues)}")
    for clue in result.clues:
        print(f"  - {clue.description} (suspicion: {clue.suspicion_level}/10)")
    print(f"Prime suspect: {result.prime_suspect}")
    print(f"Reasoning: {result.reasoning}")