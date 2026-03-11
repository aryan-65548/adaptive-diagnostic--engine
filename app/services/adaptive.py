import math
from typing import Optional
from functools import lru_cache

LEARNING_RATE = 0.3
MIN_ABILITY = 0.0
MAX_ABILITY = 1.0


@lru_cache(maxsize=1024)
def probability_correct(ability: float, difficulty: float) -> float:
    """
    1PL IRT (Rasch Model)
    P(correct) = 1 / (1 + e^-(θ - b))
    θ = student ability, b = question difficulty
    """
    return 1.0 / (1.0 + math.exp(-(ability - difficulty)))


def update_ability(current_ability: float, difficulty: float, is_correct: bool) -> float:
    """
    Update θ using IRT-based gradient step.
    error = actual - expected
    θ_new = θ + learning_rate * error
    """
    actual = 1.0 if is_correct else 0.0
    expected = probability_correct(current_ability, difficulty)
    error = actual - expected
    new_ability = current_ability + LEARNING_RATE * error
    return round(max(MIN_ABILITY, min(MAX_ABILITY, new_ability)), 4)


def get_ability_label(ability: float) -> str:
    if ability < 0.35:
        return "Beginner"
    elif ability < 0.65:
        return "Intermediate"
    else:
        return "Advanced"


def select_best_question(ability: float, questions: list, answered_ids: list) -> Optional[dict]:
    # normalize answered_ids — strip whitespace, ensure plain strings
    answered_set = {str(qid).strip() for qid in answered_ids}

    # filter out already answered questions
    unanswered = [
        q for q in questions
        if str(q["_id"]).strip() not in answered_set
    ]
    if not unanswered:
        return None

    # clamp target difficulty between 0.1 and 0.9
    target = round(max(0.1, min(0.9, ability)), 2)

    # pick question with difficulty closest to current ability
    best = min(unanswered, key=lambda q: abs(q["difficulty"] - target))
    return best