from pymongo import MongoClient
from app.config import settings

questions = [
    # --- ALGEBRA (5 questions) ---
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
        "difficulty": 0.9,
        "topic": "Algebra",
        "tags": ["quadratic", "roots", "vieta"]
    },

    # --- GEOMETRY (4 questions) ---
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

    # --- VOCABULARY (5 questions) ---
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

    # --- ARITHMETIC (3 questions) ---
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

    # --- DATA INTERPRETATION (3 questions) ---
    {
        "text": "A dataset has values: 4, 7, 7, 9, 13. What is the mean?",
        "options": ["A) 7", "B) 8", "C) 9", "D) 10"],
        "correct_answer": "B",
        "difficulty": 0.15,
        "topic": "Data Interpretation",
        "tags": ["mean", "statistics"]
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
]


def seed_questions():
    client = MongoClient(settings.mongodb_uri)
    db = client[settings.db_name]
    collection = db["questions"]

    # Avoid duplicate seeding
    if collection.count_documents({}) >= 20:
        print("✅ Questions already seeded. Skipping.")
        return

    collection.insert_many(questions)
    print(f"✅ Seeded {len(questions)} questions into MongoDB.")
    client.close()


if __name__ == "__main__":
    seed_questions()