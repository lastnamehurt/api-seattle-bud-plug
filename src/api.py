import logging

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .services import SearchService

# Create a logger instance
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create a handler that writes logs to a file
handler = logging.FileHandler("app.log")
handler.setLevel(logging.DEBUG)

# Create a formatter that adds a timestamp to each log message
formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(handler)

# Instantiate service and app
service = SearchService()
app = FastAPI()

# Configure CORS settings
origins = [
    "https://api.seattlebudplug.com",
    "http://api.settlebudplug.com",
    "http://localhost",
    "http://localhost:3000",
    "http://www.seattlebudplug.com",
    "http://seattlebudplug.com",
    "https://seattlebudplug.com",
    "https://www.seattlebudplug.com",
    "https://seattle-bud-plug.herokuapp.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/v1/products")
async def get_cached_products_parsed():
    service.parse_items()
    logger.info("Retrieved cached products.")
    return JSONResponse(content=service.parsed_items, media_type="application/json")


@app.get("/v1/products/cached")
async def get_cached_deals():
    logger.info("Retrieved cached deals.")
    return JSONResponse(content=service.collection_items, media_type="application/json")


@app.get("/v1/products/fetch")
async def root():
    data = service.run()
    logger.info("Retrieved fresh products.")
    return JSONResponse(content=data, media_type="application/json")


@app.get("/redis/{key}")
async def get_value_from_redis(key: str):
    value = service.load_from_redis(key)
    if value is None:
        logger.warning(f'Key "{key}" not found in Redis.')
        return {"message": "Key not found"}
    else:
        logger.info(f'Retrieved value for key "{key}" from Redis.')
        return {"key": key, "value": value}


@app.get("/redis")
async def get_all_values_from_redis():
    keys = service.redis.keys("*")
    values = []
    for key in keys:
        value = service.load_from_redis(key)
        values.append({"key": key, "value": value})
    logger.info("Retrieved all values from Redis.")
    return values
