import yaml
import json
import traceback
from io import BytesIO
from typing import List
from loguru import logger

from minio import Minio
from minio.error import S3Error

from fastapi import FastAPI
from fastapi import UploadFile
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.env import *
from src.model import Report


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
        pass
    except Exception as e:
        logger.error(traceback.format_exc())


@app.on_event("shutdown")
def shutdown_event():
    try:
        pass
    except Exception as e:
        logger.error(traceback.format_exc())


@app.get("/v1.0/version")
async def version():
    try:
        with open('chart/Chart.yaml') as f:
            chart = yaml.safe_load(f)
            del chart['apiVersion']
            chart_json = json.dumps(chart)
            logger.info(chart_json)
        return chart_json
    except Exception as e:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail='内部错误')


@app.get("/v1.0/metrics")
async def metrics():
    logger.info()
    try:
        pass
    except Exception as e:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail='内部错误')


@app.post("/v1.0/object")
async def upload_object(bucket_name: str, files: List[UploadFile]):
    try:
        details = []
        for file in files:
            byte = BytesIO(await file.read())
            length = len(byte.getvalue())
            result = minioClient.put_object(
                bucket_name, file.filename, byte, length
            )
            details.append({'bucket_name': result.bucket_name,
                           'object_name': result.object_name, "etag": result.etag})
        resp = {"code": 0, 'details': details, "message": "success"}
        logger.info(resp)
        return resp
    except S3Error as e:
        logger.debug(e)
        raise HTTPException(status_code=500, detail=e.message)
    except Exception as e:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail='内部错误')


@app.get("/v1.0/object")
async def get_object(bucket_name: str, prefix: str):
    try:
        data = minioClient.get_object(bucket_name, prefix)
        detail = {'code': 0, 'detail': data.data, 'message': 'success'}
        logger.info(detail)
        return detail
    except S3Error as e:
        logger.debug(e)
        raise HTTPException(status_code=500, detail=e.message)
    except Exception as e:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail='内部错误')


@app.get("/v1.0/report")
async def get_report(report: Report):
    logger.info(report)
    try:
        prefix = f'{report.type}-{report.uid}'
        resp = {
            'url': f"http://{HOST}:{PORT}/{RELEASE}/share/result/{prefix}/index.html"
        }
        logger.info(resp)
        return resp
    except S3Error as e:
        logger.debug(e)
        raise HTTPException(status_code=500, detail=e.message)
    except Exception as e:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail='内部错误')
