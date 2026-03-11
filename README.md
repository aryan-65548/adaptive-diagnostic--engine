#Adaptive Diagnostic Engine

An AI-powered adaptive testing system that uses **Item Response Theory (IRT)** to personalize question difficulty in real-time, and **Groq LLM** to generate personalized study plans based on student performance.

> Built as part of a HighScores AI internship assignment — a miniature version of the core adaptive assessment product.


## How It Works

1. Student starts a session → ability score θ initialised at **0.5**
2. System selects the question whose difficulty is **closest to current θ**
3. Student answers → θ updated using the **1PL Rasch Model**
4. Repeat for 10 questions → session complete
5. Groq LLM generates a **personalized study plan** based on weak topics

### The Math — 1PL Rasch Model

```
P(correct) = 1 / (1 + e^-(θ - b))

θ = student ability    (0.0 → 1.0)
b = question difficulty (0.0 → 1.0)

θ_new = θ_old + 0.3 × (actual - P(correct))
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| API Framework | FastAPI |
| Database | MongoDB (async via Motor) |
| LLM | Groq — llama-3.3-70b-versatile |
| Language | Python 3.9 |
| Config | Pydantic Settings |

---

##  Project Structure

```
adaptive-diagnostic-engine/
├── app/
│   ├── main.py              
│   ├── config.py            # Environment variable management
│   ├── models/
│   │   ├── question.py      # Question schema
│   │   └── session.py       # User session schema
│   ├── routes/
│   │   ├── session.py       # Session + report + study-plan endpoints
│   │   ├── questions.py     # next question endpoint
│   │   └── answers.py       # answer submission endpoint
│   ├── services/
│   │   ├── adaptive.py      # IRT Rasch Model logic
│   │   └── llm.py           # Groq LLM study plan generator
│   └── db/
│       ├── __init__.py      # Motor async MongoDB connection
│       └── seed.py          # 20 GRE question seeder
├── .env.example
├── .gitignore
└── requirements.txt
```

---

## Setup & Run

### Prerequisites
- Python 3.9+
- MongoDB running locally on port `27017`
- Groq API key → [console.groq.com](https://console.groq.com)

---
## 💡 Why Groq?

OpenAI and Anthropic both require a paid API key to get started.
Groq offers a **free tier** with generous rate limits, making this 
project completely free to run for anyone who wants to clone it.

The LLM service layer is fully abstracted — swapping to GPT-4 or 
Claude is a single line change in `.env`:

# Current (free)
GROQ_API_KEY=your_key

# Drop-in swap (if you have access)
OPENAI_API_KEY=your_key

### Installation

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/adaptive-diagnostic-engine.git
cd adaptive-diagnostic-engine

# Create virtual environment
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Open .env and add your GROQ_API_KEY
```

### Seed the Question Bank

```bash
python -m app.db.seed
```

### Start the Server

```bash
uvicorn app.main:app --reload
```

Swagger UI → [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

##  API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/session/start` | Create a new test session |
| `GET` | `/session/{id}` | Get session details |
| `GET` | `/session/{id}/report` | Performance report by topic |
| `GET` | `/session/{id}/study-plan` | AI-generated study plan (requires completed session) |
| `GET` | `/question/next/{id}` | Get next IRT-selected question |
| `POST` | `/answer/submit` | Submit answer and update θ |

---

## Session Flow

```
POST /session/start
        │
        ▼
GET  /question/next/{session_id}   ←── IRT selects question closest to θ
        │
        ▼
POST /answer/submit                ←── θ updated via Rasch model
        │
        ▼
   (repeat × 10)
        │
        ▼
GET  /session/{id}/report          ←── accuracy breakdown by topic
GET  /session/{id}/study-plan      ←── Groq LLM personalized plan
```

---

## Example Usage

**Start a session**
```bash
curl -X POST http://localhost:8000/session/start \
  -H "Content-Type: application/json" \
  -d '{"student_id": "student_001"}'
```

**Get next question**
```bash
curl http://localhost:8000/question/next/{session_id}
```

**Submit an answer**
```bash
curl -X POST http://localhost:8000/answer/submit \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "your_session_id",
    "question_id": "your_question_id",
    "selected_answer": "B"
  }'
```

**Get study plan** *(after all 10 questions answered)*
```bash
curl http://localhost:8000/session/{session_id}/study-plan
```

---

## Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
MONGODB_URI=mongodb://localhost:27017
DB_NAME=adaptive_engine
GROQ_API_KEY=your_groq_api_key_here
```

---

## IRT Ability Tracking — Example Session

```
Q1  difficulty 0.50  →  Wrong  →  θ: 0.50 → 0.35
Q2  difficulty 0.35  →  Right  →  θ: 0.35 → 0.48
Q3  difficulty 0.48  →  Right  →  θ: 0.48 → 0.59
Q4  difficulty 0.59  →  Wrong  →  θ: 0.59 → 0.47
Q5  difficulty 0.47  →  Right  →  θ: 0.47 → 0.58
...
Q10 difficulty 0.65  →  Right  →  θ: final 0.72  →  Advanced
```

The engine always targets the question where the student has ~50% chance of success — the optimal learning zone.

---

## AI Study Plan

Once all 10 questions are answered, the Groq LLM receives:

- Final θ score and ability level
- Per-topic accuracy breakdown
- Weak topics identified (below 60% accuracy)

And returns structured JSON:

```json
{
  "overall_assessment": "Strong algebra skills, needs work on reading comprehension",
  "ability_level": "Intermediate",
  "study_plan": [
    {"step": 1, "topic": "Reading Comprehension", "action": "..."},
    {"step": 2, "topic": "Vocabulary", "action": "..."},
    {"step": 3, "topic": "Practice", "action": "..."}
  ],
  "motivation": "You're making great progress..."
}
```

---

## Known Issues / Notes

- Study plan endpoint requires `is_complete: true` — answer all 10 questions first
- Questions are seeded with GRE-style content across algebra, geometry, vocabulary, and reading
- Difficulty field is intentionally excluded from `/question/next` response (security)

---

*Built with FastAPI · MongoDB · Groq LLM · Python 3.9*
