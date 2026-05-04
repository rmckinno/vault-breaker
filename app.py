import random
from datetime import date
import streamlit as st # pyright: ignore[reportMissingImports]


def generate_secret(test_mode=False):
    if test_mode:
        seed_value = 9999
    else:
        today = date.today()
        seed_value = int(today.strftime("%Y%m%d"))

    rng = random.Random(seed_value)

    first_digit = rng.choice("123456789")
    remaining_digits = rng.sample(
        [d for d in "0123456789" if d != first_digit], 3
    )
    return first_digit + "".join(remaining_digits)


def has_unique_digits(number):
    return len(set(number)) == len(number)


def evaluate_guess(secret, guess):
    result = ["⬛"] * 4
    secret_used = [False] * 4
    guess_used = [False] * 4

    for i in range(4):
        if guess[i] == secret[i]:
            result[i] = "🟩"
            secret_used[i] = True
            guess_used[i] = True

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
    return sum(abs(int(secret[i]) - int(guess[i])) for i in range(4))


def reset_game():
    st.session_state.history = []
    st.session_state.known_digits = set()
    st.session_state.eliminated_digits = set()
    st.session_state.solved = False
    st.session_state.message = ""

def build_share_text():
    today_str = date.today().strftime("%Y%m%d")

    lines = [f"Vault Breaker #{today_str}"]

    for guess, feedback, _ in st.session_state.history:
        lines.append("".join(feedback))

    if st.session_state.solved:
        lines.append(f"\nSolved in {len(st.session_state.history)}/6")
    else:
        lines.append("\nFailed")

    return "\n".join(lines)

def process_guess(secret, max_attempts):
    guess = st.session_state.guess_text.strip()

    if st.session_state.solved:
        st.session_state.message = "You already cracked today's vault."
        return

    if len(st.session_state.history) >= max_attempts:
        st.session_state.message = f"No attempts left. The vault code was {secret}."
        return

    if not guess:
        st.session_state.message = "Enter a guess."
        return

    if len(guess) != 4:
        st.session_state.message = "Must be exactly 4 digits."
        return

    if not guess.isdigit():
        st.session_state.message = "Digits only."
        return

    if guess[0] == "0":
        st.session_state.message = "Code cannot start with 0."
        return

    if not has_unique_digits(guess):
        st.session_state.message = "Digits must not repeat."
        return

    feedback = evaluate_guess(secret, guess)
    distance = calculate_distance(secret, guess)

    for i in range(4):
        digit = guess[i]
        if feedback[i] in ["🟩", "🟨"]:
            st.session_state.known_digits.add(digit)
            st.session_state.eliminated_digits.discard(digit)
        elif digit not in st.session_state.known_digits:
            st.session_state.eliminated_digits.add(digit)

    st.session_state.history.append((guess, feedback, distance))
    st.session_state.message = ""

    if guess == secret:
        st.session_state.solved = True
        st.session_state.message = "Vault cracked!"


st.title("Vault Breaker 🔐") #changed
st.write("Crack the 4-digit vault code.")

with st.expander("How to play"):
    st.write("You have 6 attempts to crack the daily vault code.")
    st.write("The code is 4 digits long.")
    st.write("The code does not start with 0.")
    st.write("Digits do not repeat.")

    st.write("Feedback:")
    st.write("🟩 Correct digit in the correct spot")
    st.write("🟨 Correct digit in the wrong spot")
    st.write("⬛ Digit is not in the code")

    st.write("Distance:")
    st.write(
        "Distance tells you how far your guess is from the real code by comparing each digit position."
    )

    st.write("Example:")
    st.code(
        """
Secret code: 5732
Your guess: 5237

Position 1: |5 - 5| = 0
Position 2: |7 - 2| = 5
Position 3: |3 - 3| = 0
Position 4: |2 - 7| = 5

Distance: 0 + 5 + 0 + 5 = 10
        """
    )

    st.write("Lower distance usually means your guess is numerically closer to the code.")

max_attempts = 6
test_mode = st.checkbox("Test mode")

if "last_test_mode" not in st.session_state:
    st.session_state.last_test_mode = test_mode

if st.session_state.last_test_mode != test_mode:
    reset_game()
    st.session_state.last_test_mode = test_mode
    st.rerun()

secret = generate_secret(test_mode=test_mode)

if "history" not in st.session_state:
    st.session_state.history = []

if "known_digits" not in st.session_state:
    st.session_state.known_digits = set()

if "eliminated_digits" not in st.session_state:
    st.session_state.eliminated_digits = set()

if "solved" not in st.session_state:
    st.session_state.solved = False

if "message" not in st.session_state:
    st.session_state.message = ""

if "guess_text" not in st.session_state:
    st.session_state.guess_text = ""

if st.button("Reset Game"):
    reset_game()
    st.rerun()

with st.form(key="guess_form"):
    st.text_input(
        f"Attempt {len(st.session_state.history) + 1}/{max_attempts} - Enter a 4-digit code:",
        key="guess_text",
    )

    st.form_submit_button(
        label="Submit",
        on_click=process_guess,
        args=(secret, max_attempts),
    )

if st.session_state.message:
    if st.session_state.solved:
        st.success(st.session_state.message)
    else:
        st.warning(st.session_state.message)

if st.session_state.history:
    st.subheader("Latest Attempts")

    for entry in reversed(st.session_state.history):
    #for entry in st.session_state.history:
        guess, feedback, distance = entry
        cols = st.columns(5)

        for i in range(4):
            
            # cols[i].markdown(
            #     f"<div style='text-align:center; font-size:24px;'>{guess[i]}<br>{feedback[i]}</div>",
            #     unsafe_allow_html=True,
            # )
            color_map = {
                "🟩": "#6aaa64",  # green
                "🟨": "#c9b458",  # yellow
                "⬛": "#787c7e",  # gray
            }

            cols[i].markdown(
                f"""
                <div style='
                    background-color:{color_map[feedback[i]]};
                    color:white;
                    text-align:center;
                    font-size:28px;
                    padding:15px;
                    border-radius:8px;
                    font-weight:bold;
                    margin:6px;
                '>
                    {guess[i]}
                </div>
                """,
                unsafe_allow_html=True,
            )

        # cols[4].markdown(
        #     f"<div style='text-align:center;font-size:24px;'>Dist<br><b>{distance}</b></div>",
        #     unsafe_allow_html=True,
        # )
        # =============DISTANCE===============
        cols[4].markdown(
            f"""
            <div style='
                background-color:#222;
                color:white;
                text-align:center;
                font-size:20px;
                padding:15px;
                border-radius:8px;
                margin:6px;
            '>
                Distance:<b>{distance}</b>
            </div>
            """,
            unsafe_allow_html=True,
        )

    known_display = (
        ", ".join(sorted(st.session_state.known_digits))
        if st.session_state.known_digits
        else "None"
    )

    eliminated_display = (
        ", ".join(sorted(st.session_state.eliminated_digits))
        if st.session_state.eliminated_digits
        else "None"
    )

    st.write(f"Known digits: {known_display}")
    st.write(f"Eliminated digits: {eliminated_display}")

if not st.session_state.solved and len(st.session_state.history) >= max_attempts:
    st.error(f"Access denied. The vault code was {secret}.")

if st.session_state.solved or len(st.session_state.history) >= 6:
    st.subheader("Share your results with friends 👇")
   
    share_text = build_share_text()

    st.text_area("Copy your results:", share_text, height=200)