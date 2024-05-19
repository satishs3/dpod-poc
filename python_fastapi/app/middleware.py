import time
from fastapi import Request
from logger import logger

async def log_requests(request: Request, call_next):
    start_time = time.time()
    print(f"Request: {request.method} {request.url}")
    logger.info(f"Request: {request.method} {request.url}")
    log_dict = {
        'url': str(request.url),
        'method': request.method,
        'client': request.client.host
        }        
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(log_dict)
    logger.info(f"Processed in {process_time:.2f} seconds")
    logger.info(f"Response: {response.status_code}")
    response.headers["X-Process-Time"] = str(process_time)
    return response