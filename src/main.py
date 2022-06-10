import os
from fastapi import FastAPI, UploadFile

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


@app.post("/files")
async def file_upload(file: UploadFile):
    open(f'{cache}/{file.filename}', 'wb').write(await file.read())
    resp = {
        "code": 200,
        'details': {
            "name": file.filename
        },
        "message": "success"
    }
    return resp


@app.get("/files")
async def files_list():
    resp = {
        "code": 200,
        'details': os.listdir(f'{cache}'),
        "message": "success"
    }
    return resp


@app.delete("/files/{name}")
async def file_remove(name):
    os.remove(f'{cache}/{name}')
    resp = {

        "code": 200,
        'details': {},
        "message": "success"

    }
    return resp
