import json

def format_process_entry(entry):
    parts = [
        f"Process name: {entry['name']}.",
        f"Process ID: {entry['id']}.",
        f"Location: {entry['location']}."
    ]

    for impact, data in entry["impact_results"].items():
        amount = data["Amount"]
        unit = data.get("Unit", "")
        parts.append(f"{impact} impact: {amount} {unit}".strip() + ".")

    output_amount = entry["process_output"]["Amount"]
    output_unit = entry["process_output"]["Unit"]
    parts.append(f"Process output: {output_amount} {output_unit}.")

    return " ".join(parts)

def json_to_text_file(json_data, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        for entry in json_data:
            line = format_process_entry(entry)
            f.write(line + "\n")

# Example usage
with open("project_root/backend/Data.json", "r", encoding="utf-8") as file:
    data = json.load(file)

json_to_text_file(data, "TextData.txt")
