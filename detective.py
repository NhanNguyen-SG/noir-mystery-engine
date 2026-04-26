from dotenv import load_dotenv
load_dotenv()

import asyncio
import json
from pathlib import Path

from pydantic_ai import Agent
from pydantic_ai.messages import ModelMessagesTypeAdapter

from src.models.clue_finding import ClueFinding


MEMORY_FILE = Path("detective_memory.json")

detective = Agent(
    "openai:claude-sonnet-4-6",
    output_type=ClueFinding,
    system_prompt="""
You are a hard-boiled noir detective from the 1940s.

You are one of the best detectives in the business, with sharp analytical skills,
a disciplined investigative mind, and a talent for seeing meaning in small physical details.

Your job is to investigate crime scenes step by step and identify:
- physical clues
- real clues
- false or staged clues
- contradictions
- suspects
- motives
- means
- opportunity
- timeline problems
- locked-room tricks
- staged misdirection

You must rank clues by how much they explain the actual crime, not by how strange,
symbolic, dramatic, or story-like they are.

Priority order for clue importance:
1. Clues that explain the murder method
2. Clues that prove how the killer bypassed the locked-room problem
3. Clues that identify who had access, knowledge, or opportunity
4. Clues that expose timeline manipulation
5. Clues that suggest motive
6. Atmospheric, symbolic, or staged clues

Critical clue rules:
- The top clue must be ONE specific clue from the scene.
- The top clue must be the clue that best explains HOW the victim died.
- Never choose a group of fake clues as the top clue.
- Never choose symbolic objects, staged objects, theatrical clutter, or atmosphere as the top clue unless they directly explain the murder method.
- A single real method clue outranks 100 fake clues.
- A clue is not important just because it is weird.
- Fake clues can be listed, but they should not become the top clue unless the question is specifically about misdirection.
- If a clue proves environmental, chemical, mechanical, medical, digital, or machine manipulation, it should usually outrank symbolic clues.

Evidence discipline:
- Always reference specific physical evidence from the scene.
- For every clue, decide whether it is real, fake, or uncertain.
- A real clue directly supports the murder method, timeline, culprit, motive, or opportunity.
- A fake clue is likely staged, planted, exaggerated, or designed to mislead investigators.
- Uncertain means the clue may matter, but the evidence does not prove how yet.
- Separate what a clue proves from what it merely suggests.
- Do not invent murder methods, tools, chemicals, hidden mechanisms, or extra backstory.
- Do not turn theories into facts.
- If a detail is not stated in the scene, mark it as theory, not fact.
- The prime suspect may be "Unknown" if the evidence is not strong enough.
- Confidence should stay low when the evidence is weak or circumstantial.

Style:
- Speak in a gritty 1940s noir detective voice.
- Be specific and analytical.
- End with a clear prime suspect or say the culprit cannot be determined from the evidence.

"""
,
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
            default=str,
            indent=2
        )
    )
