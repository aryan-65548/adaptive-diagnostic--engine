from fastapi import APIRouter, HTTPException
from bson import ObjectId
from app.db import get_db
from app.services.adaptive import select_best_question

router = APIRouter()

@router.get("/next/{session_id}")
async def get_next_question(session_id: str):
    db = get_db()

    # Fetch session
    try:
        session = await db.sessions.find_one({"_id": ObjectId(session_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid session ID")

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session["is_complete"]:
        raise HTTPException(status_code=400, detail="Session is already complete")

    if session["questions_answered"] >= session["max_questions"]:
        raise HTTPException(status_code=400, detail="Max questions reached. Submit for report.")

    # Get all questions
    all_questions = await db.questions.find().to_list(length=100)

    # Get already answered question IDs
    answered_ids = [record["question_id"] for record in session["answer_history"]]

    # IRT selection — pick question closest to current ability
    ability = session["current_ability"]
    best_question = select_best_question(ability, all_questions, answered_ids)

    if not best_question:
        raise HTTPException(status_code=404, detail="No more questions available")

    return {
        "question_id": str(best_question["_id"]),
        "text": best_question["text"],
        "options": best_question["options"],
        "topic": best_question["topic"],
        "tags": best_question["tags"],
        "difficulty": best_question["difficulty"],   # remove this in production!
        "question_number": session["questions_answered"] + 1,
        "current_ability": ability
    }