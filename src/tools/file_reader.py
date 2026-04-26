from dotenv import load_dotenv
load_dotenv()

from pathlib import Path

def read_case_file(filename: str) -> str:
    """
    Read a case file from the corpus directory.

    Args:
        filename: Name of the file to read from the corpus directory.

    Returns:
        First 2000 characters of the file contents as a string.

    Raises:
        ModelRetry: If the file does not exist or cannot be read.
    """
    corpus_path = Path("corpus") / filename

    if not corpus_path.exists():
        available = [f.name for f in Path("corpus").glob("*.txt")]
        raise FileNotFoundError(
            f"File '{filename}' not found in corpus. "
            f"Available files: {available}"
        )

    try:
        content = corpus_path.read_text(encoding="utf-8", errors="ignore")
        return content[:2000]
    except Exception as e:
        raise IOError(f"Could not read file '{filename}': {str(e)}")


if __name__ == "__main__":
    content = read_case_file("sherlock_adventures.txt")
    print(content[:500])