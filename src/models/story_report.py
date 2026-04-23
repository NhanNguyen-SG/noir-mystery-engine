from pydantic import BaseModel

class StoryReport(BaseModel):
    title: str
    setting: str
    clue_summary: list[str]
    prime_suspect: str
    verdict: str
    full_story: str