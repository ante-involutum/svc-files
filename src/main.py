import shutil
from io import BytesIO
from typing import List
from loguru import logger

from minio import Minio
from minio.error import InvalidResponseError

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, UploadFile, BackgroundTasks

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
    MINIO_HOST,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False
)


def pull(bucket_name: str, prefix: str):
    try:
        objects = list(minioClient.list_objects(
            bucket_name,
            prefix=prefix,
            recursive=True
        ))

        if len(objects) == 0:
            logger.info(f'{prefix} not in {bucket_name} bucket')
            shutil.copytree('404', f'share/{prefix}/data/autotest/reports/html')
        else:
            for obj in objects:
                logger.info(
                    [
                        obj.bucket_name,
                        obj.last_modified,
                        obj.etag,
                        obj.size,
                        obj.content_type
                    ]
                )
                minioClient.fget_object(
                    bucket_name, obj.object_name, f'share/{obj.object_name}')
    except Exception as err:
        logger.debug(err)


@app.get("/files/")
async def get_object(bucket_name: str, prefix: str):
    try:
        data = minioClient.get_object(bucket_name, prefix)
        return data.data
    except InvalidResponseError as e:
        logger.debug(e)
        raise HTTPException(status_code=e._code, detail=e._body)


@app.post("/files/upload/")
async def file_upload_to_minio(bucket_name: str, files: List[UploadFile]):

    details = []

    for file in files:
        byte = BytesIO(await file.read())
        length = len(byte.getvalue())
        result = minioClient.put_object(
            bucket_name, file.filename, byte, length)
        details.append({
            'bucket_name': result.bucket_name,
            'object_name': result.object_name,
            "etag": result.etag
        })
    resp = {
        "code": 200,
        'details': details,
        "message": "success"
    }
    return resp


@app.get("/files/report/{bucket_name}/{type}/{prefix}")
async def get_report(bucket_name: str, type: str, prefix: str):
    if os.path.exists(f'share/{prefix}'):
        shutil.rmtree(f'share/{prefix}', ignore_errors=True)
    else:
        pass
    pull(bucket_name, prefix)
    logger.info(f'get {prefix} report')

    if type == 'aomaker':
        return {"url": f"http://{HOST}:{PORT}/share/{prefix}/data/autotest/reports/html"}
    elif type == 'locust':
        return {"url": f"http://{HOST}:{PORT}/share/{prefix}/demo/report.html"}
    elif type == 'jmeter':
        return {"url": f"http://{HOST}:{PORT}/share/{prefix}/demo/report"}


@app.get("/files/generate_report/{bucket_name}/{prefix}")
async def pull_form_minio(bucket_name: str, prefix: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(pull, bucket_name, prefix)
    logger.info(f'Generate_report {prefix} in the background')
    return {"message": "Generate report in the background"}
