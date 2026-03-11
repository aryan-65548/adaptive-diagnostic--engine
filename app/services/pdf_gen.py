"""
PDF Generator for Adaptive Diagnostic Engine
Generates two PDFs:
  1. test_result_{session_id}.pdf  — all 10 questions, answers, ability tracking
  2. study_plan_{session_id}.pdf   — Groq LLM study plan formatted nicely

Drop this file at:  app/services/pdf_generator.py
Call it from:       app/routes/session.py  (new /pdf endpoint)
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, white
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
import os

# ── Colours ──────────────────────────────────────────────────────────────────
BG    = white
CARD  = HexColor("#f5f5f5")
CARD2 = HexColor("#ffffff")
ACC   = HexColor("#000000")
ACC2  = HexColor("#222222")
ACC3  = HexColor("#444444")
TX    = HexColor("#222222")
MT    = HexColor("#666666")
GR    = HexColor("#222222")
YL    = HexColor("#444444")
RD    = HexColor("#000000")
CY    = HexColor("#333333")
PU    = HexColor("#444444")
BD    = HexColor("#cccccc")
WH    = white


def _dark_bg(canvas, doc):
    canvas.saveState()
    from reportlab.lib.pagesizes import letter
    w, h = letter
    canvas.setFillColor(white)
    canvas.rect(0, 0, w, h, fill=1, stroke=0)
    canvas.setStrokeColor(HexColor("#cccccc"))
    canvas.setLineWidth(0.5)
    canvas.line(0.55 * inch, 0.45 * inch, w - 0.55 * inch, 0.45 * inch)
    canvas.setFillColor(HexColor("#666666"))
    canvas.setFont("Helvetica", 7.5)
    canvas.drawCentredString(
        w / 2, 0.28 * inch,
        f"Adaptive Diagnostic Engine  ·  HighScores AI  ·  Page {doc.page}"
    )
    canvas.restoreState()


def _S(name, **kwargs):
    return ParagraphStyle(name, **kwargs)


def _tbl(data, widths, header_color=ACC):
    t = Table(data, colWidths=widths)
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0),  header_color),
        ("TEXTCOLOR",     (0, 0), (-1, 0),  WH),
        ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, 0),  9),
        ("BACKGROUND",    (0, 1), (-1, -1), CARD),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [CARD, CARD2]),
        ("TEXTCOLOR",     (0, 1), (-1, -1), TX),
        ("FONTNAME",      (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",      (0, 1), (-1, -1), 8.5),
        ("GRID",          (0, 0), (-1, -1), 0.4, BD),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
    ]))
    return t


# ══════════════════════════════════════════════════════════════════════════════
# PDF 1 — TEST RESULT
# ══════════════════════════════════════════════════════════════════════════════
def generate_test_result_pdf(session: dict, output_path: str) -> str:
    """
    Generate a PDF showing all questions, answers, and ability tracking.
    session = the raw MongoDB session document (already as dict).
    """
    doc = SimpleDocTemplate(
        output_path, pagesize=letter,
        leftMargin=.55 * inch, rightMargin=.55 * inch,
        topMargin=.6 * inch,   bottomMargin=.6 * inch
    )

    # ── Styles ────────────────────────────────────────────────────────────────
    title_s  = _S("t",  fontSize=28, leading=36, textColor=WH,  fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=4)
    sub_s    = _S("su", fontSize=13, leading=18, textColor=ACC2, fontName="Helvetica",      alignment=TA_CENTER, spaceAfter=4)
    meta_s   = _S("me", fontSize=9,  leading=13, textColor=MT,   fontName="Helvetica",      alignment=TA_CENTER)
    sec_s    = _S("se", fontSize=14, leading=18, textColor=ACC,  fontName="Helvetica-Bold", spaceBefore=12, spaceAfter=4)
    body_s   = _S("bo", fontSize=9.5,leading=14, textColor=TX,   fontName="Helvetica",      spaceAfter=4)
    qnum_s   = _S("qn", fontSize=10, leading=14, textColor=ACC3, fontName="Helvetica-Bold", spaceBefore=10, spaceAfter=2)
    qtxt_s   = _S("qt", fontSize=10, leading=15, textColor=WH,   fontName="Helvetica-Bold", spaceAfter=4)
    corr_s   = _S("co", fontSize=9,  leading=13, textColor=GR,   fontName="Helvetica-Bold", spaceAfter=2)
    wrong_s  = _S("wr", fontSize=9,  leading=13, textColor=RD,   fontName="Helvetica-Bold", spaceAfter=2)
    note_s   = _S("no", fontSize=8.5,leading=12, textColor=MT,   fontName="Helvetica",      spaceAfter=6)

    def b(t):   return Paragraph(t, body_s)
    def sp(h=6):return Spacer(1, h)
    def hr():   return HRFlowable(width="100%", thickness=0.8, color=BD, spaceAfter=6)
    def hr2():  return HRFlowable(width="100%", thickness=1.3, color=ACC, spaceAfter=8)

    history  = session.get("answer_history", [])
    name     = session.get("student_name", "Student")
    ability  = session.get("current_ability", 0.5)
    total    = len(history)
    correct  = sum(1 for r in history if r["was_correct"])
    accuracy = round(correct / total * 100, 1) if total else 0

    def ability_label(theta):
        if theta < 0.35:  return "Beginner"
        if theta < 0.65:  return "Intermediate"
        return "Advanced"

    def diff_label(d):
        if d < 0.35:  return "Easy"
        if d < 0.65:  return "Medium"
        return "Hard"

    story = []

    # ── Cover ─────────────────────────────────────────────────────────────────
    story += [
        sp(60),
        Paragraph("TEST RESULT REPORT", title_s),
        Paragraph("Adaptive Diagnostic Engine — HighScores AI", sub_s),
        sp(6),
        HRFlowable(width="50%", thickness=1.5, color=ACC, spaceAfter=12),
        Paragraph(f"Student: {name}", meta_s), sp(3),
        Paragraph(f"Questions: {total}  ·  Correct: {correct}  ·  Accuracy: {accuracy}%", meta_s), sp(3),
        Paragraph(f"Final Ability (θ): {ability}  ·  Level: {ability_label(ability)}", meta_s),
        PageBreak(),
    ]

    # ── Summary Table ──────────────────────────────────────────────────────────
    story.append(Paragraph("SESSION SUMMARY", sec_s))
    story.append(hr2())

    # Score card
    score_color = GR if accuracy >= 70 else YL if accuracy >= 50 else RD
    score_data = [
        ["Metric", "Value"],
        ["Student Name",      name],
        ["Total Questions",   str(total)],
        ["Correct Answers",   str(correct)],
        ["Accuracy",          f"{accuracy}%"],
        ["Final Ability (θ)", str(ability)],
        ["Ability Level",     ability_label(ability)],
    ]
    story.append(_tbl(score_data, [2.5*inch, 4.2*inch]))
    story.append(sp(12))

    # ── Ability Progression Table ──────────────────────────────────────────────
    story.append(Paragraph("ABILITY (θ) PROGRESSION", sec_s))
    story.append(hr2())

    prog_data = [["Q#", "Topic", "Difficulty", "Level", "Your Answer", "Correct?", "θ Before", "θ After"]]
    for i, r in enumerate(history):
        correct_mark = "✓" if r["was_correct"] else "✗"
        prog_data.append([
            str(i + 1),
            r.get("topic", "—"),
            str(r.get("difficulty", "—")),
            diff_label(r.get("difficulty", 0.5)),
            r.get("selected_answer", "—"),
            correct_mark,
            str(r.get("ability_before", "—")),
            str(r.get("ability_after", "—")),
        ])

    prog_tbl = Table(prog_data, colWidths=[
        0.35*inch, 1.3*inch, 0.7*inch, 0.6*inch,
        0.8*inch, 0.6*inch, 0.7*inch, 0.7*inch
    ])
    prog_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0),  ACC),
        ("TEXTCOLOR",     (0, 0), (-1, 0),  WH),
        ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, 0),  8),
        ("BACKGROUND",    (0, 1), (-1, -1), CARD),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [CARD, CARD2]),
        ("TEXTCOLOR",     (0, 1), (-1, -1), TX),
        ("FONTNAME",      (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",      (0, 1), (-1, -1), 8),
        ("GRID",          (0, 0), (-1, -1), 0.4, BD),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 5),
        ("ALIGN",         (5, 1), (5, -1),  "CENTER"),
    ]))

    # Colour correct/incorrect rows
    for i, r in enumerate(history):
        row = i + 1
        color = HexColor("#0f4429") if r["was_correct"] else HexColor("#3d0814")
        prog_tbl.setStyle(TableStyle([
            ("BACKGROUND", (5, row), (5, row), color),
            ("TEXTCOLOR",  (5, row), (5, row), GR if r["was_correct"] else RD),
            ("FONTNAME",   (5, row), (5, row), "Helvetica-Bold"),
        ]))

    story.append(prog_tbl)
    story.append(sp(12))

    # ── Per-topic breakdown ────────────────────────────────────────────────────
    story.append(Paragraph("TOPIC BREAKDOWN", sec_s))
    story.append(hr2())

    topic_stats = {}
    for r in history:
        t = r.get("topic", "Unknown")
        if t not in topic_stats:
            topic_stats[t] = {"correct": 0, "total": 0}
        topic_stats[t]["total"] += 1
        if r["was_correct"]:
            topic_stats[t]["correct"] += 1

    topic_data = [["Topic", "Correct", "Total", "Accuracy", "Status"]]
    for topic, stats in topic_stats.items():
        acc = round(stats["correct"] / stats["total"] * 100, 1)
        status = "✓ Strong" if acc >= 70 else "△ Moderate" if acc >= 50 else "✗ Needs Work"
        topic_data.append([topic, str(stats["correct"]), str(stats["total"]), f"{acc}%", status])

    story.append(_tbl(topic_data, [2.2*inch, 0.8*inch, 0.8*inch, 0.9*inch, 1.5*inch]))
    story.append(sp(12))

    # ── Question-by-question detail ────────────────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("QUESTION-BY-QUESTION DETAIL", sec_s))
    story.append(hr2())

    for i, r in enumerate(history):
        is_correct = r["was_correct"]
        card_color = HexColor("#0f4429") if is_correct else HexColor("#3d0814")
        result_color = GR if is_correct else RD
        result_text = "✓  CORRECT" if is_correct else "✗  INCORRECT"

        block = [
            Paragraph(
                f"Question {i+1}  ·  {r.get('topic','').upper()}  ·  "
                f"Difficulty: {r.get('difficulty','?')} ({diff_label(r.get('difficulty',0.5))})",
                qnum_s
            ),
            Table([[
                Paragraph(result_text, _S(f"rt{i}", fontSize=9, textColor=result_color, fontName="Helvetica-Bold")),
                Paragraph(f"Your answer: {r.get('selected_answer','?')}  ·  Correct: {r.get('correct_answer','?')}", _S(f"an{i}", fontSize=9, textColor=TX, fontName="Helvetica")),
                Paragraph(f"θ: {r.get('ability_before','?')} → {r.get('ability_after','?')}", _S(f"ab{i}", fontSize=9, textColor=CY, fontName="Helvetica-Bold")),
            ]], colWidths=[1.2*inch, 3.8*inch, 1.7*inch],
            style=TableStyle([
                ("BACKGROUND", (0,0), (-1,-1), card_color),
                ("VALIGN",     (0,0), (-1,-1), "MIDDLE"),
                ("TOPPADDING", (0,0), (-1,-1), 6),
                ("BOTTOMPADDING",(0,0),(-1,-1),6),
                ("LEFTPADDING",(0,0),(-1,-1),8),
                ("GRID",       (0,0), (-1,-1), 0.3, BD),
            ])),
            sp(6),
        ]
        story += block

    story.append(sp(12))
    story.append(hr())
    story.append(Paragraph(
        f"Final ability score: {ability} ({ability_label(ability)})  ·  "
        f"Overall accuracy: {accuracy}%  ·  See study plan PDF for personalised recommendations.",
        _S("fin", fontSize=9, textColor=MT, fontName="Helvetica-Oblique", alignment=TA_CENTER)
    ))

    doc.build(story, onFirstPage=_dark_bg, onLaterPages=_dark_bg)
    return output_path


# ══════════════════════════════════════════════════════════════════════════════
# PDF 2 — STUDY PLAN
# ══════════════════════════════════════════════════════════════════════════════
def generate_study_plan_pdf(session: dict, study_plan: dict, output_path: str) -> str:
    """
    Generate a nicely formatted study plan PDF from Groq LLM output.
    study_plan = the parsed JSON from generate_study_plan()
    """
    doc = SimpleDocTemplate(
        output_path, pagesize=letter,
        leftMargin=.55 * inch, rightMargin=.55 * inch,
        topMargin=.6 * inch,   bottomMargin=.6 * inch
    )

    title_s = _S("t2", fontSize=28, leading=36, textColor=WH,  fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=4)
    sub_s   = _S("s2", fontSize=13, leading=18, textColor=ACC2, fontName="Helvetica",      alignment=TA_CENTER, spaceAfter=4)
    meta_s  = _S("m2", fontSize=9,  leading=13, textColor=MT,   fontName="Helvetica",      alignment=TA_CENTER)
    sec_s   = _S("sc", fontSize=14, leading=18, textColor=ACC,  fontName="Helvetica-Bold", spaceBefore=12, spaceAfter=4)
    body_s  = _S("b2", fontSize=9.5,leading=14, textColor=TX,   fontName="Helvetica",      spaceAfter=4, alignment=TA_JUSTIFY)
    lbl_s   = _S("lb", fontSize=8.5,leading=12, textColor=YL,   fontName="Helvetica-Bold", spaceAfter=2)
    step_s  = _S("st", fontSize=13, leading=18, textColor=ACC3, fontName="Helvetica-Bold", spaceBefore=8, spaceAfter=3)
    val_s   = _S("vl", fontSize=9.5,leading=14, textColor=TX,   fontName="Helvetica",      spaceAfter=3)
    motiv_s = _S("mo", fontSize=11, leading=16, textColor=ACC2, fontName="Helvetica-Oblique", alignment=TA_CENTER, spaceAfter=4)

    def b(t):    return Paragraph(t, body_s)
    def sp(h=6): return Spacer(1, h)
    def hr2():   return HRFlowable(width="100%", thickness=1.3, color=ACC, spaceAfter=8)
    def hr():    return HRFlowable(width="100%", thickness=0.8, color=BD,  spaceAfter=6)

    name    = session.get("student_name", "Student")
    ability = session.get("current_ability", 0.5)
    history = session.get("answer_history", [])
    total   = len(history)
    correct = sum(1 for r in history if r["was_correct"])
    acc     = round(correct / total * 100, 1) if total else 0

    overall     = study_plan.get("overall_assessment", "N/A")
    level       = study_plan.get("ability_level", "N/A")
    steps       = study_plan.get("study_plan", [])
    motivation  = study_plan.get("motivation", "")

    story = []

    # ── Cover ─────────────────────────────────────────────────────────────────
    story += [
        sp(60),
        Paragraph("PERSONALISED STUDY PLAN", title_s),
        Paragraph("Adaptive Diagnostic Engine — Powered by Groq LLM", sub_s),
        sp(6),
        HRFlowable(width="50%", thickness=1.5, color=ACC2, spaceAfter=12),
        Paragraph(f"Student: {name}  ·  Ability Level: {level}", meta_s), sp(3),
        Paragraph(f"Final θ: {ability}  ·  Accuracy: {acc}%  ·  Questions: {total}", meta_s),
        PageBreak(),
    ]

    # ── Overall Assessment ─────────────────────────────────────────────────────
    story.append(Paragraph("OVERALL ASSESSMENT", sec_s))
    story.append(hr2())

    assess_data = [
        ["Student",        name],
        ["Ability Score",  f"{ability}  (scale: 0.0 → 1.0)"],
        ["Ability Level",  level],
        ["Accuracy",       f"{acc}%  ({correct}/{total} correct)"],
    ]
    story.append(_tbl(assess_data, [2.2*inch, 4.5*inch]))
    story.append(sp(10))
    story.append(Paragraph(overall, body_s))
    story.append(sp(12))

    # ── Topic Performance ──────────────────────────────────────────────────────
    story.append(Paragraph("TOPIC PERFORMANCE", sec_s))
    story.append(hr2())

    topic_stats = {}
    for r in history:
        t = r.get("topic", "Unknown")
        if t not in topic_stats:
            topic_stats[t] = {"correct": 0, "total": 0}
        topic_stats[t]["total"] += 1
        if r["was_correct"]:
            topic_stats[t]["correct"] += 1

    topic_data = [["Topic", "Score", "Accuracy", "Verdict"]]
    for topic, stats in topic_stats.items():
        topic_acc = round(stats["correct"] / stats["total"] * 100, 1)
        verdict = "Strong ✓" if topic_acc >= 70 else "Needs Work ✗"
        topic_data.append([topic, f"{stats['correct']}/{stats['total']}", f"{topic_acc}%", verdict])

    story.append(_tbl(topic_data, [2.2*inch, 1.0*inch, 1.0*inch, 2.5*inch]))
    story.append(sp(12))

    # ── 3-Step Study Plan ──────────────────────────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("YOUR 3-STEP STUDY PLAN", sec_s))
    story.append(hr2())
    story.append(b("Generated by Groq LLM (llama-3.3-70b-versatile) based on your exact performance data."))
    story.append(sp(8))

    step_colors = [HexColor("#0d2137"), HexColor("#1a0d37"), HexColor("#0d2113")]
    step_accents = [ACC, PU, ACC2]

    for i, step in enumerate(steps):
        accent = step_accents[i % len(step_accents)]
        bg     = step_colors[i % len(step_colors)]

        step_num   = step.get("step", i + 1)
        focus      = step.get("focus", "—")
        action     = step.get("action", "—")
        resource   = step.get("resource", "—")
        time_est   = step.get("time_estimate", "—")

        # Step header
        story.append(Paragraph(f"STEP {step_num}  —  {focus.upper()}", _S(
            f"sh{i}", fontSize=13, textColor=accent, fontName="Helvetica-Bold",
            spaceBefore=10, spaceAfter=4
        )))

        # Step detail table
        step_data = [
            ["Focus Area", focus],
            ["Action",     action],
            ["Resource",   resource],
            ["Time",       time_est],
        ]
        step_tbl = Table(step_data, colWidths=[1.4*inch, 5.3*inch])
        step_tbl.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (0, -1), bg),
            ("BACKGROUND",    (1, 0), (1, -1), CARD),
            ("TEXTCOLOR",     (0, 0), (0, -1), accent),
            ("TEXTCOLOR",     (1, 0), (1, -1), TX),
            ("FONTNAME",      (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME",      (1, 0), (1, -1), "Helvetica"),
            ("FONTSIZE",      (0, 0), (-1, -1), 9),
            ("GRID",          (0, 0), (-1, -1), 0.4, BD),
            ("VALIGN",        (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING",    (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ]))
        story.append(step_tbl)
        story.append(sp(10))

    # ── Motivation ─────────────────────────────────────────────────────────────
    if motivation:
        story.append(sp(12))
        story.append(hr())
        story.append(Paragraph(f'"{motivation}"', motiv_s))
        story.append(hr())

    story.append(sp(16))
    story.append(Paragraph(
        "This plan was generated by Groq LLM based on your real test performance. "
        "Follow the steps in order for maximum improvement.",
        _S("disc", fontSize=8.5, textColor=MT, fontName="Helvetica-Oblique", alignment=TA_CENTER)
    ))

    doc.build(story, onFirstPage=_dark_bg, onLaterPages=_dark_bg)
    return output_path