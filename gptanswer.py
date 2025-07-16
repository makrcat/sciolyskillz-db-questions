import json
import re
from dotenv import load_dotenv
from pathlib import Path
import os
from openai import OpenAI

load_dotenv(dotenv_path=Path("OPENAI_API_KEY.env"))
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_MAP = {
    2026: ["Nervous", "Sense Organs", "Endocrine"],
    2025: ["Skeletal", "Muscular", "Integumentary"],
    2024: ["Cardiovascular", "Lymphatic", "Excretory"],
    2023: ["Respiratory", "Digestive", "Immune"],
    2022: ["Nervous", "Sense Organs", "Endocrine"],
    2021: ["Skeletal", "Muscular", "Integumentary"],
    2020: ["Skeletal", "Muscular", "Integumentary"],
    2019: ["Cardiovascular", "Lymphatic", "Excretory"],
    2018: ["Respiratory", "Digestive", "Immune"],
    2017: ["Nervous", "Sense Organs", "Endocrine"],
    2016: ["Skeletal", "Muscular", "Integumentary"],
    2015: ["Cardiovascular", "Integumentary", "Immune"],
    2014: ["Integumentary", "Nervous", "Immune"],
    2013: ["Nervous", "Digestive", "Excretory"],
    2012: ["Digestive", "Respiratory", "Excretory"],
    2011: ["Respiratory", "Muscular", "Endocrine"],
    2010: ["Muscular", "Skeletal", "Endocrine"],
    2009: ["Skeletal", "Circulatory"],
    2008: ["Circulatory", "Nervous"],
}

def getQ(question_obj, system_choices):
    question = question_obj["questionInfo"]["question"]
    options = question_obj["questionInfo"].get("potentialAnswers", [])

    prompt = f"""
Question: {question}

Options:
{chr(10).join([f"{i}: {opt}" for i, opt in enumerate(options)])}

Pls respond with ONLY THESE 3 LINES:

The index of the correct answers. ex. 0, or 01 if multiple. If you don't know or it's free-response, respond with 'NA'.

The body system this question relates to from this list: {', '.join(system_choices)}. If unknown, respond with 'Unknown'.

A brief explanation for the answers. 
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=150,
        temperature=0,
    )

    answer_text = response.choices[0].message.content.strip()
    print("-----")
    print(answer_text)
    print("-----")

    lines = answer_text.splitlines()
    if len(lines) < 3:
        raise ValueError(f"Expected 3 lines in response but got {len(lines)}: {answer_text}")

    answer_str = lines[0].strip()
    system = lines[1].strip()
    explanation = lines[2].strip()

    if answer_str.upper() == "NA":
        unique_indices = []
    else:
        digits = re.findall(r"\d", answer_str)
        unique_indices = sorted(set(int(d) for d in digits))

    if system not in system_choices:
        system = "Unknown"

    return unique_indices, system, explanation


def genAnswers(filename):
    with open(filename, "r") as f:
        data = json.load(f)

    year = data["year"]
    system_choices = SYSTEM_MAP[year]

    modified = False

    for q in data["questions"]:
        answer_choices = q["questionInfo"].get("potentialAnswers", [])
        already_answered = q["questionInfo"].get("correctAnswerIndex")
        explanation_present = bool(q["questionInfo"].get("explanation"))
        
        # has system already?
        system_present = q.get("searchInfo").get("system") not in [None, "", "Unknown"]

        skip_toolong = any(len(a) > 250 for a in answer_choices)
        skip_invalid = any(re.search(r"\b(pts?|points?|credit)\b", a, re.IGNORECASE) for a in answer_choices)

        if skip_toolong or skip_invalid:
            print(f"⛔ Skipped (looks like FRQ): {q['questionInfo']['question']}\n")
            continue


        # If missing answer OR missing explanation OR missing system => call API
        needs_answer = not already_answered
        needs_explanation = not explanation_present
        needs_system = not system_present

        if not (needs_answer or needs_explanation or needs_system):
            print(f"⏩ Skipped (all data present): {q['questionInfo']['question']}")
            continue

        try:
            indices, system, explanation = getQ(q, system_choices)

            if needs_answer and indices:
                q["questionInfo"]["correctAnswerIndex"] = indices

            if needs_explanation and explanation:
                q["questionInfo"]["explanation"] = explanation

            if needs_system and system and system != "Unknown":
                q["searchInfo"]["system"] = system

            print(f"✅ Updated: {q['questionInfo']['question']}")
            print(f"Answer indices: {indices}")
            print(f"System: {system}")
            print(f"Explanation: {explanation[:80]}...\n")  # print start of explanation

            modified = True

            with open(filename, "w") as f_out:
                json.dump(data, f_out, indent=2)

        except Exception as e:
            print(f"❌ Error for question: {q['questionInfo']['question']}\n{e}\n")

    if not modified:
        print("✅ No changes made. All were already filled, or skipped")


folder = "contestFiles"
for filename in os.listdir(folder):
    full_path = os.path.join(folder, filename)
    if os.path.isfile(full_path):
        genAnswers(full_path)
