import datetime
from fastapi import HTTPException
import os
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"
AIR_POLLUTION_URL = "http://api.openweathermap.org/data/2.5/air_pollution"
HISTORICAL_WEATHER_URL = "http://api.openweathermap.org/data/2.5/onecall/timemachine"
UV_INDEX_URL = "http://api.openweathermap.org/data/2.5/uvi"
GEOCODING_URL = "http://api.openweathermap.org/geo/1.0/direct"
API_K = os.getenv("API")


def format_weather_data(data):
    dt = datetime.datetime.utcfromtimestamp(data['dt']).strftime('%Y-%m-%d %H:%M:%S')
    sunrise = datetime.datetime.utcfromtimestamp(data['sys']['sunrise']).strftime('%Y-%m-%d %H:%M:%S')
    sunset = datetime.datetime.utcfromtimestamp(data['sys']['sunset']).strftime('%Y-%m-%d %H:%M:%S')

    formatted_data = {
        "city": f"{data['name']}, {data['sys']['country']}",
        "coordinates": f"({data['coord']['lat']}, {data['coord']['lon']})",
        "temperature": f"{data['main']['temp']}°C (Feels like: {data['main']['feels_like']}°C)",
        "weather": data['weather'][0]['description'].capitalize(),
        "humidity": f"{data['main']['humidity']}%",
        "pressure": f"{data['main']['pressure']} hPa",
        "wind": f"{data['wind']['speed']} m/s at {data['wind']['deg']}°",
        "cloudiness": f"{data['clouds']['all']}%",
        "rain": f"{data.get('rain', {}).get('1h', 0)} mm in the last hour",
        "visibility": f"{data['visibility']} meters",
        "data_calculated_at": dt,
        "sunrise": sunrise,
        "sunset": sunset
    }
    return formatted_data

def format_forecast_data(data):
    forecast_list = []
    for item in data['list']:
        dt = datetime.datetime.utcfromtimestamp(item['dt']).strftime('%Y-%m-%d %H:%M:%S')
        forecast_list.append({
            "datetime": dt,
            "temperature": f"{item['main']['temp']}°C (Feels like: {item['main']['feels_like']}°C)",
            "weather": item['weather'][0]['description'].capitalize(),
            "humidity": f"{item['main']['humidity']}%",
            "pressure": f"{item['main']['pressure']} hPa",
            "wind": f"{item['wind']['speed']} m/s at {item['wind']['deg']}°",
            "cloudiness": f"{item['clouds']['all']}%",
            "rain": f"{item.get('rain', {}).get('3h', 0)} mm in the last 3 hours",
            "visibility": f"{item.get('visibility', 'N/A')} meters",
        })
    formatted_data = {
        "city": f"{data['city']['name']}, {data['city']['country']}",
        "coordinates": f"({data['city']['coord']['lat']}, {data['city']['coord']['lon']})",
        "forecast": forecast_list
    }
    return formatted_data

# def format_air_pollution_data(data):
#     return {
#         "air_quality_index": data['list'][0]['main']['aqi'],
#         "components": data['list'][0]['components']
#     }

def format_air_pollution_data(data):
    aqi = data['list'][0]['main']['aqi']
    components = data['list'][0]['components']

    # Provide more descriptive keys and explanations
    formatted_data = {
        "air_quality_index": aqi,
        "air_quality_level": aqi_description(aqi),
        "pollutant_levels": {
            "carbon_monoxide": f"{components['co']} µg/m³",
            "nitrogen_monoxide": f"{components['no']} µg/m³",
            "nitrogen_dioxide": f"{components['no2']} µg/m³",
            "ozone": f"{components['o3']} µg/m³",
            "sulfur_dioxide": f"{components['so2']} µg/m³",
            "fine_particles": f"{components['pm2_5']} µg/m³",
            "coarse_particles": f"{components['pm10']} µg/m³",
            "ammonia": f"{components['nh3']} µg/m³"
        }
    }
    return formatted_data

