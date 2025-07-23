import os
import json
import uuid

input_folder = "contestFiles" 
uuid_file = "uuids.txt"

# load the
existing_uuids = set()
if os.path.exists(uuid_file):
    with open(uuid_file, "r") as f:
        for line in f:
            existing_uuids.add(line.strip())

# Just check if it's already somehow used in the astronomically small chance
def generate_unique_uuid():
    while True:
        new_id = str(uuid.uuid4())
        if new_id not in existing_uuids:
            return new_id

# go through contestFiles
for filename in os.listdir(input_folder):
    if filename.endswith(".json"):
        
        # for each file
        filepath = os.path.join(input_folder, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)


        questions = data.get("questions", [])
        
        changed = False

        for q in questions:
            
            # if ID empty (as it is)
            if not q.get("id"):
                # make a uuid
                new_id = generate_unique_uuid()
                q["id"] = new_id
                existing_uuids.add(new_id)
                changed = True

        
        # update the file (after the entire file is changed)
        if changed:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

# update the uuid file as well
with open(uuid_file, "w") as f:
    for u in sorted(existing_uuids):
        f.write(u + "\n")

print(f"UUID assignment complete. {len(existing_uuids)} UUIDs tracked in '{uuid_file}'.")