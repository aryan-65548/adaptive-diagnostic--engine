from groq import Groq
from app.config import settings

client = Groq(api_key=settings.groq_api_key)

def build_prompt(session: dict) -> str:
    history = session["answer_history"]
    student_name = session["student_name"]
    final_ability = session["current_ability"]

    # Summarize performance by topic
    topic_stats = {}
    for record in history:
        topic = record["topic"]
        if topic not in topic_stats:
            topic_stats[topic] = {"correct": 0, "total": 0, "difficulties": []}
        topic_stats[topic]["total"] += 1
        topic_stats[topic]["difficulties"].append(record["difficulty"])
        if record["was_correct"]:
            topic_stats[topic]["correct"] += 1

    # Build topic summary string
    topic_summary = ""
    weak_topics = []
    for topic, stats in topic_stats.items():
        accuracy = round(stats["correct"] / stats["total"] * 100)
        avg_diff = round(sum(stats["difficulties"]) / len(stats["difficulties"]), 2)
        topic_summary += f"- {topic}: {accuracy}% accuracy, avg difficulty {avg_diff}\n"
        if accuracy < 60:
            weak_topics.append(topic)

    weak_topics_str = ", ".join(weak_topics) if weak_topics else "None identified"

    prompt = f"""
You are an expert GRE tutor analyzing a student's adaptive test performance.

Student: {student_name}
Final Ability Score (θ): {final_ability} (scale: 0.0 to 1.0)
Total Questions: {len(history)}

Performance by Topic:
{topic_summary}
Weak Topics (below 60% accuracy): {weak_topics_str}

Based on this data, generate a precise 3-step personalized study plan.
Each step must:
1. Target a specific weak area from the data above
2. Include a concrete action (not generic advice)
3. Include a recommended resource or technique

Format your response as JSON with this exact structure:
{{
  "overall_assessment": "2-3 sentence summary of the student's performance",
  "ability_level": "Beginner / Intermediate / Advanced based on θ score",
  "study_plan": [
    {{
      "step": 1,
      "focus": "topic name",
      "action": "specific action to take",
      "resource": "specific resource or technique",
      "time_estimate": "e.g. 3 days"
    }},
    {{
      "step": 2,
      "focus": "topic name",
      "action": "specific action to take",
      "resource": "specific resource or technique",
      "time_estimate": "e.g. 2 days"
    }},
    {{
      "step": 3,
      "focus": "topic name",
      "action": "specific action to take",
      "resource": "specific resource or technique",
      "time_estimate": "e.g. 4 days"
    }}
  ],
  "motivation": "one encouraging sentence for the student"
}}

Return ONLY the JSON. No extra text, no markdown, no explanation.
"""
    return prompt


async def generate_study_plan(session: dict) -> dict:
    prompt = build_prompt(session)

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are an expert GRE tutor. Always respond with valid JSON only."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.7,
        max_tokens=1000
    )

    raw = response.choices[0].message.content.strip()

    # Clean up in case model adds markdown fences
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    import json
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {
            "error": "Failed to parse LLM response",
            "raw_response": raw
        }