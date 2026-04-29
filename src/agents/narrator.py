from dotenv import load_dotenv
load_dotenv()

from pydantic_ai import Agent
from src.models.clue_finding import ClueFinding
from src.models.story_report import StoryReport
from src.agents.witness import WitnessFindings
from src.agents.model_config import build_model

narrator = Agent(
    build_model(),
    output_type=StoryReport,
    system_prompt="""You are a noir fiction writer in the tradition of Raymond Chandler 
    and Dashiell Hammett. You take detective findings and witness testimony and weave 
    them into a gripping, atmospheric noir short story. Use vivid imagery, sharp 
    dialogue, and moody descriptions. Always end with a verdict.""",
)

async def narrate(
    scene: str,
    clues: ClueFinding,
    witness: WitnessFindings
) -> StoryReport:
    """Write the final noir story from detective and witness findings."""
    prompt = f"""
    Original crime scene: {scene}

    Detective findings:
    - Clues: {[c.description for c in clues.clues]}
    - Prime suspect: {clues.prime_suspect}
    - Reasoning: {clues.reasoning}

    Witness archive passages:
    {witness.relevance_summary}

    Write a full noir short story (300-500 words) based on these findings.
    Include a title, atmospheric setting, and a clear verdict at the end.
    """
    result = await narrator.run(prompt)
    return result.output


if __name__ == "__main__":
    import asyncio
    from src.agents.detective import investigate
    from src.agents.witness import retrieve_context

    scene = """
    A wealthy banker was found dead in his locked study at midnight.
    The window was open despite the rain. A half-empty glass of whiskey
    sat on the desk next to a torn letter. The butler claims he heard
    nothing but the cook saw a shadow near the garden at 11pm.
    """

    async def run_all():
        print("Detective investigating...")
        clues = await investigate(scene)
        print("Witness retrieving context...")
        witness_findings = await retrieve_context(
            " ".join(c.description for c in clues.clues)
        )
        print("Narrator writing story...")
        story = await narrate(scene, clues, witness_findings)
        print(f"\n{'='*50}")
        print(f"TITLE: {story.title}")
        print(f"SETTING: {story.setting}")
        print(f"SUSPECT: {story.prime_suspect}")
        print(f"VERDICT: {story.verdict}")
        print(f"\n{story.full_story}")

    asyncio.run(run_all())
