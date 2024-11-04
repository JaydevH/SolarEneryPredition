import json
import pandas as pd
import pvlib
from datetime import datetime
import pytz
from pathlib import Path

def calculate_solar_parameters(data_entry):
    """Calculate solar parameters for a single data entry"""
    # Create timezone aware datetime
    local_tz = pytz.FixedOffset(330)  # UTC+5:30 for India
    
    # Parse the date and time separately and combine them
    date_obj = datetime.strptime(data_entry['datetime'], '%Y-%m-%d')
    sunrise_time = datetime.strptime(data_entry['sunrise'].split('T')[1], '%H:%M:%S').time()
    datetime_obj = datetime.combine(date_obj.date(), sunrise_time)
    
    # Localize the datetime object
    datetime_obj = local_tz.localize(datetime_obj)
    
    # Convert to pandas timestamp for pvlib
    times = pd.date_range(start=datetime_obj, periods=1, freq='H')
    
    # Create location object
    location = pvlib.location.Location(
        latitude=data_entry['latitude'],
        longitude=data_entry['longitude'],
        altitude=data_entry['altitude'],
        tz=local_tz
    )
    
    # Calculate solar position
    solar_position = location.get_solarposition(times)
    
    # Calculate clear sky data
    clear_sky = location.get_clearsky(times)
    
    # Get solar position parameters
    solar_zenith = solar_position['zenith'].iloc[0]
    solar_azimuth = solar_position['azimuth'].iloc[0]
    
    # Calculate clearness index (kt) using measured GHI and extraterrestrial radiation
    dni_extra = pvlib.irradiance.get_extra_radiation(times.dayofyear[0])
    cos_zenith = pvlib.tools.cosd(solar_zenith)
    clearness = data_entry['average_ghi'] / (dni_extra * cos_zenith)
    
    # Use Erbs model to calculate DNI and DHI
    dni_dhi = pvlib.irradiance.erbs(
        data_entry['average_ghi'],
        solar_zenith,
        times.dayofyear[0]
    )
    
    # Add new calculated values to the data entry
    data_entry.update({
        'dni': float(dni_dhi['dni']),
        'dhi': float(dni_dhi['dhi']),
        'solar_zenith': float(solar_zenith),
        'solar_azimuth': float(solar_azimuth)
    })
    
    return data_entry

def process_weather_data(input_path, output_path):
    """Process weather data from input JSON file and save results to output file"""
    try:
        # Read input JSON file
        with open(input_path, 'r') as file:
            data = json.load(file)
            
        if not isinstance(data, list):
            raise ValueError("Input JSON must contain a list of weather data entries")
        
        # Process each entry
        processed_data = []
        for entry in data:
            try:
                processed_entry = calculate_solar_parameters(entry)
                processed_data.append(processed_entry)
                print(f"Successfully processed entry for {entry['datetime']}")
            except Exception as e:
                print(f"Error processing entry with datetime {entry.get('datetime', 'unknown')}: {str(e)}")
                continue
        
        # Save processed data to output file
        with open(output_path, 'w') as file:
            json.dump(processed_data, file, indent=2)
            
        print(f"\nSuccessfully processed {len(processed_data)} entries")
        print(f"Results saved to {output_path}")
        
    except Exception as e:
        print(f"Error processing file: {str(e)}")

# Example usage
if __name__ == "__main__":
    # Define input and output paths
    input_path = Path("ORIGINAL\\Srinagar 2022-01-01 to 2024-08-31.json")  # Replace with your input file path
    output_path = Path("Srinagar.json")  # Replace with desired output file path
    
    process_weather_data(input_path, output_path)