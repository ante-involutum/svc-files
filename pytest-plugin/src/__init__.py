import pytest
from loguru import logger
from minio import Minio
from minio.error import InvalidResponseError


def pytest_terminal_summary(terminalreporter, config):

    htmlpath = config.getoption("htmlpath")
    rootdir = config.getoption("rootdir")
    minioClient = Minio(
        '127.0.0.1:9000',
        access_key='admin',
        secret_key='changeme',
        secure=False
    )

    try:
        minioClient.fput_object(
            'atop', htmlpath, htmlpath)
    except InvalidResponseError as err:
        logger.debug(err)

    terminalreporter.write_sep(
        "-", f"push html {rootdir}/{htmlpath} to minio")
