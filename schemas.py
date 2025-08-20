# schemas.py

from pydantic import BaseModel
from typing import List

class InterviewLog(BaseModel):
    candidate_name: str
    questions: List[str]
    answers: List[str]
