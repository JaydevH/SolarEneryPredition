import json
import glob

# Path to JSON files
file_paths = glob.glob("SIMULATION\\*.json")

combined_data = []

# Load each JSON file and append the data
for file_path in file_paths:
    with open(file_path, 'r') as file:
        data = json.load(file)
        combined_data.append(data)

# Save combined data to a new JSON file
with open("combined_output.json", 'w') as output_file:
    json.dump(combined_data, output_file, indent=4)

print("JSON files combined successfully!")
