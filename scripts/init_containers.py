from pprint import pprint
from minio import Minio
import os

MIDDLEWARE_MINIO_SERVICE_HOST = os.getenv('MIDDLEWARE_MINIO_SERVICE_HOST')
MIDDLEWARE_MINIO_SERVICE_PORT = os.getenv('MIDDLEWARE_MINIO_SERVICE_PORT')
MIDDLEWARE_MINIO_ACCESS_KEY = os.getenv('MIDDLEWARE_MINIO_ACCESS_KEY')
MIDDLEWARE_MINIO_SECRET_KEY = os.getenv('MIDDLEWARE_MINIO_SECRET_KEY')
BUCKET_NAME = os.getenv('BUCKET_NAME')
PREFIX = os.getenv('PREFIX')


minioClient = Minio(
    f'{MIDDLEWARE_MINIO_SERVICE_HOST}:{MIDDLEWARE_MINIO_SERVICE_PORT}',
    access_key=MIDDLEWARE_MINIO_ACCESS_KEY,
    secret_key=MIDDLEWARE_MINIO_SECRET_KEY,
    secure=False
)


def obj_to_dict(x):
    return {
        'bucket_name': x.bucket_name,
        'object_name': x.object_name,
        'is_dir': x.is_dir,
        'size': x.size,
        'etag': x.etag,
        'last_modified': x.last_modified,
        'content_type': x.content_type,
        'metadata': x.metadata,
    }


def get_dirs(bucket_name='jmx', prefix=None):
    dirs = minioClient.list_objects(
        bucket_name=bucket_name,
        prefix=prefix,
        recursive=False
    )
    return list(map(obj_to_dict, dirs))


def get_objs(bucket_name='jmx', prefix=None):
    objs = minioClient.list_objects(
        bucket_name=bucket_name,
        prefix=prefix,
        recursive=True
    )
    return list(map(obj_to_dict, objs))


for i in list(map(lambda x: x['object_name'], get_objs(bucket_name=BUCKET_NAME, prefix=PREFIX))):
    pprint(i)
    minioClient.fget_object(
        bucket_name='jmx', object_name=i, file_path=i)
