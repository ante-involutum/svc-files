import shutil
from io import BytesIO
from loguru import logger

from minio import Minio
from minio.error import InvalidResponseError

from fastapi import FastAPI, UploadFile, BackgroundTasks
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


def get_report(bucket_name: str, prefix: str):
    try:
        objects = minioClient.list_objects(
            bucket_name,
            prefix=prefix,
            recursive=True
        )
        for obj in objects:
            logger.info(
                [
                    obj.bucket_name,
                    obj.object_name.encode('utf-8'),
                    obj.last_modified,
                    obj.etag,
                    obj.size,
                    obj.content_type
                ]
            )
            minioClient.fget_object(
                'atop', obj.object_name, f'cache/{obj.object_name}')
    except InvalidResponseError as err:
        logger.debug(err)


@app.get("/files/aomaker/{prefix}")
async def pull_report(prefix: str):
    get_report('atop', prefix)
    shutil.copytree(
        f'cache/{prefix}/data/autotest/reports/html',
        f'tmp/{prefix}/reports/{prefix}'
    )
    return 200


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
