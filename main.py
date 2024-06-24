from fastapi import FastAPI
from routers.weather import router as weather_router
from routers.auth import router as auth_router
from dependencies.redis_client import redis_client
from fastapi_limiter import FastAPILimiter
app = FastAPI(
    title="Weather API",
    description="This FastAPI application provides comprehensive weather data services, including current weather conditions, forecasts, air pollution metrics, historical weather data, UV index information, and geographical mapping. The application features authentication and authorization using SQLite, employs caching mechanisms with Redis to enhance performance, and implements rate limiting to manage API request rates effectively.",
    version="1.0.0",
)

# Include routers
app.include_router(weather_router, prefix="/api", tags=["weather"])
app.include_router(auth_router, tags=["auth"])



@app.get("/")
def read_root():
    return {"message": "Welcome to the Weather API"}



# Initialize Redis client during startup
@app.on_event("startup")
async def startup_event():
    try:
        await redis_client.init()
        await FastAPILimiter.init(redis=redis_client.redis_client)  # Initialize FastAPILimiter with redis client
    except Exception as e:
        print(f"Error initializing Redis or FastAPILimiter: {e}")
        raise

# Handle cleanup during shutdown
@app.on_event("shutdown")
async def shutdown_event():
    if redis_client.redis_client:
        await redis_client.redis_client.close()
