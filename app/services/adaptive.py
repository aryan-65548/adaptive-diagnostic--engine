import math
from typing import Optional

LEARNING_RATE = 0.3
DIFFICULTY_TOLERANCE = 0.15
MIN_ABILITY = 0.0
MAX_ABILITY = 1.0


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

    # Clamp between 0.0 and 1.0
    return round(max(MIN_ABILITY, min(MAX_ABILITY, new_ability)), 4)


def get_target_difficulty(ability: float) -> float:
    """
    Target difficulty should match current ability.
    This is where IRT shines — question difficulty tracks θ.
    """
    return round(max(0.1, min(0.9, ability)), 2)


def select_best_question(ability: float, questions: list, answered_ids: list) -> Optional[dict]:
    """
    From unanswered questions, pick the one whose difficulty
    is closest to the student's current ability (target difficulty).
    """
    target = get_target_difficulty(ability)

    unanswered = [q for q in questions if str(q["_id"]) not in answered_ids]

    if not unanswered:
        return None

    # Pick question with difficulty closest to target
    best = min(unanswered, key=lambda q: abs(q["difficulty"] - target))
    return best