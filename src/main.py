import os
from io import BytesIO

from minio import Minio
from src.utils.editer import remake
from src.model.file import File, Plan
from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from src.env import MIDDLEWARE_MINIO_SERVICE_HOST, MIDDLEWARE_MINIO_SERVICE_PORT, MIDDLEWARE_MINIO_ACCESS_KEY, MIDDLEWARE_MINIO_SECRET_KEY


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
test_plans = []

minioClient = Minio(
    f'{MIDDLEWARE_MINIO_SERVICE_HOST}:{MIDDLEWARE_MINIO_SERVICE_PORT}',
    access_key=MIDDLEWARE_MINIO_ACCESS_KEY,
    secret_key=MIDDLEWARE_MINIO_SECRET_KEY,
    secure=False
)


@app.post("/files/v2")
async def file_upload_to_minio(file: UploadFile):
    byte = BytesIO(await file.read())
    length = len(byte.getvalue())
    result = minioClient.put_object('jmx', file.filename, byte, length)
    resp = {
        "code": 200,
        'details': {
            'bucket_name': result.bucket_name,
            'object_name': result.object_name,
            "etag": result.etag
        },
        "message": "success"
    }
    return resp


@app.post("/files/v2/plan")
async def files_plan(plan: Plan):
    test_plans.append(plan)
    resp = {
        "code": 200,
        'details': test_plans,
        "message": "success"
    }
    return resp


@app.get("/files/v2/plan")
async def get_plan():
    resp = {
        "code": 200,
        'details': test_plans,
        "message": "success"
    }
    return resp


@app.post("/files/v2/download/{plan_name}")
async def files_get_plan(plan_name):
    for i in test_plans:
        for k, m in i:
            if m == plan_name:
                for v in i.attachment:
                    name = v['object_name']
                    fp = f'{cache}/{name}'
                    result = minioClient.fget_object(
                        v['bucket_name'], name, fp)
    resp = {
        "code": 200,
        'details': {},
        "message": "success"
    }
    return resp


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
async def file_remake(file: File):
    remake(f'{cache}/{file.name}',
           f'{cache}/InfluxdbBackendListener-{file.name}')
    resp = {
        "code": 200,
        'details': {
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
