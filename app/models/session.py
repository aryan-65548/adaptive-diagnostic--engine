from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class AnswerRecord(BaseModel):
    question_id: str
    topic: str
    difficulty: float
    was_correct: bool
    ability_before: float
    ability_after: float

class UserSession(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    student_name: str
    current_ability: float = 0.5       # θ starts at 0.5
    questions_answered: int = 0
    max_questions: int = 10
    answer_history: List[AnswerRecord] = []
    is_complete: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True