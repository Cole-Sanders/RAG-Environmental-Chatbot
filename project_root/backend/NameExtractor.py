import re

def extract_process_info(input_file, output_file):
    with open(input_file, 'r') as infile:
        data = infile.read()

    # Split by 'Process name:' to separate each block (ignore first empty split)
    entries = data.split("Process name:")[1:]

    results = []

    for entry in entries:
        # Extract process name up to the second '|'
        parts = entry.split('|')
        if len(parts) >= 2:
            name = f"{parts[0].strip()} | {parts[1].strip()}"
        else:
            name = parts[0].strip()

        # Get location
        location_match = re.search(r"Location:\s+([A-Za-z\-]+)", entry)
        location = location_match.group(1).strip() if location_match else "Unknown"

        results.append(f"Process name: {name}. Location: {location}\n")

    # Write to output file
    with open(output_file, 'w') as outfile:
        outfile.writelines(results)

    print(f"Extracted {len(results)} processes to {output_file}")


# Run the function
extract_process_info("project_root/backend/TextData.txt", "project_root/backend/NameData.txt")
