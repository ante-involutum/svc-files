from io import BytesIO
from loguru import logger

from minio import Minio

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, UploadFile, BackgroundTasks

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


@app.post("/files/generate_report/{prefix}")
async def pull_form_minio(prefix: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(pull, 'atop', prefix)
    logger.info(f'Generate_report {prefix} in the background')
    return {"message": "Generate_report in the background"}


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
