from dotenv import load_dotenv
load_dotenv()

import asyncio
from pydantic import BaseModel
from pydantic_evals import Case, Dataset
from pydantic_evals.evaluators import Evaluator, EvaluatorContext
from pydantic_ai import Agent
from src.agents.orchestrator import run_mystery_engine
from src.agents.orchestrator import OrchestratorOutput
from src.agents.model_config import build_model

# ── Evaluator 1: Deterministic ──────────────────────────────
class ContainsExpectedFields(Evaluator[str, OrchestratorOutput]):
    """Check that the output has a title, suspect, and non-empty story."""

    def evaluate(self, ctx: EvaluatorContext[str, OrchestratorOutput]) -> float:
        output = ctx.output
        if not output:
            return 0.0
        score = 0.0
        if output.story.title and len(output.story.title) > 3:
            score += 0.33
        if output.prime_suspect and len(output.prime_suspect) > 2:
            score += 0.33
        if output.story.full_story and len(output.story.full_story) > 100:
            score += 0.34
        return score


# ── Evaluator 2: Behavioral ──────────────────────────────────
class CluesDiscovered(Evaluator[str, OrchestratorOutput]):
    """Check that the detective found at least 3 clues."""

    def evaluate(self, ctx: EvaluatorContext[str, OrchestratorOutput]) -> float:
        output = ctx.output
        if not output:
            return 0.0
        return 1.0 if output.clues_found >= 3 else 0.0


# ── Evaluator 3: LLM Judge ───────────────────────────────────
class NoirQualityJudge(Evaluator[str, OrchestratorOutput]):
    """Ask the LLM to judge if the story feels like real noir fiction."""

    async def evaluate(self, ctx: EvaluatorContext[str, OrchestratorOutput]) -> float:
        output = ctx.output
        if not output or not output.story.full_story:
            return 0.0

        judge = Agent(
            build_model(),
            output_type=bool,
            system_prompt="""You are a literary critic judging noir fiction quality.
            Return true if the story has atmospheric noir writing, a clear suspect,
            and a dramatic verdict. Return false if it is generic or low quality."""
        )
        result = await judge.run(
            f"Is this good noir fiction?\n\n{output.story.full_story[:500]}"
        )
        return 1.0 if result.output else 0.0


# ── Test Cases ───────────────────────────────────────────────
def build_dataset() -> Dataset[str, OrchestratorOutput]:
    cases = [
        Case(
            name="classic_locked_room",
            inputs="A banker was found dead in his locked study. The window was open despite rain. A torn letter and whiskey glass sat on the desk. The butler claims he heard nothing.",
            metadata={"category": "classic"}
        ),
        Case(
            name="opera_singer",
            inputs="A famous opera singer was found dead in her dressing room. The door was locked from inside. A red rose with a threatening note lay on the mirror. Her understudy has no alibi.",
            metadata={"category": "theatre"}
        ),
        Case(
            name="poisoned_professor",
            inputs="A university professor was found slumped over his desk. A half finished cup of tea sat beside an open gradebook. A failing student was seen arguing with him earlier.",
            metadata={"category": "academic"}
        ),
        Case(
            name="missing_jewels",
            inputs="A jeweler was found unconscious in his locked vault. A diamond necklace worth half a million was gone. Security footage was wiped. A white glove was found on the floor.",
            metadata={"category": "heist"}
        ),
        Case(
            name="dead_journalist",
            inputs="An investigative journalist was found dead the night before publishing a major story. Her laptop was smashed. A city councillor had threatened her two days prior.",
            metadata={"category": "political"}
        ),
        Case(
            name="lighthouse_murder",
            inputs="A lighthouse keeper was found dead at the bottom of the spiral staircase. A fisherman saw two figures at the top before the light went dark. A torn photo was in his hand.",
            metadata={"category": "coastal"}
        ),
        Case(
            name="card_game",
            inputs="A gambler was found shot in a private card club. Thirty thousand dollars was missing. Five players all claim they saw nothing. A loud argument about cheating was heard before the shot.",
            metadata={"category": "gambling"}
        ),
        Case(
            name="poisoned_chef",
            inputs="A famous chef was found dead in his kitchen surrounded by rivals. His secret recipe was stolen. A half eaten croissant was found at the scene.",
            metadata={"category": "culinary"}
        ),
        Case(
            name="art_gallery",
            inputs="A gallery owner was found dead on the night of a major exhibition opening. A priceless painting was missing. The security guard was found unconscious in the storage room.",
            metadata={"category": "art"}
        ),
        Case(
            name="train_mystery",
            inputs="A diplomat was found dead in a first class train compartment. The door was locked from inside. His briefcase containing state secrets was open and empty. Three passengers had motive.",
            metadata={"category": "travel"}
        ),
        Case(
            name="manor_house",
            inputs="An elderly lord was found dead in his manor library. His will had been changed the week before. Three relatives were visiting. A secret passage behind the bookshelf was left open.",
            metadata={"category": "manor"}
        ),
        Case(
            name="theater_director",
            inputs="A theater director was found dead in the prop room on opening night. A fake dagger was replaced with a real one. The lead actor and the playwright both had grudges against him.",
            metadata={"category": "theatre"}
        ),
    ]

    return Dataset(
        cases=cases,
        evaluators=[
            ContainsExpectedFields(),
            CluesDiscovered(),
            NoirQualityJudge(),
        ]
    )


async def run_eval():
    """Run the full evaluation suite and print results."""
    print("Building evaluation dataset...")
    dataset = build_dataset()

    print(f"Running {len(dataset.cases)} test cases...\n")

    async def task(scene: str) -> OrchestratorOutput:
        return await run_mystery_engine(scene)

    report = await dataset.evaluate(task, max_concurrency=1)
    report.print(include_input=True)
    return report


if __name__ == "__main__":
    asyncio.run(run_eval())
