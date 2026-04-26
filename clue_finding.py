from pydantic import BaseModel,Field 
from typing import Literal

class Clue(BaseModel):
    description: str
    clue_type: Literal["real", "fake", "uncertain"]
    suspicion_level: int = Field(ge=1, le=10)
    location: str
    proves: str
    suggests: str

class Theory(BaseModel):
    claim: str
    confidence: int = Field(ge=1, le=10)
    evidence: list[str]    

class ClueFinding(BaseModel):
    title: str
    setting: str
    top_clue: str
    clues: list[Clue]
    likely_fake_clues: list[str]
    theories: list[Theory]
    prime_suspect: str
    reasoning: str
    confidence: int = Field(ge=1, le=10)