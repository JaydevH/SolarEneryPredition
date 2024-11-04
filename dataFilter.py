import json

# File path of the original JSON file
input_file_path = "FINAL JSON\\Srinagar.json"  # Replace with your actual file path

# Load data from the JSON file
with open(input_file_path, "r") as infile:
    data = json.load(infile)

# Check if data is a list of dictionaries
if isinstance(data, list):
    # Loop over each entry in the list
    filtered_data_list = []
    for entry in data:
        # Extract specified fields for each entry
        filtered_entry = {
            "name": entry["name"],                     # str
            "datetime": entry["datetime"],             # str (date string)
            "tempmax": entry["tempmax"],               # float
            "tempmin": entry["tempmin"],               # float
            "temp": entry["temp"],                     # float
            "dew": entry["dew"],                       # float
            "humidity": entry["humidity"],             # float
            "precip": entry["precip"],                 # float
            "precipprob": entry["precipprob"],         # int
            "precipcover": entry["precipcover"],       # int
            "snow": entry["snow"],                     # int
            "snowdepth": entry["snowdepth"],           # int
            "windgust": entry["windgust"],             # float
            "windspeed": entry["windspeed"],           # float
            "winddir": entry["winddir"],               # float
            "sealevelpressure": entry["sealevelpressure"], # float
            "cloudcover": entry["cloudcover"],         # float
            "visibility": entry["visibility"],         # int
            "sunrise": entry["sunrise"],               # str (datetime string)
            "sunset": entry["sunset"],                 # str (datetime string)
            "average_ghi": entry["average_ghi"],       # float
            "latitude": entry["latitude"],             # float
            "longitude": entry["longitude"],           # float
            "altitude": entry["altitude"],             # float
            "dni": entry["dni"],                       # float
            "dhi": entry["dhi"],                       # float
            "solar_zenith": entry["solar_zenith"],     # float
            "solar_azimuth": entry["solar_azimuth"]    # float
        }
        filtered_data_list.append(filtered_entry)
else:
    # If it's a dictionary, proceed as usual
    filtered_data_list = [{
        "name": data["name"],
        "datetime": data["datetime"],
        "tempmax": data["tempmax"],
        "tempmin": data["tempmin"],
        "temp": data["temp"],
        "dew": data["dew"],
        "humidity": data["humidity"],
        "precip": data["precip"],
        "precipprob": data["precipprob"],
        "precipcover": data["precipcover"],
        "snow": data["snow"],
        "snowdepth": data["snowdepth"],
        "windgust": data["windgust"],
        "windspeed": data["windspeed"],
        "winddir": data["winddir"],
        "sealevelpressure": data["sealevelpressure"],
        "cloudcover": data["cloudcover"],
        "visibility": data["visibility"],
        "sunrise": data["sunrise"],
        "sunset": data["sunset"],
        "average_ghi": data["average_ghi"],
        "latitude": data["latitude"],
        "longitude": data["longitude"],
        "altitude": data["altitude"],
        "dni": data["dni"],
        "dhi": data["dhi"],
        "solar_zenith": data["solar_zenith"],
        "solar_azimuth": data["solar_azimuth"]
    }]

# Save to a new JSON file with a similar name as the original file
output_file_path = input_file_path.replace(".json", "_filtered.json")
with open(output_file_path, "w") as outfile:
    json.dump(filtered_data_list, outfile, indent=4)

print(f"Filtered data saved to {output_file_path}")
