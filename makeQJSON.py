import re

def flatten(text):
    return re.sub(r'\W+', '_', text.strip().lower()).strip('_')

def makeQ(
    question_text,
    answer_choices,
    correct_index,
    explanation,
    topic,
    tags,
    reference,
    competition,
    division,
    page,
    year,
    q_index
):
    competition_slug = flatten(competition)
    q_id = f"{year}_{competition_slug}_p{page}_q{q_index}"

    return {
        "id": q_id,
        "questionInfo": {
            "question": question_text,
            "correctAnswerIndex": correct_index,
            "potentialAnswers": answer_choices,
            "explanation": explanation
        },
        "searchInfo": {
            "reference": reference,
            "topic": topic,
            "tags": tags
        },
        "sourceInfo": {
            "competition": competition,
            "division": division,
            "page": page,
            "year": year
        }
    }
