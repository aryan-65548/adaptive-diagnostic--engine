from app.services.adaptive import probability_correct, update_ability

# Test 1: equal ability and difficulty = 50% chance
p = probability_correct(0.5, 0.5)
print(f"P(correct) when θ=0.5, b=0.5: {p:.2f}")  # should be 0.50

# Test 2: high ability, low difficulty = high chance
p = probability_correct(0.8, 0.2)
print(f"P(correct) when θ=0.8, b=0.2: {p:.2f}")  # should be > 0.70

# Test 3: ability updates correctly after correct answer
new_theta = update_ability(0.5, 0.5, is_correct=True)
print(f"θ after correct answer: {new_theta}")  # should be > 0.5

# Test 4: ability drops after wrong answer
new_theta = update_ability(0.5, 0.5, is_correct=False)
print(f"θ after wrong answer: {new_theta}")  # should be < 0.5