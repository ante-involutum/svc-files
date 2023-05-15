import shutil
from io import BytesIO
from typing import List
from loguru import logger

from minio import Minio
from minio.error import S3Error

from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request, UploadFile, BackgroundTasks

from src.env import *
from src.exceptions import FilesException

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


@app.exception_handler(FilesException)
async def files_exception_handler(request: Request, exc: FilesException):
    return JSONResponse(
        status_code=200,
        content={
            'code': exc.code,
            'detail': exc.detail,
            'message': exc.message
        },
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
            shutil.copytree(
                '404',
                f'share/{prefix}/data/autotest/reports/html'
            )
        else:
            for obj in objects:
                minioClient.fget_object(
                    bucket_name,
                    obj.object_name,
                    f'share/{obj.object_name}'
                )
    except Exception as err:
        logger.debug(err)


@app.get("/files/")
async def get_object(bucket_name: str, prefix: str):
    try:
        data = minioClient.get_object(bucket_name, prefix)
        detail = {'code': 0, 'detail': data.data, 'message': 'success'}
        return detail
    except S3Error as e:
        logger.debug(e)
        raise FilesException(
            code=-1,
            detail={},
            message=e.message
        )


@app.post("/files/upload/")
async def file_upload_to_minio(bucket_name: str, files: List[UploadFile]):

    details = []

    for file in files:
        byte = BytesIO(await file.read())
        length = len(byte.getvalue())
        result = minioClient.put_object(
            bucket_name, file.filename, byte, length
        )
        details.append({
            'bucket_name': result.bucket_name,
            'object_name': result.object_name,
            "etag": result.etag
        })
        logger.info(details)
    resp = {
        "code": 0,
        'details': details,
        "message": "success"
    }
    return resp


@app.get("/files/report/{bucket_name}/{type}/{prefix}")
async def get_report(bucket_name: str, type: str, prefix: str):
    if os.path.exists(f'share/{prefix}'):
        pass
    else:
        pull(bucket_name, prefix)
        logger.info(f'get {prefix} report')

    if type == 'aomaker':
        return {"url": f"http://{HOST}:{PORT}/share/{prefix}/data/autotest/reports/html"}
    elif type == 'hatbox':
        return {"url": f"http://{HOST}:{PORT}/share/{prefix}/hatbox/Log/report/pytest_html"}

@app.get("/files/generate_report/{bucket_name}/{prefix}")
async def pull_form_minio(bucket_name: str, prefix: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(pull, bucket_name, prefix)
    logger.info(f'Generate_report {prefix} in the background')
    return {"message": "Generate report in the background"}
