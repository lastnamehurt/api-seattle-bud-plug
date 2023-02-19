from fastapi import FastAPI
from services import SearchService
from fastapi.responses import JSONResponse

app = FastAPI()


@app.get("/")
async def root():
    data = SearchService().run()
    return JSONResponse(content=data, media_type="application/json")
