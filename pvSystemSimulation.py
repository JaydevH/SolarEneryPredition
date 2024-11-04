import json
from datetime import datetime
import math

# Load JSON data
with open('FILTERED JSON\\Srinagar_filtered.json', 'r') as f:
    data = json.load(f)

# Constants and parameters
panel_area = 1.7  # Area of the panel in square meters
system_efficiency = 0.18  # Base system efficiency without temperature losses
inverter_efficiency = 0.95  # Inverter efficiency (DC to AC conversion)
temperature_coefficient = -0.004  # Efficiency loss per °C above 25°C
panel_tilt = 30  # Tilt of the panel from the horizontal in degrees
panel_azimuth = 180  # Azimuth of the panel (180 degrees for south-facing)
NOCT = 45  # Nominal Operating Cell Temperature in °C (adjust as needed)

# Helper functions for solar position
def calculate_declination(day_of_year):
    # Calculate solar declination angle in radians
    return 23.45 * math.sin(math.radians(360 * (284 + day_of_year) / 365))

def calculate_hour_angle(hour, longitude):
    # Calculate the hour angle in degrees
    return (hour - 12) * 15 + longitude

def calculate_zenith(latitude, declination, hour_angle):
    # Calculate solar zenith angle in degrees
    latitude_rad = math.radians(latitude)
    declination_rad = math.radians(declination)
    hour_angle_rad = math.radians(hour_angle)
    cos_zenith = (math.sin(latitude_rad) * math.sin(declination_rad) + 
                  math.cos(latitude_rad) * math.cos(declination_rad) * math.cos(hour_angle_rad))
    return math.degrees(math.acos(cos_zenith))

def calculate_azimuth(latitude, declination, hour_angle, zenith_angle):
    # Calculate solar azimuth angle in degrees
    latitude_rad = math.radians(latitude)
    declination_rad = math.radians(declination)
    hour_angle_rad = math.radians(hour_angle)
    cos_azimuth = (math.sin(declination_rad) - math.sin(latitude_rad) * math.cos(math.radians(zenith_angle))) / (math.cos(latitude_rad) * math.sin(math.radians(zenith_angle)))
    return math.degrees(math.acos(cos_azimuth)) if hour_angle > 0 else 360 - math.degrees(math.acos(cos_azimuth))

# Process each day's data
for day in data:
    # Parse the date and time zone
    date = datetime.strptime(day["datetime"], "%Y-%m-%d")
    day_of_year = date.timetuple().tm_yday
    
    # Solar declination angle
    declination = calculate_declination(day_of_year)
    
    # Accumulate daily energy production
    daily_energy_dc_kwh = 0
    
    # Iterate over each hour of the day (simplified for hourly average)
    for hour in range(6, 18):  # Assume daylight hours from 6 AM to 6 PM
        # Calculate hour angle
        hour_angle = calculate_hour_angle(hour, day['longitude'])
        
        # Calculate zenith and azimuth
        zenith_angle = calculate_zenith(day['latitude'], declination, hour_angle)
        azimuth_angle = calculate_azimuth(day['latitude'], declination, hour_angle, zenith_angle)
        
        # Calculate angle of incidence on the panel
        incident_angle = abs(zenith_angle - panel_tilt)  # Simplified for south-facing panels
        
        # Adjust GHI based on tilt and incident angle
        ghi = day["average_ghi"]  # Assuming average GHI is for the whole day
        effective_irradiance = ghi * math.cos(math.radians(incident_angle))
        
        # Temperature-adjusted efficiency
        temp_effect = (day['temp'] - 25) * temperature_coefficient
        adjusted_efficiency = system_efficiency * (1 + temp_effect)
        
        # Hourly DC energy production (in kWh)
        hourly_dc_energy_kwh = (effective_irradiance * panel_area * adjusted_efficiency) / 1000
        daily_energy_dc_kwh += hourly_dc_energy_kwh
    
    # Convert DC energy to AC energy by applying inverter efficiency
    daily_energy_ac_kwh = daily_energy_dc_kwh * inverter_efficiency
    
    # Append the DC and AC results to the day's data
    day["simulated_solar_energy_dc_kwh"] = daily_energy_dc_kwh
    day["simulated_solar_energy_ac_kwh"] = daily_energy_ac_kwh

# Save the updated data to a new JSON file
with open('updated_weather_data_Srinagar.json', 'w') as f:
    json.dump(data, f, indent=4)
