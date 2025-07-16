import requests
import fitz as PyMuPDF
import io
import re
import json

def download_drive_pdf(file_id):
    download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
    response = requests.get(download_url)
    if response.status_code == 200:
        return io.BytesIO(response.content)
    else:
        raise Exception(f"Failed to download PDF (status {response.status_code})")


pdf_bytes = download_drive_pdf("1OL2gJgh84i2vfGKhEqw4mMfmfPreYY9C")
doc = PyMuPDF.open(stream=pdf_bytes, filetype="pdf")

'''
for page in doc:
    print("BLOCK ------------------")
    text_dict = page.get_text("dict")
    for block in text_dict["blocks"]:
        if "lines" in block:
            for line in block["lines"]:
                line_text = " ".join([span["text"] for span in line["spans"]])
                print(line_text)
        print("---------------------")
    break'''
    

lines = []

for page in doc:
    text_dict = page.get_text("dict")
    for block in text_dict["blocks"]:
        if "lines" in block:
            for line in block["lines"]:
                line_text = " ".join([span["text"] for span in line["spans"]])
                if line_text.strip():
                    lines.append(line_text.strip())

# text blob
textblob = "\n".join(lines)

# split by the 1. 2. 3. digits
chunks = re.split(r"\n(?=\d+\.\s)", textblob)  
# splits before lines like "1. blehblehbleh"
questions = []

import re

for chunk in chunks:
    chunk = chunk.strip()
    # skip if chunk does not start with question number
    if not re.match(r"^\d+\.", chunk):
        continue

    # find where the first answer starts (a. b. c. d.)
    answer_start_match = re.search(r"\n[a-d]\.", chunk, re.IGNORECASE)
    if answer_start_match:
        question_text = chunk[:answer_start_match.start()].strip().replace('\n', ' ')
        answers_part = chunk[answer_start_match.start():].strip()
    else:
        # no answers found. skip
        
        continue

    # parse answers by matching each answer label + text
    answer_pattern = re.compile(r"([a-d]\.)\s*(.*?)(?=(\n[a-d]\.)|\Z)", re.IGNORECASE | re.DOTALL)
    answer_choices = []
    for m in answer_pattern.finditer(answers_part):
        answer_text = m.group(2).replace('\n', ' ').strip()
        answer_choices.append(answer_text)

    correct_index = None  
    # it's too hard, every test is different. I'll probably feed it into an AI to find the correct answers.

    # only add questions with at least 4 answers
    if len(answer_choices) >= 4:
        questions.append({
            "question": question_text,
            "answers": answer_choices,
            "correctAnswerIndex": correct_index
        })


import json
with open("parsed_questions.json", "w", encoding="utf-8") as f:
    json.dump(questions, f, indent=2, ensure_ascii=False)

print(f"✅ Parsed {len(questions)} questions")
