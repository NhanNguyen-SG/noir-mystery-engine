from dotenv import load_dotenv
load_dotenv()

from pydantic_ai import ModelRetry
from pydantic import BaseModel

class ScoredClue(BaseModel):
    description: str
    score: int
    reason: str

def score_clues(clues: list[str]) -> list[ScoredClue]:
    """
    Score a list of clues by importance on a scale of 1-10.

    Args:
        clues: List of clue descriptions from the crime scene.

    Returns:
        List of ScoredClue objects with scores and reasoning.

    Raises:
        ModelRetry: If the clue list is empty.
    """
    if not clues:
        raise ModelRetry("No clues provided to score. Please provide at least one clue.")

    scored = []
    for clue in clues:
        clue_lower = clue.lower()
        score = 5
        if any(w in clue_lower for w in ["weapon", "blood", "body", "murder", "kill"]):
            score = 10
        elif any(w in clue_lower for w in ["letter", "note", "document", "torn"]):
            score = 9
        elif any(w in clue_lower for w in ["window", "door", "lock", "key"]):
            score = 8
        elif any(w in clue_lower for w in ["witness", "saw", "heard", "shadow"]):
            score = 7
        elif any(w in clue_lower for w in ["glass", "drink", "food"]):
            score = 6

        scored.append(ScoredClue(
            description=clue,
            score=score,
            reason=f"Scored {score}/10 based on physical evidence weight."
        ))

    return sorted(scored, key=lambda x: x.score, reverse=True)


if __name__ == "__main__":
    clues = [
        "open window despite heavy rain",
        "torn letter on the desk",
        "half empty whiskey glass",
        "shadow seen in the garden",
    ]
    results = score_clues(clues)
    for r in results:
        print(f"[{r.score}/10] {r.description}")