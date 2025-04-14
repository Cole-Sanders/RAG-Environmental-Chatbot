"""
import json

# Load JSON from file
with open("project_root/backend/process_data/processes/00ca40a7-f952-3e81-aca8-97a3d71a1ffc.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Extract the @id
process_id = data["@id"]

# Extract the middle part between the two pipe symbols
name_parts = data["name"].split("|")
middle_name = name_parts[1].strip() if len(name_parts) >= 3 else None

# Find the specific exchange
target_exchange = next(
    (ex for ex in data["exchanges"] if ex["flow"]["name"] == middle_name),
    None
)

# Extract amount and unit
amount = target_exchange["amount"] if target_exchange else None
unit = target_exchange["unit"]["name"] if target_exchange else None

# Output results
print("Process ID:", process_id)
print("Middle name:", middle_name)
print("Amount:", amount)
print("Unit:", unit)

"""

import json
import os

# Load your original dataset (list of processes)
with open("project_root/backend/AllProcessData.json", "r", encoding="utf-8") as f:
    processes = json.load(f)

# Folder where the individual JSON files are stored
json_folder = "project_root/backend/process_data/processes" 

# Go through each process and update it
for process in processes:
    process_id = process.get("id")
    json_file_path = os.path.join(json_folder, f"{process_id}.json")

    # Check if the corresponding JSON file exists
    if os.path.isfile(json_file_path):
        with open(json_file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

            name_parts = data["name"].split("|")
            middle_name = name_parts[1].strip() if len(name_parts) >= 3 else None
            # Find exchange with flow name matching middle_name
            exchange = next(
                (e for e in data.get("exchanges", []) if e.get("flow", {}).get("name") == middle_name),
                None
            )

            if exchange:
                amount = exchange.get("amount")
                unit = exchange.get("flow", {}).get("refUnit")

                process["process_output"] = {
                    "Amount": amount,
                    "Unit": unit
                }
            else:
                print(f"Exchange not found in {process_id}")
    else:
        print(f"JSON file not found for {process_id}")

# Save the updated processes list back to a new JSON file
with open("updated_dataset.json", "w", encoding="utf-8") as f:
    json.dump(processes, f, indent=2)
