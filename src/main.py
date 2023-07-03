import shutil
import time
import traceback
from io import BytesIO
from typing import List
from loguru import logger

from minio import Minio
from minio.error import S3Error

from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request, UploadFile

from fastapi import FastAPI, Request, BackgroundTasks
from starlette.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware import Middleware
from starlette.middleware.errors import ServerErrorMiddleware
from starlette.responses import FileResponse, HTMLResponse

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


middleware = [
    Middleware(ServerErrorMiddleware, handlers={
               StarletteHTTPException: "custom_error_handler"})
]
app.middleware_stack = middleware


@app.exception_handler(StarletteHTTPException)
async def custom_error_handler(request: Request, exc: StarletteHTTPException):
    return FileResponse('404/index.html')

app.mount("/share", StaticFiles(directory="share"), name="share")
app.mount("/404", StaticFiles(directory="404"), name="404")


minioClient = Minio(
    MINIO_HOST,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False
)


@app.on_event("startup")
async def startup_event():
    try:
        # 删除前30天的文件夹
        current_time = time.time()
        for folder in os.listdir('share'):
            folder_path = os.path.join('share', folder)
            if os.path.isdir(folder_path):
                modified_time = os.path.getmtime(folder_path)
                age = current_time - modified_time
                if age > 30 * 24 * 60 * 60:
                    try:
                        os.removedirs(folder_path)
                        logger.info(f"已删除文件夹: {folder_path}")
                    except OSError as e:
                        logger.info(f"无法删除文件夹: {folder_path}，错误信息: {e}")
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
        else:
            for obj in objects:
                minioClient.fget_object(
                    bucket_name,
                    obj.object_name,
                    f'share/{obj.object_name}'
                )
            logger.info(f'get {prefix} done')

    except Exception as err:
        logger.debug(err)


@app.get("/hello")
async def root():
    return {"message": "Hello World"}


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
async def get_report(bucket_name: str, type: str, prefix: str, background_tasks: BackgroundTasks):

    try:
        m = {
            'hatbox': {
                'url': f"http://{HOST}:{PORT}/{ENV}/share/{prefix}/hatbox/Log/report/pytest_html/index.html"
            },
            'aomaker': {
                "url": f"http://{HOST}:{PORT}/{ENV}/share/{prefix}/data/autotest/reports/html/index.html"
            }
        }

        if os.path.exists(f'share/{prefix}'):
            m[type]['status'] = 'completed'
        else:
            background_tasks.add_task(
                pull, bucket_name, prefix, message="generating report")
            logger.info("generating repor")
            m[type]['status'] = 'generating'
        return m[type]
    except Exception as e:
        logger.error(traceback.format_exc())
        raise FilesException(code=-1, detail={}, message='内部错误')


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
async def get_report_v1(report: Report, background_tasks: BackgroundTasks):

    try:
        prefix = f'{report.type}-{report.uid}'
        m = {"url": f"http://{HOST}:{PORT}/{ENV}/share/{prefix}{report.path}"}

        if os.path.exists(f'share/{prefix}'):
            m['status'] = 'completed'
        else:
            background_tasks.add_task(
                pull, 'result', prefix, message="generating report")
            logger.info("generating repor")
            m['status'] = 'generating'
        return m
    except Exception as e:
        logger.error(traceback.format_exc())
        raise FilesException(code=-1, detail={}, message='内部错误')
