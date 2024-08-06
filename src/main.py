import io
import logging

from minio import Minio
from minio.error import S3Error

from fastapi import UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, UploadFile, HTTPException


from src.env import MINIO_HOST, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, HOST, NGINX

logger = logging.getLogger("uvicorn.error")

app = FastAPI(name="files")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


minio_client = Minio(
    MINIO_HOST,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False,
)


@app.post("/upload/{bucket}")
async def upload_files(bucket: str, files: list[UploadFile] = File(...)):
    try:
        for file in files:
            byte = io.BytesIO(await file.read())
            length = len(byte.getvalue())
            minio_client.put_object(bucket, file.filename, byte, length)
        return {"message": f"{len(files)} files uploaded successfully to {bucket}"}
    except S3Error as err:
        raise HTTPException(status_code=500, detail=f"Error: {err}")


@app.get("/download/")
async def download_file(bucket: str, object: str):
    try:
        response = minio_client.get_object(bucket, object)
        file_data = response.read()
        return {"file_data": file_data.decode("utf-8")}
    except S3Error as err:
        raise HTTPException(status_code=404, detail=f"File not found: {err}")


@app.get("/query")
async def query_files(bucket: str, prefix: str = None, recursive: bool = True):
    resp = {"folders": None}
    try:
        objects = minio_client.list_objects(bucket, prefix=prefix, recursive=recursive)
        file_list = []
        for obj in objects:
            file_list.append(obj.object_name)
        resp["folders"] = file_list
        logger.debug(resp)
        return resp
    except S3Error as err:
        raise HTTPException(status_code=500, detail=f"Error: {err}")


@app.get("/report")
async def get_report(type: str, uid: str, path: str):
    prefix = f"{type}-{uid}/"
    resp = {"url": None}
    try:
        objects = minio_client.list_objects("result", prefix=prefix, recursive=False)
        file_list = []
        for obj in objects:
            if obj.object_name.endswith("/"):
                file_list.append(obj.object_name)

        if len(file_list) == 0:
            # raise HTTPException(status_code=404, detail="Report not found")
            return resp

        url = f"http://{HOST}:{NGINX}/result/{file_list[-1]}{path[1:]}"
        resp["url"] = url
        logger.debug(resp)
        return resp
    except S3Error as err:
        raise HTTPException(status_code=500, detail=f"Error: {err}")


@app.get("/get")
async def get_file(type: str, uid: str, path: str):
    prefix = f"{type}-{uid}/"
    resp = {"data": None}
    try:
        objects = minio_client.list_objects("result", prefix=prefix, recursive=False)
        file_list = []
        for obj in objects:
            if obj.object_name.endswith("/"):
                file_list.append(obj.object_name)
        if len(file_list) != 0:
            name = file_list[0] + path[1:]
            response = minio_client.get_object("result", name)
            file_data = response.read()
            resp["data"] = file_data.decode("utf-8")
            logger.debug(resp)
            return resp
        logger.debug(resp)
        return resp
    except S3Error as err:
        raise HTTPException(status_code=500, detail=f"Error: {err}")
