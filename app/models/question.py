from pydantic import BaseModel, Field
from typing import List, Optional
from bson import ObjectId

class Question(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    text: str
    options: List[str]          # ["A) ...", "B) ...", "C) ...", "D) ..."]
    correct_answer: str         # "A", "B", "C", or "D"
    difficulty: float           # 0.1 to 1.0
    topic: str                  # "Algebra", "Vocabulary", etc.
    tags: List[str]             # ["quadratic", "equations"]

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True