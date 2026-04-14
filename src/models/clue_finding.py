from pydantic import BaseModel

class Clue(BaseModel):
    description: str
    suspicion_level: int  # 1-10
    location: str

class ClueFinding(BaseModel):
    clues: list[Clue]
    prime_suspect: str
    reasoning: str
    confidence: int  # 1-10