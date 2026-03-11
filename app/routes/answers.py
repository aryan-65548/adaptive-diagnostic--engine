from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from bson import ObjectId
from app.db import get_db
from app.services.adaptive import update_ability

router = APIRouter()

class SubmitAnswerRequest(BaseModel):
    session_id: str
    question_id: str
    selected_answer: str   # "A", "B", "C", or "D"

@router.post("/submit")
async def submit_answer(request: SubmitAnswerRequest):
    db = get_db()

    # Fetch session
    try:
        session = await db.sessions.find_one({"_id": ObjectId(request.session_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid session ID")

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session["is_complete"]:
        raise HTTPException(status_code=400, detail="Session already complete")

    # Fetch question
    try:
        question = await db.questions.find_one({"_id": ObjectId(request.question_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid question ID")

    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    # Check answer
    is_correct = request.selected_answer.upper() == question["correct_answer"].upper()

    # IRT ability update
    old_ability = session["current_ability"]
    new_ability = update_ability(old_ability, question["difficulty"], is_correct)

    # Build answer record
    answer_record = {
        "question_id": request.question_id,
        "topic": question["topic"],
        "difficulty": question["difficulty"],
        "selected_answer": request.selected_answer.upper(),
        "correct_answer": question["correct_answer"],
        "was_correct": is_correct,
        "ability_before": old_ability,
        "ability_after": new_ability
    }

    # Update session
    new_count = session["questions_answered"] + 1
    is_complete = new_count >= session["max_questions"]

    await db.sessions.update_one(
        {"_id": ObjectId(request.session_id)},
        {
            "$set": {
                "current_ability": new_ability,
                "questions_answered": new_count,
                "is_complete": is_complete
            },
            "$push": {
                "answer_history": answer_record
            }
        }
    )

    return {
        "is_correct": is_correct,
        "correct_answer": question["correct_answer"],
        "ability_before": old_ability,
        "ability_after": new_ability,
        "ability_change": round(new_ability - old_ability, 4),
        "questions_answered": new_count,
        "is_complete": is_complete,
        "message": "✅ Correct! Keep going!" if is_correct else "❌ Incorrect. You got this!"
    }