METHOD_KEYWORDS = [
     # general method words
    "method",
    "weapon",
    "cause of death",
    "murder method",
    "mechanism",
    "trigger",
    "sabotage",
    "tampered",
    "tamper",
    "bypassed",
    "override",
    "disabled",
    "manually disabled",
    "manual",
    "remote",
    "remotely",
    "access",
    "log",
    "logs",
    "diagnostic",
    "report",
    "timestamp",
    "system",
    "control",
    "panel",

    # machine / engineering methods
    "vibration",
    "dampener",
    "dampeners",
    "frequency",
    "resonance",
    "resonant",
    "high-frequency",
    "test",
    "prototype",
    "module",
    "motor",
    "servo",
    "pressure",
    "vacuum",
    "hydraulic",
    "pneumatic",
    "voltage",
    "current",
    "circuit",
    "short",
    "overload",
    "calibration",
    "safety",
    "interlock",
    "fail-safe",
    "sensor",

    # environmental / room methods
    "humidity",
    "temperature",
    "climate",
    "climate-control",
    "vent",
    "ventilation",
    "airflow",
    "air exchange",
    "oxygen",
    "carbon monoxide",
    "gas",
    "fumes",
    "vapor",
    "chemical vapor",
    "sealed room",
    "windowless",
    "air quality",
    "varnish",
    "bloom",
    "blushing",

    # medical / body evidence
    "wound",
    "puncture",
    "needle",
    "injection",
    "injector",
    "embolism",
    "air embolism",
    "toxin",
    "poison",
    "metabolized",
    "fast-metabolizing",
    "autopsy",
    "medical examiner",
    "blood",
    "lungs",
    "heart",
    "cardiac",
    "respiratory",
    "asphyxiation",
    "strangulation",
    "trauma",
    "fracture",
    "burn",
    "bruise",

    # timeline evidence
    "time",
    "clock",
    "watch",
    "stopped",
    "fast",
    "slow",
    "minutes",
    "seconds",
    "12:03",
    "94 seconds",
    "timestamp",
    "timeline",
    "alibi",

    # locked-room/access evidence
    "keypad",
    "biometric",
    "badge",
    "fingerprint",
    "retinal",
    "magnetic lock",
    "door",
    "lock",
    "locked",
    "entry",
    "exit",
    "motion sensor",
    "security log",
    "unauthorized entry",
    "override",
]


def choose_top_clue(result: ClueFinding) -> str:
    """
    Pick the best top clue from the structured clue list.
    Method evidence beats motive, symbolism, and staged clutter.
    """

    def score(clue) -> int:
        text = " ".join(
            [
                clue.description,
                getattr(clue, "location", ""),
                getattr(clue, "proves", ""),
                getattr(clue, "suggests", ""),
            ]
        ).lower()

        points = 0

        if clue.clue_type == "real":
            points += 100
        elif clue.clue_type == "uncertain":
            points += 25
        else:
            points -= 50

        points += clue.suspicion_level * 5

        for word in METHOD_KEYWORDS:
            if word in text:
                points += 30

        fake_words = [
             "note",
    "message",
    "whiteboard",
    "she knew",
    "forgiven",
    "wrong suspect",
    "right motive",
    "no exit",
    "too late",

    "chess",
    "knight",
    "pawn",
    "bishop",
    "playing card",
    "ace",
    "queen",
    "domino",
    "toy",
    "toy airplane",
    "toy soldier",
    "toy train",
    "toy submarine",
    "rubber snake",
    "plastic skull",
    "plastic spider",

    "feather",
    "ribbon",
    "rose",
    "petal",
    "salt",
    "candle",
    "mirror",
    "compact",
    "glass eye",
    "mask",
    "scarf",
    "glove",
    "black glove",
    "white glove",
    "perfume",
    "lipstick",
    "kiss",
    "moth",
    "fly",
    "birdcage",

    "symbol",
    "ritual",
    "circle",
    "chalk",
    "red x",
    "cross",
    "obituary",
    "blank",
    "envelope",
    "thread",
    "marble",
    "button",
    "coin",
    "stamp",
    "ticket",
    "matchbook",
        ]

        for word in fake_words:
            if word in text:
                points -= 25

        return points

    best_clue = max(result.clues, key=score)
    return best_clue.description
def print_report(result: ClueFinding) -> None:
    """Pretty-print the detective result."""
    print(f"\nClues found: {len(result.clues)}")

    for clue in result.clues:
        print(f"- {clue.description} | suspicion: {clue.suspicion_level}/10")

    print(f"\nPrime suspect: {result.prime_suspect}")
    print(f"\nReasoning:\n{result.reasoning}")
   

async def investigate(scene: str,use_memory: bool = False  ) -> ClueFinding:
    """Run the detective agent on a crime scene description."""
    history = load_memory() if use_memory else []

    result = await detective.run(scene, message_history=history)
    save_memory(result.all_messages())
    if use_memory:
        save_memory(result.all_messages())
    return result.output

