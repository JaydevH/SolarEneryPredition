import json
from pathlib import Path

def count_json_entries(file_path):
    """
    Count entries in a JSON file. Works with both JSON arrays and objects.
    
    Args:
        file_path (str): Path to the JSON file
        
    Returns:
        int: Number of entries
        str: Structure type ('array', 'object', or 'value')
    """
    try:
        # Read the JSON file
        with open(file_path, 'r') as file:
            data = json.load(file)
        
        # Check the type of JSON structure
        if isinstance(data, list):
            return len(data), 'array'
        elif isinstance(data, dict):
            return len(data.keys()), 'object'
        else:
            return 1, 'value'
            
    except json.JSONDecodeError:
        print(f"Error: {file_path} is not a valid JSON file")
        return 0, 'invalid'
    except FileNotFoundError:
        print(f"Error: File {file_path} not found")
        return 0, 'not found'
    except Exception as e:
        print(f"Error: An unexpected error occurred: {str(e)}")
        return 0, 'error'

def main():
    # Get the file path
    file_path = Path("ORIGINAL\\madrid 2022-01-01 to 2024-08-31.json")
    
    # Count entries
    count, structure_type = count_json_entries(file_path)
    
    # Print results
    if count > 0:
        print(f"\nFile structure: {structure_type}")
        if structure_type == 'array':
            print(f"Number of array elements: {count}")
        elif structure_type == 'object':
            print(f"Number of key-value pairs: {count}")
        else:
            print("File contains a single value")
    
if __name__ == "__main__":
    main()