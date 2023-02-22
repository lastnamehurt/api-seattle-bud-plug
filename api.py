from fastapi import FastAPI
from services import SearchService
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware


service = SearchService()
app = FastAPI()

# Configure CORS settings
origins = [
    "https://seattle-bud-plug.herokuapp.com",
    "http://localhost",
    "http://localhost:3000",
    "https://seattlebudplug.com",
    "http://seattlebudplug.com",
    "https://www.seattlebudplug.com",
    "http://www.seattlebudplug.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/deals/cached")
async def get_cached_deals():
    keys = service.redis.keys("*")
    deals = []
    for key in keys:
        value = service.load_from_redis(key)
        deals.append({key.decode(): value})

    data = []
    for deal in deals:
        for _, products in deal.items():
            for item in products.get("items", []):
                data.append(service.parse_item_to_deal(item))
    return JSONResponse(content=data, media_type="application/json")


@app.get("/api/deals")
async def root():
    data = service.run()
    return JSONResponse(content=data, media_type="application/json")


@app.get("/redis/{key}")
async def get_value_from_redis(key: str):
    value = service.load_from_redis(key)
    if value is None:
        return {"message": "Key not found"}
    else:
        return {"key": key, "value": value}


@app.get("/redis")
async def get_all_values_from_redis():
    keys = service.redis.keys("*")
    values = []
    for key in keys:
        value = service.load_from_redis(key)
        values.append({"key": key, "value": value})
    return values
