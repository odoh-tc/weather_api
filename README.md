# Weather API

## Overview

This FastAPI application provides comprehensive weather data services, including current weather conditions, forecasts, air pollution metrics, historical weather data, UV index information, and geographical mapping. The application features authentication and authorization using SQLite, employs caching mechanisms with Redis to enhance performance, and implements rate limiting to manage API request rates effectively.

## Features

- **Weather Data**: Current weather, forecasts, air pollution metrics, historical weather data, UV index information, and geographical mapping.
- **Caching**: Utilizes Redis for caching responses, ensuring efficient handling of repeated requests.
- **Rate Limiting**: Implements rate limiting to control API request rates effectively, preventing abuse and ensuring fair usage.
- **Authentication**: Allows user registration and login to access protected API endpoints.
- **Authorization**: Ensures security with protected routes that require authentication.

## Requirements

- Python
- FastAPI
- SQLAlchemy
- SQLite
- Redis
- Pydantic
- Uvicorn
- Passlib
- Python-Jose

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/weather_api.git
cd weather_api
```

### 2. Create a virtual environment

```bash
pip install -r requirements.txt

```

### 3. Install dependencies

```bash
git clone https://github.com/yourusername/weather_api.git
cd weather_api
```

### 4. Run the application

```bash
uvicorn main:app --reload
```

### 5. Docker setup (optional)

Build and run the application using Docker:

```bash
docker-compose up --build
```
