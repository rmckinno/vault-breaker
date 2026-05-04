
# generate secret number
# random
# no 0 at start
# numbers do not repeat
import random
from datetime import date

def generate_secret():
    today = date.today()
    seed_value = int(today.strftime("%m%d%Y"))
    random.seed(seed_value)

    first_digit = random.choice("123456789")
    remaining_digits = random.sample(
        [d for d in "0123456789" if d != first_digit], 3
    )
    return first_digit + "".join(remaining_digits)
    print(today)

def has_unique_digits(number):
    return len(set(number)) == len(number)


def evaluate_guess(secret, guess):
    result = ["⬛"] * 4
    secret_used = [False] * 4
    guess_used = [False] * 4

    # First pass: correct digit, correct position
    for i in range(4):
        if guess[i] == secret[i]:
            result[i] = "🟩"
            secret_used[i] = True
            guess_used[i] = True

    # Second pass: correct digit, wrong position
    for i in range(4):
        if guess_used[i]:
            continue
        for j in range(4):
            if not secret_used[j] and guess[i] == secret[j]:
                result[i] = "🟨"
                secret_used[j] = True
                guess_used[i] = True
                break

    return result


def calculate_distance(secret, guess):
    total_distance = 0
    for i in range(4):
        total_distance += abs(int(secret[i]) - int(guess[i]))
    return total_distance


secret = generate_secret()
attempts = 6
history = []
known_digits = set()
eliminated_digits = set()

print("=== VAULT BREAKER ===")
print("Crack the 4-digit vault code.")
print("Feedback will show digit clues")
print("🟩 = correct digit in correct spot")
print("🟨 = correct digit in wrong spot")
print("⬛ = digit not in the code")
print("Distance = how far your guess is from the real code")
print("Example:")
print("Secret: 5732")
print("Guess: 5237")
print("Distance would be:")
print("|5-5| = 0")
print("|7-2| = 5")
print("|3-3| = 0")
print("|2-7| = 5")
print("total = 10")
print()

attempt = 0
solved = False

while attempt < attempts:
    guess = input(f"Attempt {attempt + 1}/{attempts} - Enter a 4-digit code: ")

    if len(guess) != 4 or not guess.isdigit():
        print("Invalid input. Enter exactly 4 digits.\n")
        continue

    if guess[0] == "0":
        print("Code cannot start with 0.\n")
        continue

    if not has_unique_digits(guess):
        print("Digits must not repeat.\n")
        continue

    feedback = evaluate_guess(secret, guess)
    distance = calculate_distance(secret, guess)

    for i in range(4):
        digit = guess[i]
        if feedback[i] in ["🟩", "🟨"]:
            known_digits.add(digit)
            if digit in eliminated_digits:
                eliminated_digits.remove(digit)
        else:
            if digit not in known_digits:
                eliminated_digits.add(digit)

    history.append((guess, feedback, distance))
    attempt += 1

    print("\n--- Guess History ---")
    for i, entry in enumerate(history, start=1):
        past_guess, past_feedback, past_distance = entry
        print(
            f"Attempt {i}: {past_guess}  {' '.join(past_feedback)}  Distance: {past_distance}"
        )

    known_display = ", ".join(sorted(known_digits)) if known_digits else "None"
    eliminated_display = (
        ", ".join(sorted(eliminated_digits)) if eliminated_digits else "None"
    )

    print(f"Known digits: {known_display}")
    print(f"Eliminated digits: {eliminated_display}")
    print()

    if guess == secret:
        print(f"Vault cracked in {attempt} tries!")
        solved = True
        break

if not solved:
    print(f"Access denied. The vault code was {secret}.")