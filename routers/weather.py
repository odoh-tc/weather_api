from datetime import timezone, datetime
from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import JSONResponse
import json

from dependencies.redis_client import redis_client  # Import redis_client
from dependencies.rate_limiter import rate_limiter
from services.auth import get_current_user
from models import User
from services.weather import (
    fetch_air_pollution,
    fetch_coordinates,
    fetch_forecast,
    fetch_historical_weather,
    fetch_uv_index,
    fetch_weather
)

router = APIRouter()

@router.get("/weather/{city}", dependencies=[Depends(rate_limiter)])
async def get_weather(city: str, current_user: User = Depends(get_current_user)):

    """
    Fetch weather data for a given city.

    Parameters:
    - city (str): The name of the city for which weather data is requested.
    - current_user (User): The authenticated user making the request.

    Returns:
    - JSONResponse: A JSON response containing the weather data for the specified city.

    Raises:
    - HTTPException: If an error occurs while fetching or caching the weather data.
    """

    try:
        client = await redis_client.get_client()
        cache_key = f"weather:{city}"
        cached_data = await client.get(cache_key)
        
        if cached_data:
            return JSONResponse(content=json.loads(cached_data))

        weather_data = await fetch_weather(city)
        await client.setex(cache_key, 300, json.dumps(weather_data))  # Cache for 300 seconds
        return JSONResponse(content=weather_data)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/forecast/{city}", dependencies=[Depends(rate_limiter)])
async def get_forecast(city: str, current_user: User = Depends(get_current_user)):

    """
    Fetch forecast data for a given city.

    Parameters:
    - city (str): The name of the city for which forecast data is requested.
    - current_user (User): The authenticated user making the request.

    Returns:
    - JSONResponse: A JSON response containing the forecast data for the specified city.

    Raises:
    - HTTPException: If an error occurs while fetching or caching the forecast data.
    """

    try:
        client = await redis_client.get_client()
        cache_key = f"forecast:{city}"
        cached_data = await client.get(cache_key)
        
        if cached_data:
            return JSONResponse(content=json.loads(cached_data))

        forecast_data = await fetch_forecast(city)
        await client.setex(cache_key, 300, json.dumps(forecast_data))  # Cache for 300 seconds
        return JSONResponse(content=forecast_data)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/air_pollution/{city}", dependencies=[Depends(rate_limiter)])
async def get_air_pollution(city: str, current_user: User = Depends(get_current_user)):

    """
    Fetch air pollution data for a given city.

    Parameters:
    - city (str): The name of the city for which air pollution data is requested.
    - current_user (User): The authenticated user making the request.

    Returns:
    - JSONResponse: A JSON response containing the air pollution data for the specified city.

    Raises:
    - HTTPException: If an error occurs while fetching or caching the air pollution data.
    """
    try:
        client = await redis_client.get_client()
        cache_key = f"air_pollution:{city}"
        cached_data = await client.get(cache_key)
        
        if cached_data:
            return JSONResponse(content=json.loads(cached_data))

        air_pollution_data = await fetch_air_pollution(city)
        await client.setex(cache_key, 300, json.dumps(air_pollution_data))  # Cache for 300 seconds
        return JSONResponse(content=air_pollution_data)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/historical_weather/{city}", dependencies=[Depends(rate_limiter)])
async def get_historical_weather(city: str, date: str = Query(..., description="Date in format YYYY-MM-DD"), current_user: User = Depends(get_current_user)):

    """
    Fetch historical weather data for a given city and date.

    Parameters:
    - city (str): The name of the city for which historical weather data is requested.
    - date (str): The date for which historical weather data is requested, in format YYYY-MM-DD.
    - current_user (User): The authenticated user making the request.

    Returns:
    - JSONResponse: A JSON response containing the historical weather data for the specified city and date.

    Raises:
    - HTTPException: If an error occurs while fetching or caching the historical weather data.
    """
    try:
        timestamp = int(datetime.strptime(date, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp())
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    try:
        client = await redis_client.get_client()
        cache_key = f"historical_weather:{city}:{timestamp}"
        cached_data = await client.get(cache_key)
        
        if cached_data:
            return JSONResponse(content=json.loads(cached_data))

        historical_weather_data = await fetch_historical_weather(city, timestamp)
        await client.setex(cache_key, 300, json.dumps(historical_weather_data))  # Cache for 300 seconds
        return JSONResponse(content=historical_weather_data)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    


@router.get("/uv_index/{city}", dependencies=[Depends(rate_limiter)])
async def get_uv_index(city: str, current_user: User = Depends(get_current_user)):

    """
    Fetch UV index data for a given city.

    Parameters:
    - city (str): The name of the city for which UV index data is requested.
    - current_user (User): The authenticated user making the request.

    Returns:
    - JSONResponse: A JSON response containing the UV index data for the specified city.

    Raises:
    - HTTPException: If an error occurs while fetching or caching the UV index data.
    """
    try:
        lat, lon = await fetch_coordinates(city)
    except HTTPException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail)
    
    try:
        client = await redis_client.get_client()
        cache_key = f"uv_index:{lat}:{lon}"
        cached_data = await client.get(cache_key)
        
        if cached_data:
            return JSONResponse(content=json.loads(cached_data))

        uv_index_data = await fetch_uv_index(lat, lon)
        await client.setex(cache_key, 300, json.dumps(uv_index_data))  # Cache for 300 seconds
        return JSONResponse(content=uv_index_data)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))





@router.get("/map/{city}", dependencies=[Depends(rate_limiter)], response_class=JSONResponse)
async def get_map(city: str, current_user: User = Depends(get_current_user)):

    """
    Fetch map data for a given city.

    Parameters:
    - city (str): The name of the city for which map data is requested.
    - current_user (User): The authenticated user making the request.

    Returns:
    - JSONResponse: A JSON response containing the map data for the specified city.

    Raises:
    - HTTPException: If an error occurs while fetching or caching the map data.
    """
    try:
        client = await redis_client.get_client()
        cache_key = f"map:{city}"
        cached_data = await client.get(cache_key)
        
        if cached_data:
            return JSONResponse(content=json.loads(cached_data))

        lat, lon = await fetch_coordinates(city)
        response_data = {"city": city, "latitude": lat, "longitude": lon}

        await client.setex(cache_key, 300, json.dumps(response_data))  # Cache for 300 seconds
        return JSONResponse(content=response_data)

    except HTTPException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
