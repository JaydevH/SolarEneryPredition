import pvlib
import pandas as pd
import json
from datetime import datetime, timedelta
import numpy as np
from timezonefinder import TimezoneFinder
import os

def parse_time_from_iso(time_str):
    """Parse hour from ISO format time string"""
    try:
        return pd.to_datetime(time_str).hour
    except:
        return None

def interpolate_weather_data(data, timestamps):
    """
    Interpolate weather data for each hour of the day based on min/max values.
    Returns hourly weather parameters.
    """
    # Create hourly temperature using min/max
    try:
        temp_max = float(data.get('tempmax', data.get('temp', 25)))
        temp_min = float(data.get('tempmin', data.get('temp', 15)))
    except (ValueError, TypeError):
        temp_max = 25
        temp_min = 15
    
    # Simple sinusoidal temperature model
    hour_temps = [temp_min + (temp_max - temp_min) * 
                 np.sin(np.pi * (h - 6) / 24) if 6 <= h <= 18 
                 else temp_min for h in range(24)]
    
    # Parse sunrise and sunset times
    try:
        sunrise_hour = parse_time_from_iso(data.get('sunrise'))
        sunset_hour = parse_time_from_iso(data.get('sunset'))
        
        if sunrise_hour is None or sunset_hour is None:
            print("Warning: Could not parse sunrise/sunset times. Using default values.")
            sunrise_hour, sunset_hour = 6, 18
    except:
        print("Warning: Could not parse sunrise/sunset times. Using default values.")
        sunrise_hour, sunset_hour = 6, 18
    
    day_length = max(1, sunset_hour - sunrise_hour)  # Ensure non-zero day length
    
    # Calculate clear sky GHI for each hour
    weather_data = []
    
    for timestamp in timestamps:
        hour = timestamp.hour
        
        # Is it daytime?
        is_daytime = sunrise_hour <= hour <= sunset_hour
        
        if is_daytime:
            try:
                # Use provided GHI and cloud cover
                cloud_cover = float(data.get('cloudcover', 0))
                cloud_factor = 1 - (cloud_cover / 100)
                relative_hour = (hour - sunrise_hour) / day_length
                
                # Use provided solarradiation if available, otherwise use average_ghi
                ghi = float(data.get('solarradiation', data.get('average_ghi', 1000))) * np.sin(np.pi * relative_hour)
                
                # Use provided DNI and DHI if available
                dni = float(data.get('dni', ghi * cloud_factor))
                dhi = float(data.get('dhi', ghi * (1 - cloud_factor)))
                
            except (ValueError, TypeError):
                ghi, dni, dhi = 0, 0, 0
        else:
            ghi, dni, dhi = 0, 0, 0
        
        try:
            wind_speed = float(data.get('windspeed', 0))
        except (ValueError, TypeError):
            wind_speed = 0
            
        weather_data.append({
            'ghi': float(ghi),
            'dni': float(dni),
            'dhi': float(dhi),
            'temp_air': float(hour_temps[hour]),
            'wind_speed': wind_speed
        })
    
    return pd.DataFrame(weather_data, index=timestamps)

