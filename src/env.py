import os


MINIO_HOST = os.getenv('MINIO_HOST')
MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY')
MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY')
HOST = os.getenv('HOST')
PORT = os.getenv('PORT')
ENV = os.getenv('ENV')
LIFE_CYCLE = os.getenv('LIFE_CYCLE', default=30)
