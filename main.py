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

def read_scene_from_file(file_path: str) -> str:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if not path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")

    if path.suffix.lower() != ".txt":
        raise ValueError("Please provide a .txt file")

    return path.read_text(encoding="utf-8").strip()



async def main():
    parser = argparse.ArgumentParser(description="Noir Mystery Story Engine")
    parser.add_argument(
        "--file",
        "-f",
        help="Path to a .txt file containing the crime scene",
    )

    args = parser.parse_args()

    print_banner()

    if args.file:
        scene = read_scene_from_file(args.file)
    else:
        scene = read_scene_from_terminal()

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