def aqi_description(aqi):
    """Returns a human-readable description of the AQI level."""
    if aqi == 1:
        return "Good"
    elif aqi == 2:
        return "Fair"
    elif aqi == 3:
        return "Moderate"
    elif aqi == 4:
        return "Poor"
    elif aqi == 5:
        return "Very Poor"
    else:
        return "Unknown"

def format_historical_weather_data(data):
    dt = datetime.datetime.utcfromtimestamp(data['current']['dt']).strftime('%Y-%m-%d %H:%M:%S')
    return {
        "datetime": dt,
        "temperature": f"{data['current']['temp']}°C (Feels like: {data['current']['feels_like']}°C)",
        "weather": data['current']['weather'][0]['description'].capitalize(),
        "humidity": f"{data['current']['humidity']}%",
        "pressure": f"{data['current']['pressure']} hPa",
        "wind": f"{data['current']['wind_speed']} m/s at {data['current']['wind_deg']}°",
        "cloudiness": f"{data['current']['clouds']}%",
        "rain": f"{data.get('rain', {}).get('1h', 0)} mm in the last hour",
        "visibility": f"{data['current']['visibility']} meters"
    }

def format_uv_index_data(data):
    dt = datetime.datetime.utcfromtimestamp(data['date']).strftime('%Y-%m-%d %H:%M:%S')
    return {
        "uv_index": data['value'],
        "date": dt
    }

async def fetch_weather(city: str):
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            return format_weather_data(data)
    except httpx.ConnectTimeout:
        raise HTTPException(status_code=504, detail="Connection to weather API timed out")
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {exc}")

async def fetch_forecast(city: str):
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric",
        "cnt": 5
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(FORECAST_URL, params=params)
            response.raise_for_status()
            data = response.json()
            return format_forecast_data(data)
    except httpx.ConnectTimeout:
        raise HTTPException(status_code=504, detail="Connection to weather API timed out")
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {exc}")

async def fetch_air_pollution(city: str):
    try:
        lat, lon = await fetch_coordinates(city)
    except HTTPException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail)
    
    params = {
        "lat": lat,
        "lon": lon,
        "appid": API_KEY
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(AIR_POLLUTION_URL, params=params)
            response.raise_for_status()
            data = response.json()
            return format_air_pollution_data(data)  # Ensure this function is defined in your code
    except httpx.ConnectTimeout:
        raise HTTPException(status_code=504, detail="Connection to air pollution API timed out")
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {exc}")


async def fetch_coordinates(city: str):
    params = {
        "q": city,
        "limit": 1,
        "appid": API_KEY
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(GEOCODING_URL, params=params)
            response.raise_for_status()
            data = response.json()
            if not data:
                raise HTTPException(status_code=404, detail=f"City '{city}' not found")
            return data[0]['lat'], data[0]['lon']
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {exc}")





async def fetch_uv_index(lat: float, lon: float):
    params = {
        "lat": lat,
        "lon": lon,
        "appid": API_KEY
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(UV_INDEX_URL, params=params)
            response.raise_for_status()
            data = response.json()
            return format_uv_index_data(data)
    except httpx.ConnectTimeout:
        raise HTTPException(status_code=504, detail="Connection to UV index API timed out")
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {exc}")





# Function to fetch historical weather data
async def fetch_historical_weather(city: str, timestamp: int):
    try:
        city_lat, city_lon = await fetch_coordinates(city)
    except HTTPException as exc:
        raise exc

    params = {
        "lat": city_lat,
        "lon": city_lon,
        "dt": timestamp,
        "appid": API_KEY,
        "units": "metric"
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(HISTORICAL_WEATHER_URL, params=params)
            response.raise_for_status()
            data = response.json()
            return format_historical_weather_data(data)
    except httpx.ConnectTimeout:
        raise HTTPException(status_code=504, detail="Connection to historical weather API timed out")
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {exc}")

