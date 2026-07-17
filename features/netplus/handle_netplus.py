import random

from .netplusdict import netplusdict

# --- PATCH: shuffle every question's answer options ONCE at import time ---
# (previously the correct answer was "a" for 82% of questions; this fixes
# that bias without re-shuffling on every call, which caused a race condition
# where an already-posted question could get its answer key changed underneath it)
for _q in netplusdict:
    _old_correct_text = _q["answers"][_q["correctanswer"]]
    _keys = list(_q["answers"].keys())
    _values = list(_q["answers"].values())
    random.shuffle(_values)
    _q["answers"] = dict(zip(_keys, _values))
    _q["correctanswer"] = next(
        k for k, v in _q["answers"].items() if v == _old_correct_text
    )
# --- END PATCH ---

def handle_netplus(user_responses):
    # Create a list of question IDs, weighted based on user responses
    weighted_question_ids = []
    for i, question in enumerate(netplusdict):
        # Get the question ID and correct answer
        prefix = "netplus_"  # Unique prefix for CISSP questions
        question_id = prefix + str(i)
        correct_answer = question["correctanswer"].lower()

        # Compute the weight based on user responses
        weight = 1
        if question_id in user_responses:
            user_answer = user_responses[question_id].lower()
            if user_answer != correct_answer:
                weight += 1  # Increase weight for incorrect answers
            else:
                weight -= 1  # Decrease weight for correct answers

        # Add the question ID to the list with the appropriate weight
        weighted_question_ids.extend([question_id] * weight)

    # Select a random question ID from the weighted list
    question_id = random.choice(weighted_question_ids)

    # If all questions have been answered correctly, reset all the weights to 1
    if not weighted_question_ids:
        weighted_question_ids = [f"{prefix}{i}" for i in range(len(netplusdict))]

    # Retrieve the selected question
    question = netplusdict[int(question_id.split('_')[1])]
    prompt = question["question"]
    answers = question["answers"]
    correct_answer = question["correctanswer"]
    reasoning = question["reasoning"] or None

    # Format the response
    options = []
    for key, value in answers.items():
        if key != "correctanswer":
            options.append(f"**{key.upper()}**: {value}")
    options = "\n".join(options)
    response = f"**Here's a Network+ question for you**:\n\n**Question**: {prompt}\n\n**Options**: \n{options}"
    return response, question_id
