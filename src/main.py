import os
from fastapi import FastAPI, UploadFile

from starlette.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(name="files")

origins = [
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


cache = './cache'


@app.post("/upload/")
async def upload(fp: UploadFile):
    open(f'{cache}/{fp.filename}', 'wb').write(await fp.read())
    return {"filename": fp.filename}


@app.get("/file_list")
async def file_list():
    return os.listdir(f'{cache}')


@app.get("/download/{fp}")
async def download(fp):
    fn = f'{cache}/{fp}'
    return FileResponse(fn, filename=fp)