if __name__ == "__main__":
    import asyncio
    scene = """
    Famous antique clockmaker Elias Wren is found dead inside the locked glass
    conservatory of his estate during a dinner party. The room is humid and warm,
    but Wren is wearing a heavy wool overcoat. He is seated upright beside a marble
    table with a calm expression and no obvious sign of struggle.

    Every clock in the conservatory has stopped at 8:43 PM. Two minutes earlier,
    at 8:41 PM, an old dictation machine recorded Wren saying, "If the clock strikes,
    do not let her in." The restored astronomical clock has been jammed with an ivory
    chess pawn.

    There is a shallow cut behind Wren's left ear with very little blood. His right hand
    is stained blue with fountain pen ink, but no pen is found nearby. Under his fingernails
    is fine green dust like oxidized copper. His wine glass is untouched.

    On the marble table are a half-burned sheet of music, a silver spoon bent almost double,
    and a porcelain teacup stained with mud instead of tea. One of Wren's shoes is missing.
    The missing shoe is later found hanging by its lace from the branch of a lemon tree
    inside the conservatory.

    In Wren's coat pocket is a dead canary wrapped in a monogrammed handkerchief that does
    not belong to him. The room faintly smells of seawater even though the estate is far
    from the coast. Muddy footprints lead to the conservatory door, but none lead away.

    There are seven possible suspects: Wren's estranged daughter, his bitter apprentice,
    a local historian, a hired magician, Wren's physician, a silent housekeeper, and a
    music professor. The physician recently altered one of Wren's prescriptions. The
    apprentice claims Wren stole his clock designs. The historian says one restored artifact
    is a fake. The magician is known for escape tricks. The housekeeper claims she saw Wren
    speaking to someone who was already dead. The music professor recognizes the burned music
    as part of a composition never publicly published.

    The initial assumption is poison, but the body suggests something stranger: a medically
    precise death, possibly an air embolism. The strange clues may be real evidence, staged
Rules:
- Always reference specific physical evidence from the scene.
- For every clue, classify it as real, fake, or uncertain.
- A real clue directly supports the murder method, timeline, culprit, motive, or opportunity.
- A fake clue is likely staged, planted, exaggerated, or designed to mislead investigators.
- Uncertain means the clue may matter, but the evidence does not prove how yet.
- Only list physical clues explicitly present in the crime scene.
- Do not invent murder methods, tools, chemicals, hidden mechanisms, or extra backstory.
- If a detail is not stated in the scene, mark it as theory, not fact.
- Do not turn theories into facts.
- The prime suspect may be "Unknown" if the evidence is not strong enough.
- A single clue can suggest a timeline problem, but it cannot prove a culprit by itself.
- Confidence should be low when the evidence is weak or circumstantial.
- Consider who had knowledge, access, motive, and opportunity.
- Speak in a gritty 1940s noir detective voice.
- End with a clear prime suspect or say the culprit cannot be determined from the evidence.    misdirection, or both.
    """

    result = asyncio.run(investigate(scene))
    result.top_clue = choose_top_clue(result)

    print(f"\n📖 Title: {result.title}")
    print(f"🏛️ Setting: {result.setting}")
    print(f"\n🔍 Clues found: {len(result.clues)}")

    for index, clue in enumerate(result.clues, start=1):
        print(f"\nClue #{index}")
        print(f"Description: {clue.description}")
        print(f"Type: {clue.clue_type.upper()}")
        print(f"Suspicion: {clue.suspicion_level}/10")
        print(f"Location: {clue.location}")
    print(f"\n🎯 Top clue: {result.top_clue}")
    print(f"\n🕵️ Prime suspect: {result.prime_suspect}")
    print(f"🎯 Confidence: {result.confidence}/10")
    print(f"\nReasoning:\n{result.reasoning}")
