# 🎩 Noir Mystery Story Engine

An agentic AI system that transforms crime scene descriptions into atmospheric noir mystery stories. Built with PydanticAI, ChromaDB, and classic detective literature.

## Architecture

```mermaid
flowchart TD
    A([User types crime scene]) --> B[Orchestrator Agent]

    B --> C[Detective Agent]
    B --> D[Witness Agent]
    B --> E[Narrator Agent]

    C --> F[(Clue Memory\nSliding Window)]
    F --> C

    D --> G[(ChromaDB\nVector Store)]
    G --> D

    G --> H[Sherlock Holmes Texts]
    G --> I[Agatha Christie Texts]

    C --> J[Tool: Clue Scorer]
    C --> K[Tool: Web Search]
    D --> L[Tool: File Reader]

    C --> M[Structured Output\nClueFinding Model]
    D --> M
    M --> E

    E --> N[Structured Output\nStoryReport Model]

    N --> O[pydantic-evals Suite\n10+ test cases]
    O --> P[Deterministic Check]
    O --> Q[LLM Judge]
    O --> R[Behavioral Check]

    N --> S([Final Noir Mystery Story])
```

## Setup

**1. Clone the repo**
```bash
git clone https://github.com/NhanNguyen-SG/noir-mystery-engine.git
cd noir-mystery-engine
```

**2. Create and activate virtual environment**

Mac/Linux:
```bash
python3.11 -m venv venv
source venv/bin/activate
```

Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

**3. Install dependencies**
```bash
pip install pydantic-ai pydantic-evals chromadb sentence-transformers python-dotenv httpx
```

**4. Set up environment variables**
```bash
cp .env.example .env
```
Then open `.env` and fill in your course API key and proxy URL:
```
OPENAI_API_KEY=your_course_key_here
OPENAI_BASE_URL=https://litellm.6640.ucf.spencerlyon.com
```

**5. Download the corpus and build the vector store**
```bash
cd corpus
curl -o sherlock_adventures.txt "https://www.gutenberg.org/files/1661/1661-0.txt"
curl -o sherlock_memoirs.txt "https://www.gutenberg.org/files/834/834-0.txt"
curl -o sherlock_return.txt "https://www.gutenberg.org/files/108/108-0.txt"
curl -o mysterious_affair.txt "https://www.gutenberg.org/files/863/863-0.txt"
cd ..
python src/rag/ingest.py
```

**6. Run the system**
```bash
PYTHONPATH=. python main.py
```

## Usage

```
$ PYTHONPATH=. python main.py

Welcome to the Noir Mystery Engine
Enter a crime scene description: A wealthy banker was found dead in his locked study...

Investigating...
Retrieving witness testimony...
Writing your story...

============================================================
TITLE: The Banker's Last Secret
SETTING: A rain-soaked manor, midnight
SUSPECT: The Butler
VERDICT: Guilty beyond reasonable doubt
...
```

## Project Structure

```
noir-mystery-engine/
├── src/
│   ├── agents/
│   │   ├── orchestrator.py     # Routes tasks between agents
│   │   ├── detective.py        # Reasons through clues + memory
│   │   ├── witness.py          # Retrieves from RAG corpus
│   │   └── narrator.py         # Writes final story
│   ├── tools/
│   │   ├── clue_scorer.py      # Scores and ranks clues
│   │   ├── web_search.py       # Web search tool
│   │   └── file_reader.py      # File reader tool
│   ├── models/
│   │   ├── clue_finding.py     # ClueFinding Pydantic model
│   │   └── story_report.py     # StoryReport Pydantic model
│   ├── rag/
│   │   ├── ingest.py           # Chunks and embeds corpus
│   │   └── retriever.py        # ChromaDB query wrapper
│   └── evals/
│       └── suite.py            # pydantic-evals test suite
├── corpus/                     # Public domain detective stories
├── overview.ipynb              # End-to-end walkthrough notebook
├── presentation/               # Week 14 slides
├── main.py                     # CLI entry point
├── pyproject.toml
├── .env.example
└── README.md
```

## Team

| Name | Contributions |
|------|--------------|
| Nhan | RAG pipeline, Detective agent, Witness agent, Orchestrator, Tools, Narrator agent |
| Khoi | Evaluation suite, CLI, Notebook, Presentation |
| Brent | Pending|

## Course

CAP-6640 — Computational Understanding of Natural Language
University of Central Florida — Spring 2026
