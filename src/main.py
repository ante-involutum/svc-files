from io import BytesIO

from minio import Minio
from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from src.env import *


app = FastAPI(name="files")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

minioClient = Minio(
    f'{MIDDLEWARE_MINIO_SERVICE_HOST}:{MIDDLEWARE_MINIO_SERVICE_PORT}',
    access_key=MIDDLEWARE_MINIO_ACCESS_KEY,
    secret_key=MIDDLEWARE_MINIO_SECRET_KEY,
    secure=False
)


@app.post("/files/upload")
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
