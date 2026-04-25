from dotenv import load_dotenv
load_dotenv()

import asyncio
from src.agents.orchestrator import run_mystery_engine


def print_banner():
    print("""
╔══════════════════════════════════════════════════════════╗
║           🎩  NOIR MYSTERY STORY ENGINE  🎩              ║
║        Where every crime scene tells a story...          ║
╚══════════════════════════════════════════════════════════╝
    """)


def print_divider():
    print("\n" + "═" * 60 + "\n")


async def main():
    print_banner()

    print("Describe your crime scene in as much detail as you like.")
    print("Press Enter twice when done.\n")

    lines = []
    while True:
        line = input()
        if line == "" and lines and lines[-1] == "":
            break
        lines.append(line)

    scene = "\n".join(lines).strip()

    if not scene:
        print("No scene provided. Exiting.")
        return

    print_divider()
    print("The investigation begins...\n")

    try:
        result = await run_mystery_engine(scene)

        print_divider()
        print(f"📖  TITLE:    {result.story.title}")
        print(f"🏛️   SETTING:  {result.story.setting}")
        print(f"🔍  CLUES:    {result.clues_found} discovered")
        print(f"🎯  TOP CLUE: {result.top_clue}")
        print(f"🕵️   SUSPECT:  {result.prime_suspect}")
        print_divider()

        print("THE STORY:\n")
        print(result.story.full_story)
        print_divider()

        print(f"⚖️   VERDICT: {result.story.verdict}")
        print_divider()

    except KeyboardInterrupt:
        print("\nInvestigation abandoned. The case goes cold...")
    except Exception as e:
        print(f"Something went wrong: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())