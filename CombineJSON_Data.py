import json

def combine_and_append(weather_file, ghi_file):
    """
    Combine weather and GHI data into single objects and append to weather file
    """
    # Read the weather JSON file (first file)
    with open(weather_file, 'r') as f:
        weather_data = json.load(f)
    
    # Read the GHI JSON file (second file)
    with open(ghi_file, 'r') as f:
        ghi_data = json.load(f)
    
    # Convert lists to dictionaries keyed by date if they're not already
    if isinstance(weather_data, list):
        weather_dict = {entry['datetime']: entry for entry in weather_data}
    else:
        weather_dict = {weather_data['datetime']: weather_data}
        
    if isinstance(ghi_data, list):
        ghi_dict = {entry['date']: entry for entry in ghi_data}
    else:
        ghi_dict = {ghi_data['date']: ghi_data}
    
    # Combine matching entries
    combined_data = []
    for date, weather_entry in weather_dict.items():
        if date in ghi_dict:
            # Create a new combined entry
            combined_entry = weather_entry.copy()  # Start with weather data
            # Add GHI and location data
            ghi_entry = ghi_dict[date]
            combined_entry.update({
                'average_ghi': ghi_entry['average_ghi'],
                'latitude': ghi_entry['latitude'],
                'longitude': ghi_entry['longitude'],
                'altitude': ghi_entry['altitude']
            })
            combined_data.append(combined_entry)
    
    # Sort combined data by date
    combined_data.sort(key=lambda x: x['datetime'])
    
    # Write back to the weather file
    with open(weather_file, 'w') as f:
        json.dump(combined_data, f, indent=2)

# Example usage
if __name__ == "__main__":
    weather_file = "ORIGINAL\\Srinagar 2022-01-01 to 2024-08-31.json"  # Replace with your weather data file
    ghi_file = "DAILY GHI\\daily_ghi_Srinagar.json"         # Replace with your GHI data file
    
    try:
        combine_and_append(weather_file, ghi_file)
        print("Successfully combined and appended data")
    except FileNotFoundError as e:
        print(f"Error: Could not find file - {e}")
    except KeyError as e:
        print(f"Error: Missing required field - {e}")
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format - {e}")
    except Exception as e:
        print(f"Error: An unexpected error occurred - {e}")