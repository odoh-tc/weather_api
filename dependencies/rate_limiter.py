from fastapi_limiter.depends import RateLimiter

rate_limiter = RateLimiter(times=10, seconds=60)  # Example rate limiter: 10 requests per minute
