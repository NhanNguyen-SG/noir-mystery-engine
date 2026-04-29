from dotenv import load_dotenv
load_dotenv()

from pydantic_ai import Agent
from pydantic_ai.messages import ModelMessagesTypeAdapter

from src.models.clue_finding import ClueFinding
from src.agents.model_config import build_model
from src.tools import web_search

import json
from pathlib import Path


MEMORY_FILE = Path("detective_memory.json")


detective = Agent(
    build_model(),
    output_type=ClueFinding,
    system_prompt="""You are a hard-boiled noir detective. You reason through crime scenes 
step by step, identifying clues, suspects, and motives. Be specific and analytical. 
Always reference physical evidence. Speak like a 1940s detective.

You have access to a web_search tool. Use it when the scene is vague, when you need
outside context, or when the crime mentions a specific object, poison, weapon, location,
occupation, historical detail, or forensic method.""",
)

detective.tool_plain(web_search.web_search)
print("✅ Detective registered web_search.web_search as a tool")


def load_memory() -> list:
    """Load conversation history from disk."""
    if MEMORY_FILE.exists():
        print(f"🧠 DETECTIVE MEMORY LOADED FROM: {MEMORY_FILE}")

        data = json.loads(MEMORY_FILE.read_text())
        messages = ModelMessagesTypeAdapter.validate_python(data)

        print(f"🧠 MEMORY MESSAGE COUNT: {len(messages)}")
        return messages

    print("🧠 NO DETECTIVE MEMORY FOUND")
    return []


def memory_has_related_case(history: list, scene: str) -> bool:
    """
    Check whether detective_memory.json has anything related to the current scene.
    """
    if not history:
        return False

    memory_text = json.dumps(
        ModelMessagesTypeAdapter.dump_python(history),
        default=str,
    ).lower()

    scene_words = [
        word.strip(".,!?;:()[]{}\"'").lower()
        for word in scene.split()
        if len(word) > 5
    ]

    if not scene_words:
        return False

    matches = [word for word in scene_words if word in memory_text]

    print(f"🧠 MEMORY RELATED WORD MATCHES: {matches}")

    return len(matches) >= 3


def save_memory(messages: list) -> None:
    """Save conversation history to disk."""
    print(f"💾 SAVING DETECTIVE MEMORY TO: {MEMORY_FILE}")
    print(f"💾 MESSAGE COUNT SAVED: {len(messages)}")

    MEMORY_FILE.write_text(
        json.dumps(
            ModelMessagesTypeAdapter.dump_python(messages),
            default=str,
        )
    )


async def investigate(scene: str) -> ClueFinding:
    """Run the detective agent on a crime scene description."""
    history = load_memory()

    if memory_has_related_case(history, scene):
        print("🧠 RELATED MEMORY FOUND — using detective_memory.json first")

        prompt = f"""
Investigate this crime scene using your existing detective memory when helpful.

Crime scene:
{scene}
"""
    else:
        print("🌐 NO USEFUL MEMORY FOUND — forcing web_search")

        prompt = f"""
You must call the web_search tool before answering.

The detective_memory.json file did not contain enough useful related information.

Search for outside context related to this crime scene, then investigate it.

Crime scene:
{scene}
"""

    result = await detective.run(
        prompt,
        message_history=history,
    )

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