from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from bson import ObjectId
from app.db import get_db
from app.services.adaptive import update_ability, get_ability_label

router = APIRouter()


class SubmitAnswerRequest(BaseModel):
    session_id:      str
    question_id:     str
    selected_answer: str   # "A", "B", "C", or "D"


@router.post("/submit")
async def submit_answer(request: SubmitAnswerRequest):
    db = get_db()

    # Fetch session
    try:
        session = await db.sessions.find_one({"_id": ObjectId(request.session_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid session ID format")

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session["is_complete"]:
        raise HTTPException(status_code=400, detail="Session already complete")

    # FIX: check if this question was already answered — prevent duplicate submissions
    answered_ids = [
        str(record["question_id"]).strip()
        for record in session.get("answer_history", [])
    ]
    if str(request.question_id).strip() in answered_ids:
        raise HTTPException(
            status_code=400,
            detail="This question was already answered. Call /question/next to get the next one."
        )

    # Fetch question
    try:
        question = await db.questions.find_one({"_id": ObjectId(request.question_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid question ID format")

    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    # Check answer
    is_correct = request.selected_answer.strip().upper() == question["correct_answer"].strip().upper()

    # IRT ability update
    old_ability = session["current_ability"]
    new_ability = update_ability(old_ability, question["difficulty"], is_correct)

    # Build answer record
    # FIX: store question_id as plain string — consistent with how we read it back
    answer_record = {
        "question_id":     str(request.question_id).strip(),
        "topic":           question["topic"],
        "difficulty":      question["difficulty"],
        "selected_answer": request.selected_answer.strip().upper(),
        "correct_answer":  question["correct_answer"].strip().upper(),
        "was_correct":     is_correct,
        "ability_before":  old_ability,
        "ability_after":   new_ability,
    }

    # Update session in DB
    new_count   = session["questions_answered"] + 1
    is_complete = new_count >= session["max_questions"]

    await db.sessions.update_one(
        {"_id": ObjectId(request.session_id)},
        {
            "$set": {
                "current_ability":    new_ability,
                "questions_answered": new_count,
                "is_complete":        is_complete,
            },
            "$push": {
                "answer_history": answer_record
            }
        }
    )

    return {
        "is_correct":          is_correct,
        "correct_answer":      question["correct_answer"].upper(),
        "selected_answer":     request.selected_answer.upper(),
        "ability_before":      old_ability,
        "ability_after":       new_ability,
        "ability_change":      round(new_ability - old_ability, 4),
        "ability_label":       get_ability_label(new_ability),
        "questions_answered":  new_count,
        "questions_remaining": session["max_questions"] - new_count,
        "is_complete":         is_complete,
        "message":             "Correct! Keep going!" if is_correct else "Incorrect. You got this!",
        "next_step":           "GET /session/{id}/study-plan" if is_complete else "GET /question/next/{session_id}",
    }