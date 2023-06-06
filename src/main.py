import shutil
import traceback
from io import BytesIO
from typing import List
from loguru import logger

from minio import Minio
from minio.error import S3Error

from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request, UploadFile

from src.env import *
from src.model import Report
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


@app.on_event("startup")
async def startup_event():
    try:
        objects = list(minioClient.list_objects(
            'templates',
            prefix='404',
            recursive=True
        ))
        if len(objects) != 2:
            logger.info('404 html not exist in tempplates bucket')
            minioClient.fput_object(
                'templates',
                '404/index.html',
                '404/index.html'
            )
            minioClient.fput_object(
                'templates',
                '404/styles.css',
                '404/styles.css'
            )
            logger.info('push 404 html to tempplates bucket')
    except Exception as e:
        logger.error(traceback.format_exc())


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
async def upload(bucket_name: str, files: List[UploadFile]):

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
        return {"url": f"http://{HOST}:{PORT}/{ENV}/share/{prefix}/data/autotest/reports/html"}
    elif type == 'hatbox':
        return {"url": f"http://{HOST}:{PORT}/{ENV}/share/{prefix}/hatbox/Log/report/pytest_html"}


@app.get("/files/v1.1")
async def get_object_v1(bucket_name: str, prefix: str):
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


@app.post("/files/v1.1")
async def upload_to_minio(bucket_name: str, files: List[UploadFile]):
    try:
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
        resp = {
            "code": 0,
            'details': details,
            "message": "success"
        }
        logger.info(resp)
        return resp
    except Exception as e:
        logger.error(traceback.format_exc())
        raise FilesException(code=-1, detail={}, message='内部错误')


@app.get("/files/v1.1/report")
async def get_report_v1(report: Report):
    prefix = f'{report.type}-{report.uid}'
    if os.path.exists(f'share/{prefix}'):
        shutil.rmtree(f'share/{prefix}', ignore_errors=True)
    else:
        pass

    try:
        objects = list(minioClient.list_objects(
            'result',
            prefix=prefix,
            recursive=True
        ))
        if len(objects) == 0:
            minioClient.fget_object(
                'templates',
                '404/index.html',
                f'share/{prefix}/{report.path}/index.html'
            )
            minioClient.fget_object(
                'templates',
                '404/styles.css',
                f'share/{prefix}/{report.path}/styles.css'
            )
        else:
            for obj in objects:
                minioClient.fget_object(
                    'result',
                    obj.object_name,
                    f'share/{obj.object_name}'
                )
        return {"url": f"http://{HOST}:{PORT}/{ENV}/share/{prefix}{report.path}"}
    except Exception as e:
        logger.error(traceback.format_exc())
        raise FilesException(code=-1, detail={}, message='内部错误')
