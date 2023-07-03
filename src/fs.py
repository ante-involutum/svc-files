from fastapi import FastAPI
from starlette.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/share", StaticFiles(directory="share"), name="share")
app.mount("/404", StaticFiles(directory="404"), name="404")

@app.get("/")
async def root():
    return {"message": "Hello World"}