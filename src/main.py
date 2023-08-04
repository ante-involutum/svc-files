import time
import shutil
import traceback
from io import BytesIO
from typing import List
from loguru import logger
from datetime import datetime

from minio import Minio
from minio.error import S3Error

from fastapi import FastAPI
from fastapi import Request
from fastapi import BackgroundTasks
from fastapi import UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware import Middleware
from starlette.responses import FileResponse
from starlette.staticfiles import StaticFiles
from starlette.middleware.errors import ServerErrorMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

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


background_tasks_status = {}


@app.on_event("startup")
async def startup_event():
    try:
        current_time = time.time()
        for folder in os.listdir('share'):
            folder_path = os.path.join('share', folder)
            if os.path.isdir(folder_path):
                modified_time = os.path.getmtime(folder_path)
                fmt= datetime.fromtimestamp(modified_time).strftime("%Y-%m-%d %H:%M:%S")
                logger.info(f"{folder_path} 修改时间: {fmt}")
                age = current_time - modified_time
                if age > int(LIFE_CYCLE) * 24 * 60 * 60:
                    try:
                        shutil.rmtree(folder_path)
                        logger.info(f"删除文件夹: {folder_path}")
                    except OSError as e:
                        logger.info(f"无法删除文件夹: {folder_path}，错误信息: {e}")
    except Exception as e:
        logger.error(traceback.format_exc())


@app.on_event("shutdown")
def shutdown_event():
    try:
        pass
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
            background_tasks_status[prefix] = {'status': 'generating'}
            for obj in objects:
                minioClient.fget_object(
                    bucket_name,
                    obj.object_name,
                    f'share/{obj.object_name}'
                )
            logger.info(f'BackgroundTasks: get {prefix} done')
            background_tasks_status[prefix] = {'status': 'completed'}

    except Exception as err:
        background_tasks_status[prefix] = {'status': 'erro'}
        logger.debug(err)


@app.get("/hello")
async def root():
    return {"message": "Hello World"}


@app.get("/files/")
async def get_object(bucket_name: str, prefix: str):
    try:
        data = minioClient.get_object(bucket_name, prefix)
        detail = {'code': 0, 'detail': data.data, 'message': 'success'}
        logger.info(detail)
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
            logger.info(details)
        resp = {
            "code": 0,
            'details': details,
            "message": "success"
        }
        return resp
    except Exception as e:
        logger.error(traceback.format_exc())
        raise FilesException(code=-1, detail={}, message='内部错误')


@app.get("/files/report/{bucket_name}/{type}/{prefix}")
async def get_report(bucket_name: str, type: str, prefix: str, background_tasks: BackgroundTasks):
    try:
        background_tasks_status[prefix] = {'status': 'notReady'}
        if os.path.exists(f'share/{prefix}'):
            dirs = os.listdir(f'share/{prefix}')
            dirs = sorted(dirs, reverse=True)
            resp = {
                'url': '',
                'status': 'completed'
            }
            if type == 'aomaker':
                resp['url'] = f"http://{HOST}:{PORT}/{ENV}/share/{prefix}/data/autotest/reports/html/index.html"
            if type == 'hatbox':
                resp['url'] = f"http://{HOST}:{PORT}/{ENV}/share/{prefix}/{dirs[0]}/hatbox/Log/report/pytest_html/index.html"
            background_tasks_status[prefix] = {'status': 'completed'}
            return resp
        else:
            logger.info('Test report does not exist, start regeneration')
            background_tasks.add_task(pull, bucket_name, prefix)
            resp = {
                'url': "",
                'status': 'generating'
            }
            logger.info('Test report regeneration completed')
            return resp
    except Exception as e:
        logger.error(traceback.format_exc())
        background_tasks_status[prefix] = {'status': 'erro'}
        raise FilesException(code=-1, detail={}, message='内部错误')


@app.get("/files/tasks/{prefix}")
async def get_background_tasks_status(prefix: str):
    try:
        logger.info(background_tasks_status)
        resp = background_tasks_status[prefix]
        return resp
    except Exception as e:
        logger.error(traceback.format_exc())
        raise FilesException(code=-1, detail={}, message='内部错误')


@app.get("/files/v1.1")
async def get_object_v1(bucket_name: str, prefix: str):
    try:
        data = minioClient.get_object(bucket_name, prefix)
        detail = {'code': 0, 'detail': data.data, 'message': 'success'}
        logger.info(detail)
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
    logger.info(report)
    try:
        prefix = f'{report.type}-{report.uid}'
        background_tasks_status[prefix] = {'status': 'notReady'}
        if os.path.exists(f'share/{prefix}'):
            dirs = os.listdir(f'share/{prefix}')
            dirs = sorted(dirs, reverse=True)
            resp = {
                'url': '',
                'status': 'completed'
            }
            if report.type == 'aomaker':
                resp['url'] = f"http://{HOST}:{PORT}/{ENV}/share/{prefix}{report.path}/index.html"
            if report.type == 'hatbox':
                resp['url'] = f"http://{HOST}:{PORT}/{ENV}/share/{prefix}/{dirs[0]}{report.path}/index.html"
            background_tasks_status[prefix] = {'status': 'completed'}
            return resp
        else:
            logger.info('Test report does not exist, start regeneration')
            background_tasks.add_task(pull, 'result', prefix)
            resp = {
                'url': "",
                'status': 'generating'
            }
            logger.info('Test report regeneration completed')
            return resp
    except Exception as e:
        logger.error(traceback.format_exc())
        raise FilesException(code=-1, detail={}, message='内部错误')
