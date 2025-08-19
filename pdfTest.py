import requests
import fitz as PyMuPDF
import io
import re
import json
import os

def flatten(s):
    s = s.lower().strip()
    s = re.sub(r'[^a-z0-9]+', '_', s)
    return s

# thank you gpt
def cleanQ(text):
   # Remove any parentheses with content at the start + following space
    text = re.sub(r'^\(.*?\)\s+', '', text)
    # Remove any other parentheses with content anywhere else
    text = re.sub(r'\(.*?\)', '', text)
    return text.strip()

def download_drive_pdf(file_id):
    download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
    response = requests.get(download_url)
    if response.status_code == 200:
        return io.BytesIO(response.content)
    else:
        raise Exception(f"Failed to download PDF (status {response.status_code})")

def extract_drive_id(url):
    match = re.search(r"(?:/d/|id=)([a-zA-Z0-9_-]{10,})", url)
    if match:
        return match.group(1)
    else:
        return None
            
            
links = {
    "2023 Northview Invitational C":"https://drive.google.com/file/d/1OL2gJgh84i2vfGKhEqw4mMfmfPreYY9C/view",
    "2024 University of Massachusetts Amherst C":"https://drive.google.com/file/d/1NrRz89hACvK4M-WfucZ-tcoGIf_zFvhP/view",
    "2024 University of Pennsylvania (SOUP) Invitational C":"https://drive.google.com/file/d/185gEh1ADRqhIFYt7KCptm2Y9SE35QVK0/view",
    "2024 Golden Gate (GGSO) Invitational C":"https://drive.google.com/file/d/1J6qVsnVfKAEGNGamfX4Nbt_h9zxL_2e2/view",
    "2024 Seven Lakes Invitational C":"https://drive.google.com/file/d/1JFGywF9TI177FlprawfVmOHh3rnAw38T/view",
    "2024 Georgia Tech (Yellow Jacket) Invitational C":"https://drive.google.com/file/d/11n1Opib93ftsXPVIpl2T_YC9agS8tBO4/view",
    "2024 Stanford Invitational C":"https://drive.google.com/file/d/1LZJj86RzJt3nYjEgNw1Ax3xe98t3UF29/view",
    
    "2024 Mason Satellite Invitational C":"https://drive.google.com/file/d/1KWj_8P3ICJJqLnXVOGBoiZJaVj1QEaje/view",
    "2025 Purdue University Invitational C":"https://drive.google.com/file/d/1o4EisWrlrx4zSGBLgA0YJAvV3uHTUEvM/view",
    "2025 Rickards Invitational C":"https://drive.google.com/file/d/1fvU66rNa6V3nt0ZXp5ADjOD4VIqZszfj/view",
    "2025 UCR Highlander Invitational C":"https://drive.google.com/file/d/1w1XQZyrNpP1DlhTWBFl_2n2bM9COxy_A/view",
    "2025 USC Invitational C":"https://drive.google.com/file/d/1MUF5A4ngLG8LgvxP_RNThfAb161UASqp/view",
    
    
    # that one was a google doc
    "2024 Brown Invitational C":"https://drive.google.com/file/d/1iFfaE6tbYKRM7LK_R-5AV-G5bvyL5LAL/view?usp=drive_link",
    
}


    
def doTheThingLol(drivelink, outputfile, name, event):
    pdf_bytes = download_drive_pdf(extract_drive_id(drivelink))
    doc = PyMuPDF.open(stream=pdf_bytes, filetype="pdf")

    lines = []

    for page in doc:
        text_dict = page.get_text("dict")
        for block in text_dict["blocks"]:
            if "lines" in block:
                for line in block["lines"]:
                    line_text = " ".join([span["text"] for span in line["spans"]])
                    if line_text.strip():
                        lines.append(line_text.strip())

    year = int(name[:4])
    tourn_name = name[5:-2]
    division = name[-1:]

    # text blob
    textblob = "\n".join(lines)

    # split by the 1. 2. 3. digits
    chunks = re.split(r"\n(?=\d+\.\s)", textblob)  
    # splits before lines like "1. blehblehbleh"
    questions = []

    for chunk in chunks:
        chunk = chunk.strip()
        # skip if chunk does not start with question number
        if not re.match(r"^\d+\.", chunk):
            continue

        # find where the first answer starts (a. b. c. d.)
                # find where the first answer starts (a. b. c. d.)
        answer_start_match = re.search(r"\n[abcd][\.\)]", chunk, re.IGNORECASE)
        if answer_start_match:
            question_text = chunk[:answer_start_match.start()].strip().replace('\n', ' ')
            answers_part = chunk[answer_start_match.start():].strip()
        else:
            # no answers found. skip
            continue


        question_text = re.sub(r'^[a-d][\.\)]\s+[a-d][\.\)]\s+', '', question_text, flags=re.IGNORECASE)
        
        # parse answers by matching each answer label + text
        answer_pattern = re.compile(
            r"([a-d][\.\)])\s*(.*?)(?=(\n[a-d][\.\)]\s)|\Z)",
            re.IGNORECASE | re.DOTALL
        )
        answer_choices = []
        for m in answer_pattern.finditer(answers_part):
            answer_text = m.group(2).replace('\n', ' ').strip()

            # FIX for "Page ..." junk in answers 
            answer_text = re.split(r"\b[Pp]age\b", answer_text, maxsplit=1)[0].strip()

            if answer_text:  # keep only if not empty
                answer_choices.append(answer_text)


        # correct_index = None  
        # it's too hard, every test is different. I'll probably feed it into an AI to find the correct answers.

        # only add questions with at least 4 answers
        if len(answer_choices) >= 4:

            # question_text = "12. What is the main function of the heart?"
            match = re.match(r"^(\d+)", question_text)
            qnum = None
            if match:
                qnum = int(match.group(1))
            else:
                qnum = None

            qtext = re.sub(r"^\d+\.\s*", "", question_text)
            qtext = cleanQ(qtext).strip()

            questions.append({
                "id": None,
                "questionInfo": {
                    "question": qtext,
                    "correctAnswerIndex": None,
                    "potentialAnswers": answer_choices,
                    "explanation": None,
                },
                "searchInfo": {
                    "reference": None,
                    "system": None,
                    "event": event,
                    "tags": [None]
                },
                "sourceInfo": {
                    "page": page.number + 1,
                    "number": qnum
                }
            })

    # wrap questions with test metadata at the top
    output = {
        "competition": tourn_name,
        "division": division,
        "year": year,
        "event": event,
        "questions": questions
    }

    with open(outputfile, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"✅ Parsed {len(questions)} questions")

output_dir = "contestFiles"

for name in links.keys():
    drivelink = links[name]
    filename = flatten(name) + ".json"
    output_path = os.path.join(output_dir, filename) 

    if os.path.exists(output_path):
        print(f"Skipping {filename}, already exists in {output_dir}")
        continue
    else:
        doTheThingLol(drivelink, output_path, name, "anatomy")

    