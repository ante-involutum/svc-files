from io import BytesIO
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
        objects = minioClient.list_objects(
            bucket_name,
            prefix=prefix,
            recursive=True
        )
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
                'atop', obj.object_name, f'share/{obj.object_name}')
    except Exception as err:
        logger.debug(err)


@app.get("/files/")
async def get_object(prefix: str):
    try:
        data = minioClient.get_object('atop', prefix)
        return data.data
    except InvalidResponseError as e:
        logger.debug(e)
        raise HTTPException(status_code=e._code, detail=e._body)


@app.post("/files/upload")
async def file_upload_to_minio(file: UploadFile):
    byte = BytesIO(await file.read())
    length = len(byte.getvalue())
    result = minioClient.put_object('atop', file.filename, byte, length)
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


@app.get("/files/report/{type}/{prefix}")
async def get_report(type: str, prefix: str):
    if os.path.exists('share/' + prefix):
        pass
    else:
        pull('atop', prefix)
    logger.info(f'get {prefix} report')

    if type == 'aomaker':
        return {"url": f"http://tink.test:31695/share/{prefix}/data/autotest/reports/html"}
    elif type == 'locust':
        return {"url": f"http://tink.test:31695/share/{prefix}/demo/report.html"}


@app.get("/files/generate_report/{prefix}")
async def pull_form_minio(prefix: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(pull, 'atop', prefix)
    logger.info(f'Generate_report {prefix} in the background')
    return {"message": "Generate report in the background"}