def simulate_pv_system(json_path):
    """
    Simulate PV system using data from a JSON file and append results.
    """
    # Read JSON file
    try:
        with open(json_path, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        raise FileNotFoundError(f"Could not find JSON file at: {json_path}")
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON format in file: {json_path}")
    
    # Ensure required fields are present and convert to float
    try:
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
    except (KeyError, ValueError, TypeError):
        raise ValueError("Invalid or missing latitude/longitude in JSON file")
    
    # Get timezone based on coordinates
    tf = TimezoneFinder()
    tz = tf.timezone_at(lat=latitude, lng=longitude)
    if not tz:
        print(f"Warning: Could not determine timezone for coordinates {latitude}, {longitude}. Using UTC.")
        tz = 'UTC'
    
    # Create timestamp range for the entire day (hourly)
    try:
        # Handle the specific date format in your JSON
        date = pd.to_datetime(data['datetime'])
    except (KeyError, ValueError, TypeError):
        print("Warning: Could not parse datetime. Using current date.")
        date = pd.Timestamp.now()
    
    timestamps = pd.date_range(
        start=date.replace(hour=0, minute=0, second=0),
        periods=24,
        freq='H',
        tz=tz
    )
    
    # Location parameters
    try:
        altitude = float(data.get('altitude', 0))
    except (ValueError, TypeError):
        altitude = 0
        
    location = pvlib.location.Location(
        latitude,
        longitude,
        tz=tz,
        altitude=altitude
    )
    
    # Get weather data for each hour
    weather_data = interpolate_weather_data(data, timestamps)
    
    # System Parameters
    system_config = {
        'surface_tilt': 20,
        'surface_azimuth': 180,
        'module_parameters': {
            'pdc0': 280,
            'gamma_pdc': -0.004
        },
        'inverter_parameters': {
            'pdc0': 3000,
            'eta_inv_nom': 0.96
        },
        'strings_per_inverter': 10,
        'modules_per_string': 10
    }
    
    # Create PV system
    system = pvlib.pvsystem.PVSystem(
        surface_tilt=system_config['surface_tilt'],
        surface_azimuth=system_config['surface_azimuth'],
        module_parameters=system_config['module_parameters'],
        inverter_parameters=system_config['inverter_parameters'],
        strings_per_inverter=system_config['strings_per_inverter'],
        modules_per_string=system_config['modules_per_string']
    )
    
    try:
        # Calculate solar position
        solar_position = location.get_solarposition(times=weather_data.index)
        
        # Calculate plane of array irradiance
        poa_irradiance = pvlib.irradiance.get_total_irradiance(
            surface_tilt=system_config['surface_tilt'],
            surface_azimuth=system_config['surface_azimuth'],
            dni=weather_data['dni'],
            ghi=weather_data['ghi'],
            dhi=weather_data['dhi'],
            solar_zenith=solar_position['apparent_zenith'],
            solar_azimuth=solar_position['azimuth']
        )
        
        # Calculate cell temperature
        cell_temperature = pvlib.temperature.sapm_cell(
            poa_global=poa_irradiance['poa_global'],
            temp_air=weather_data['temp_air'],
            wind_speed=weather_data['wind_speed']
        )
        
        # Calculate DC power
        dc_power = system.pvwatts_dc(
            g_poa_effective=poa_irradiance['poa_global'],
            temp_cell=cell_temperature
        )
        
        # Calculate AC power
        ac_power = system.pvwatts_ac(dc_power)
        
        # Calculate daily energy
        daily_energy_dc = float(dc_power.sum() / 1000)  # Convert to kWh
        daily_energy_ac = float(ac_power.sum() / 1000)  # Convert to kWh
        
        # Create hourly generation profile
        hourly_generation = []
        for i in range(len(dc_power)):
            hourly_generation.append({
                'hour': i,
                'dc_power': float(dc_power.iloc[i]),
                'ac_power': float(ac_power.iloc[i])
            })
        
        # Add simulation results to the original data
        data['pv_simulation'] = {
            'daily_energy_dc_kwh': daily_energy_dc,
            'daily_energy_ac_kwh': daily_energy_ac,
            'peak_dc_power_w': float(dc_power.max()),
            'peak_ac_power_w': float(ac_power.max()),
            'system_efficiency': float(daily_energy_ac / daily_energy_dc * 100 if daily_energy_dc > 0 else 0),
            'hourly_generation': hourly_generation,
            'timezone': tz,
            'system_config': system_config
        }
        
        # Save updated data back to the JSON file
        output_path = os.path.splitext(json_path)[0] + '_with_pv.json'
        with open(output_path, 'w') as file:
            json.dump(data, file, indent=2)
        
        return output_path
        
    except Exception as e:
        raise Exception(f"Error during PV simulation: {str(e)}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Simulate PV system from weather data JSON file')
    parser.add_argument('json_path', help='Path to the input JSON file')
    
    args = parser.parse_args()
    
    try:
        output_path = simulate_pv_system(args.json_path)
        print(f"Simulation completed successfully. Results saved to: {output_path}")
    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)