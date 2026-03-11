from pymongo import MongoClient
from app.config import settings

questions = [

    # ── ALGEBRA (7 questions, difficulty 0.1 → 0.95) ──────────────────────────
    {
        "text": "Solve for x: 2x + 5 = 13",
        "options": ["A) 2", "B) 3", "C) 4", "D) 5"],
        "correct_answer": "C",
        "difficulty": 0.1,
        "topic": "Algebra",
        "tags": ["linear equations", "basic"]
    },
    {
        "text": "If f(x) = 3x² - 2x + 1, what is f(2)?",
        "options": ["A) 9", "B) 11", "C) 12", "D) 14"],
        "correct_answer": "A",
        "difficulty": 0.3,
        "topic": "Algebra",
        "tags": ["functions", "quadratic"]
    },
    {
        "text": "Simplify: (x² - 9) / (x - 3)",
        "options": ["A) x - 3", "B) x + 3", "C) x² + 3", "D) x - 9"],
        "correct_answer": "B",
        "difficulty": 0.4,
        "topic": "Algebra",
        "tags": ["factoring", "simplification"]
    },
    {
        "text": "For what values of x is x² - 5x + 6 < 0?",
        "options": ["A) x < 2", "B) 2 < x < 3", "C) x > 3", "D) x < 2 or x > 3"],
        "correct_answer": "B",
        "difficulty": 0.55,
        "topic": "Algebra",
        "tags": ["inequalities", "quadratic"]
    },
    {
        "text": "If log₂(x) + log₂(x-2) = 3, find x.",
        "options": ["A) 2", "B) 3", "C) 4", "D) 6"],
        "correct_answer": "C",
        "difficulty": 0.75,
        "topic": "Algebra",
        "tags": ["logarithms"]
    },
    {
        "text": "The sum of roots of 3x² - kx + 6 = 0 is 4. Find k.",
        "options": ["A) 6", "B) 8", "C) 10", "D) 12"],
        "correct_answer": "D",
        "difficulty": 0.85,
        "topic": "Algebra",
        "tags": ["quadratic", "roots", "vieta"]
    },
    {
        "text": "If 2^(x+1) = 8^(x-1), find x.",
        "options": ["A) 1", "B) 2", "C) 3", "D) 4"],
        "correct_answer": "D",
        "difficulty": 0.95,
        "topic": "Algebra",
        "tags": ["exponential equations", "advanced"]
    },

    # ── GEOMETRY (6 questions, difficulty 0.15 → 0.85) ────────────────────────
    {
        "text": "A circle has radius 7. What is its area? (use π ≈ 3.14)",
        "options": ["A) 43.96", "B) 49", "C) 153.86", "D) 154"],
        "correct_answer": "C",
        "difficulty": 0.15,
        "topic": "Geometry",
        "tags": ["circle", "area"]
    },
    {
        "text": "Triangle ABC has angles A=55° and B=75°. What is angle C?",
        "options": ["A) 40°", "B) 50°", "C) 55°", "D) 60°"],
        "correct_answer": "B",
        "difficulty": 0.2,
        "topic": "Geometry",
        "tags": ["triangles", "angles"]
    },
    {
        "text": "A rectangle has perimeter 36 and length 10. What is its area?",
        "options": ["A) 70", "B) 80", "C) 90", "D) 100"],
        "correct_answer": "B",
        "difficulty": 0.35,
        "topic": "Geometry",
        "tags": ["rectangle", "perimeter", "area"]
    },
    {
        "text": "A cylinder has radius 3 and height 10. What is its volume? (π ≈ 3.14)",
        "options": ["A) 188.4", "B) 282.6", "C) 314", "D) 94.2"],
        "correct_answer": "B",
        "difficulty": 0.45,
        "topic": "Geometry",
        "tags": ["cylinder", "volume", "3D"]
    },
    {
        "text": "Two similar triangles have sides in ratio 3:5. What is the ratio of their areas?",
        "options": ["A) 3:5", "B) 6:10", "C) 9:25", "D) 27:125"],
        "correct_answer": "C",
        "difficulty": 0.7,
        "topic": "Geometry",
        "tags": ["similarity", "area ratio"]
    },
    {
        "text": "A cone has base radius 4 and slant height 5. What is its lateral surface area? (π ≈ 3.14)",
        "options": ["A) 62.8", "B) 50.24", "C) 75.36", "D) 80"],
        "correct_answer": "A",
        "difficulty": 0.85,
        "topic": "Geometry",
        "tags": ["cone", "surface area", "3D"]
    },

    # ── VOCABULARY (7 questions, difficulty 0.1 → 0.9) ────────────────────────
    {
        "text": "Choose the word most similar in meaning to HAPPY:",
        "options": ["A) Sad", "B) Joyful", "C) Angry", "D) Tired"],
        "correct_answer": "B",
        "difficulty": 0.1,
        "topic": "Vocabulary",
        "tags": ["synonyms", "basic"]
    },
    {
        "text": "Choose the word most similar in meaning to BENEVOLENT:",
        "options": ["A) Hostile", "B) Charitable", "C) Indifferent", "D) Greedy"],
        "correct_answer": "B",
        "difficulty": 0.2,
        "topic": "Vocabulary",
        "tags": ["synonyms", "GRE word"]
    },
    {
        "text": "Choose the word most opposite in meaning to LOQUACIOUS:",
        "options": ["A) Talkative", "B) Verbose", "C) Taciturn", "D) Eloquent"],
        "correct_answer": "C",
        "difficulty": 0.5,
        "topic": "Vocabulary",
        "tags": ["antonyms", "GRE word"]
    },
    {
        "text": "The professor's _______ remarks confused even the brightest students.",
        "options": ["A) lucid", "B) abstruse", "C) trite", "D) candid"],
        "correct_answer": "B",
        "difficulty": 0.65,
        "topic": "Vocabulary",
        "tags": ["fill in the blank", "GRE word"]
    },
    {
        "text": "CAPITULATE most nearly means:",
        "options": ["A) Summarize", "B) Behead", "C) Surrender", "D) Expand"],
        "correct_answer": "C",
        "difficulty": 0.7,
        "topic": "Vocabulary",
        "tags": ["synonyms", "GRE word"]
    },
    {
        "text": "Her _______ nature made it impossible to predict her reaction — she was equally likely to laugh or rage.",
        "options": ["A) stolid", "B) capricious", "C) phlegmatic", "D) sanguine"],
        "correct_answer": "B",
        "difficulty": 0.85,
        "topic": "Vocabulary",
        "tags": ["fill in the blank", "advanced GRE"]
    },
    {
        "text": "The scholar's _______ treatise was praised for dismantling decades of conventional wisdom with surgical precision.",
        "options": ["A) tendentious", "B) perspicacious", "C) lachrymose", "D) nugatory"],
        "correct_answer": "B",
        "difficulty": 0.9,
        "topic": "Vocabulary",
        "tags": ["fill in the blank", "advanced GRE"]
    },

    # ── ARITHMETIC (5 questions, difficulty 0.1 → 0.75) ──────────────────────
    {
        "text": "What is 15% of 240?",
        "options": ["A) 24", "B) 36", "C) 48", "D) 30"],
        "correct_answer": "B",
        "difficulty": 0.1,
        "topic": "Arithmetic",
        "tags": ["percentage", "basic"]
    },
    {
        "text": "A train travels 180 km in 2.5 hours. What is its average speed?",
        "options": ["A) 60 km/h", "B) 65 km/h", "C) 70 km/h", "D) 72 km/h"],
        "correct_answer": "D",
        "difficulty": 0.3,
        "topic": "Arithmetic",
        "tags": ["speed", "distance", "time"]
    },
    {
        "text": "If a price increases by 20% then decreases by 20%, the net change is:",
        "options": ["A) 0%", "B) -4%", "C) +4%", "D) -2%"],
        "correct_answer": "B",
        "difficulty": 0.55,
        "topic": "Arithmetic",
        "tags": ["percentage", "tricky"]
    },
    {
        "text": "A and B together can complete a job in 6 days. A alone takes 10 days. How long does B take alone?",
        "options": ["A) 12 days", "B) 15 days", "C) 16 days", "D) 20 days"],
        "correct_answer": "B",
        "difficulty": 0.65,
        "topic": "Arithmetic",
        "tags": ["work", "rates"]
    },
    {
        "text": "A shopkeeper marks a price 40% above cost price and gives a 25% discount. What is the profit percent?",
        "options": ["A) 2%", "B) 5%", "C) 8%", "D) 15%"],
        "correct_answer": "B",
        "difficulty": 0.75,
        "topic": "Arithmetic",
        "tags": ["profit", "discount", "percentage"]
    },

    # ── DATA INTERPRETATION (5 questions, difficulty 0.15 → 0.9) ─────────────
    {
        "text": "A dataset has values: 4, 7, 7, 9, 13. What is the mean?",
        "options": ["A) 7", "B) 8", "C) 9", "D) 10"],
        "correct_answer": "B",
        "difficulty": 0.15,
        "topic": "Data Interpretation",
        "tags": ["mean", "statistics"]
    },
    {
        "text": "What is the median of: 3, 7, 1, 9, 4, 6, 2?",
        "options": ["A) 3", "B) 4", "C) 6", "D) 7"],
        "correct_answer": "B",
        "difficulty": 0.25,
        "topic": "Data Interpretation",
        "tags": ["median", "statistics"]
    },
    {
        "text": "In a set {3, 5, 7, 7, 9, 11}, what is the interquartile range (IQR)?",
        "options": ["A) 2", "B) 4", "C) 6", "D) 8"],
        "correct_answer": "B",
        "difficulty": 0.6,
        "topic": "Data Interpretation",
        "tags": ["IQR", "statistics"]
    },
    {
        "text": "A box plot shows Q1=20, median=35, Q3=50. A value of 80 would be considered:",
        "options": ["A) Normal", "B) Below average", "C) An outlier", "D) The maximum"],
        "correct_answer": "C",
        "difficulty": 0.8,
        "topic": "Data Interpretation",
        "tags": ["outliers", "box plot", "statistics"]
    },
    {
        "text": "A normal distribution has mean=50 and standard deviation=10. What percentage of data falls between 40 and 60?",
        "options": ["A) 50%", "B) 68%", "C) 95%", "D) 99.7%"],
        "correct_answer": "B",
        "difficulty": 0.9,
        "topic": "Data Interpretation",
        "tags": ["normal distribution", "standard deviation", "statistics"]
    },
]


def seed_questions():
    client = MongoClient(settings.mongodb_uri)
    db = client[settings.db_name]
    collection = db["questions"]

    # Clear old questions and reseed fresh
    existing = collection.count_documents({})
    if existing >= 30:
        print(f"Already have {existing} questions. Skipping seed.")
        client.close()
        return

    # If old 20-question seed exists, clear and reseed with 30
    if existing > 0:
        collection.delete_many({})
        print(f"Cleared {existing} old questions. Reseeding with 30...")

    collection.insert_many(questions)
    print(f"✅ Seeded {len(questions)} questions into MongoDB.")
    print("Topics: Algebra (7), Geometry (6), Vocabulary (7), Arithmetic (5), Data Interpretation (5)")
    client.close()


if __name__ == "__main__":
    seed_questions()