import json

def append_location_data(source_file, target_file):
    """
    Extract location data from source file and append it to the target file's list items
    """
    # Read the source JSON file containing location data
    with open(source_file, 'r') as f:
        source_data = json.load(f)
    
    # Extract location data from first item in source if it's a list
    if isinstance(source_data, list):
        location_data = {
            'latitude': source_data[0]['latitude'],
            'longitude': source_data[0]['longitude'],
            'altitude': source_data[0]['altitude']
        }
    else:
        location_data = {
            'latitude': source_data['latitude'],
            'longitude': source_data['longitude'],
            'altitude': source_data['altitude']
        }
    
    # Read the target JSON file
    with open(target_file, 'r') as f:
        target_data = json.load(f)
    
    # Make sure target_data is a list
    if not isinstance(target_data, list):
        raise ValueError("Target file must contain a JSON array/list")
    
    # Add location data to each item in the target list
    for item in target_data:
        if isinstance(item, dict):
            item.update(location_data)
    
    # Write the updated data back to the target file
    with open(target_file, 'w') as f:
        json.dump(target_data, f, indent=4)

# Example usage
if __name__ == "__main__":
    source_file = "HOURLY GHI\\Srinagar_merged_data.json"  # Replace with your source file name
    target_file = "DAILY GHI\\daily_ghi_Srinagar.json"  # Replace with your target file name
    try:
        append_location_data(source_file, target_file)
        print(f"Successfully updated {target_file} with location data from {source_file}")
    except FileNotFoundError as e:
        print(f"Error: Could not find file - {e}")
    except KeyError as e:
        print(f"Error: Missing required location field - {e}")
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format - {e}")
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error: An unexpected error occurred - {e}")