import os
from fastapi import FastAPI
from services import SearchService
from fastapi.responses import JSONResponse
import redis
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

# Configure CORS settings
origins = [
    "https://seattle-bud-plug.herokuapp.com",
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

# async def startup_event():
#     app.state.redis = await redis.create_redis_pool(redis_url)

@app.on_event("startup")
def startup_event():
    app.state.redis = redis.from_url(redis_url)

@app.on_event("shutdown")
async def shutdown_event():
    app.state.redis.close()

@app.get("/incr/{key}")
async def incr_key(key: str):
    value = app.state.redis.incr(key)
    return {"key": key, "value": value}

@app.get("/api/deals")
async def root():
    data = SearchService().run()
    return JSONResponse(content=data, media_type="application/json")
