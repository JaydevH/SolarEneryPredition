import json
from datetime import datetime
from collections import defaultdict

def process_ghi_data(input_file, output_file):
    # Read the input JSON file
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    # Dictionary to store daily GHI values
    daily_ghi = defaultdict(list)
    
    # Process each entry in the data
    for entry in data:
        # Extract the date part from period_end
        date_str = entry['period_end'].split('T')[0]
        ghi_value = entry['ghi']
        
        # Add GHI value to the corresponding date
        daily_ghi[date_str].append(ghi_value)
    
    # Calculate daily averages
    daily_averages = {
        date: sum(values) / len(values)
        for date, values in daily_ghi.items()
    }
    
    # Create output format
    output_data = [
        {
            "date": date,
            "average_ghi": avg_ghi
        }
        for date, avg_ghi in sorted(daily_averages.items())
    ]
    
    # Write to output JSON file
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=4)

# Example usage
if __name__ == "__main__":
    input_file = "mergedFile\\Srinagar_merged_data.json"  # Replace with your input file name
    output_file = "daily_ghi_Srinagar.json"  # Replace with desired output file name
    process_ghi_data(input_file, output_file)