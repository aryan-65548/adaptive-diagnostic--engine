from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.db import get_db
from app.services.llm import generate_study_plan
from datetime import datetime
from bson import ObjectId

router = APIRouter()

class StartSessionRequest(BaseModel):
    student_name: str

@router.post("/start")
async def start_session(request: StartSessionRequest):
    db = get_db()

    session = {
        "student_name": request.student_name,
        "current_ability": 0.5,
        "questions_answered": 0,
        "max_questions": 1,
        "answer_history": [],
        "is_complete": False,
        "created_at": datetime.utcnow()
    }

    result = await db.sessions.insert_one(session)

    return {
        "session_id": str(result.inserted_id),
        "student_name": request.student_name,
        "current_ability": 0.5,
        "message": "Session started. Good luck! 🎯"
    }


@router.get("/{session_id}")
async def get_session(session_id: str):
    db = get_db()

    try:
        session = await db.sessions.find_one({"_id": ObjectId(session_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid session ID")

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "session_id": str(session["_id"]),
        "student_name": session["student_name"],
        "current_ability": session["current_ability"],
        "questions_answered": session["questions_answered"],
        "max_questions": session["max_questions"],
        "is_complete": session["is_complete"],
        "answer_history": session["answer_history"]
    }


@router.get("/{session_id}/report")
async def get_report(session_id: str):
    db = get_db()

    try:
        session = await db.sessions.find_one({"_id": ObjectId(session_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid session ID")

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    history = session["answer_history"]
    if not history:
        raise HTTPException(status_code=400, detail="No answers recorded yet")

    total = len(history)
    correct = sum(1 for r in history if r["was_correct"])
    accuracy = round(correct / total * 100, 1)

    # Per topic breakdown
    topic_breakdown = {}
    for record in history:
        topic = record["topic"]
        if topic not in topic_breakdown:
            topic_breakdown[topic] = {"correct": 0, "total": 0}
        topic_breakdown[topic]["total"] += 1
        if record["was_correct"]:
            topic_breakdown[topic]["correct"] += 1

    return {
        "student_name": session["student_name"],
        "final_ability": session["current_ability"],
        "total_questions": total,
        "correct_answers": correct,
        "accuracy_percent": accuracy,
        "is_complete": session["is_complete"],
        "topic_breakdown": topic_breakdown,
        "answer_history": history
    }


@router.get("/{session_id}/study-plan")
async def get_study_plan(session_id: str):
    db = get_db()

    try:
        session = await db.sessions.find_one({"_id": ObjectId(session_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid session ID")

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if not session["is_complete"]:
        raise HTTPException(
            status_code=400,
            detail="Complete all 10 questions before generating a study plan"
        )

    plan = await generate_study_plan(session)

    return {
        "student_name": session["student_name"],
        "final_ability": session["current_ability"],
        "study_plan": plan
    }
