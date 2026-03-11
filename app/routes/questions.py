from fastapi import APIRouter, HTTPException
from bson import ObjectId
from app.db import get_db
from app.services.adaptive import select_best_question, get_ability_label

router = APIRouter()


@router.get("/next/{session_id}")
async def get_next_question(session_id: str):
    db = get_db()

    # Fetch session
    try:
        session = await db.sessions.find_one({"_id": ObjectId(session_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid session ID format")

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session["is_complete"]:
        raise HTTPException(status_code=400, detail="Session is already complete. Get your report!")

    if session["questions_answered"] >= session["max_questions"]:
        raise HTTPException(status_code=400, detail="Max questions reached. Get your report!")

    # Fetch all questions from DB
    all_questions = await db.questions.find().to_list(length=200)

    answered_ids = [
        str(record["question_id"]).strip()
        for record in session.get("answer_history", [])
    ]

    ability = session["current_ability"]

    # Debug log remove in production
    print(f"[DEBUG] Session {session_id}")
    print(f"[DEBUG] Questions answered: {session['questions_answered']}")
    print(f"[DEBUG] Answered IDs: {answered_ids}")
    print(f"[DEBUG] Current ability (θ): {ability}")

    # IRT selection
    best_question = select_best_question(ability, all_questions, answered_ids)

    if not best_question:
        raise HTTPException(status_code=404, detail="No more unanswered questions available")

    print(f"[DEBUG] Selected question: {str(best_question['_id'])} | difficulty: {best_question['difficulty']}")

    return {
        "question_id":      str(best_question["_id"]),
        "question_number":  session["questions_answered"] + 1,
        "total_questions":  session["max_questions"],
        "text":             best_question["text"],
        "options":          best_question["options"],
        "topic":            best_question["topic"],
        "tags":             best_question.get("tags", []),
        "current_ability":  ability,
        "ability_label":    get_ability_label(ability),
        # difficulty hidden from student — shown for testing only
        "difficulty":       best_question["difficulty"],
    }