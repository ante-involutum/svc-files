import os


from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from src.utils.editer import remake


app = FastAPI(name="files")

origins = [
    # "http://localhost",
    "*"
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


@app.post("/files/remake")
async def file_remake(file: UploadFile):
    open(f'{cache}/{file.filename}', 'wb').write(await file.read())
    remake(f'{cache}/{file.filename}', f'{cache}/{file.filename}')
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
