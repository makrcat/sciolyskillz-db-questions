import re
import os
import json

input_folder = "contestFiles"
output_file = "algolify.json"

algolia_records = []

# for each file
for filename in os.listdir(input_folder):
    
    # Yes
    if filename.endswith(".json"):
        
        # oh cool this exists
        filepath = os.path.join(input_folder, filename)
        
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            
            competition = data.get("competition")
            division = data.get("division")
            year = data.get("year")
            
            event = data.get("event")
            
            questions = data.get("questions")
            
            for q in questions:
                sourceInfo = q.get("sourceInfo")
                searchInfo = q.get("searchInfo")
                questionInfo = q.get("questionInfo")
                
                question_id = q.get("id")

                record = {
                    "id": question_id,
                    "competition": competition,
                    "division": division,
                    "year": year,
                    "event": event,
                    
                    "question": questionInfo.get("question"),
                    "potentialAnswers": questionInfo.get("potentialAnswers"),
                    "correctAnswerIndex": questionInfo.get("correctAnswerIndex"),
                    "explanation": questionInfo.get("explanation"),

                    "system": searchInfo.get("system"),
                    "tags": [tag for tag in searchInfo.get("tags") if tag],  # remove nulls

                    "page": sourceInfo.get("page"),
                    "number": sourceInfo.get("number"),
                }

                algolia_records.append(record)

# Write the resulting list to algolify.json
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(algolia_records, f, indent=2)
