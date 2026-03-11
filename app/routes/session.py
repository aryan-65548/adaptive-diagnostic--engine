from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from app.db import get_db
from app.services.llm import generate_study_plan
from app.services.pdf_gen import generate_test_result_pdf, generate_study_plan_pdf
from datetime import datetime
from bson import ObjectId
import os

router = APIRouter()

# Directory to save generated PDFs
PDF_DIR = "generated_pdfs"
os.makedirs(PDF_DIR, exist_ok=True)


class StartSessionRequest(BaseModel):
    student_name: str


@router.post("/start")
async def start_session(request: StartSessionRequest):
    db = get_db()

    session = {
        "student_name":       request.student_name,
        "current_ability":    0.5,
        "questions_answered": 0,
        "max_questions":      10,
        "answer_history":     [],
        "is_complete":        False,
        "created_at":         datetime.utcnow()
    }

    result = await db.sessions.insert_one(session)

    return {
        "session_id":      str(result.inserted_id),
        "student_name":    request.student_name,
        "current_ability": 0.5,
        "message":         "Session started. Good luck! 🎯"
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
        "session_id":         str(session["_id"]),
        "student_name":       session["student_name"],
        "current_ability":    session["current_ability"],
        "questions_answered": session["questions_answered"],
        "max_questions":      session["max_questions"],
        "is_complete":        session["is_complete"],
        "answer_history":     session["answer_history"]
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

    total    = len(history)
    correct  = sum(1 for r in history if r["was_correct"])
    accuracy = round(correct / total * 100, 1)

    topic_breakdown = {}
    for record in history:
        topic = record["topic"]
        if topic not in topic_breakdown:
            topic_breakdown[topic] = {"correct": 0, "total": 0}
        topic_breakdown[topic]["total"] += 1
        if record["was_correct"]:
            topic_breakdown[topic]["correct"] += 1

    return {
        "student_name":    session["student_name"],
        "final_ability":   session["current_ability"],
        "total_questions": total,
        "correct_answers": correct,
        "accuracy_percent":accuracy,
        "is_complete":     session["is_complete"],
        "topic_breakdown": topic_breakdown,
        "answer_history":  history
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
        "student_name":  session["student_name"],
        "final_ability": session["current_ability"],
        "study_plan":    plan
    }


# ── NEW: PDF ENDPOINTS ────────────────────────────────────────────────────────

@router.get("/{session_id}/pdf/result")
async def download_result_pdf(session_id: str):
    """
    Generate and download the test result PDF.
    Shows all 10 questions, answers, ability tracking, topic breakdown.
    Can be called any time after at least 1 answer.
    """
    db = get_db()

    try:
        session = await db.sessions.find_one({"_id": ObjectId(session_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid session ID")

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if not session.get("answer_history"):
        raise HTTPException(status_code=400, detail="No answers yet — complete at least 1 question first")

    # Convert ObjectId to string so PDF generator can use it
    session["_id"] = str(session["_id"])

    output_path = os.path.join(PDF_DIR, f"result_{session_id}.pdf")
    generate_test_result_pdf(session, output_path)

    return FileResponse(
        path=output_path,
        media_type="application/pdf",
        filename=f"test_result_{session['student_name'].replace(' ', '_')}.pdf"
    )


@router.get("/{session_id}/pdf/study-plan")
async def download_study_plan_pdf(session_id: str):
    """
    Generate and download the study plan PDF.
    Calls Groq LLM, formats the plan, and returns it as a PDF.
    Requires session to be complete (all 10 questions answered).
    """
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
            detail="Complete all 10 questions first before generating a study plan PDF"
        )

    # Get study plan from Groq
    plan = await generate_study_plan(session)

    if "error" in plan:
        raise HTTPException(status_code=500, detail=f"LLM error: {plan.get('error')}")

    # Convert ObjectId to string
    session["_id"] = str(session["_id"])

    output_path = os.path.join(PDF_DIR, f"study_plan_{session_id}.pdf")
    generate_study_plan_pdf(session, plan, output_path)

    return FileResponse(
        path=output_path,
        media_type="application/pdf",
        filename=f"study_plan_{session['student_name'].replace(' ', '_')}.pdf"
    )