import os
import pytest
from minio import Minio
from loguru import logger


def pytest_addoption(parser, pluginmanager):
    mygroup = parser.getgroup("reprtPush")
    mygroup.addoption(
        "--host",
        default='middleware-minio.tink:9000',
        dest='minio_host',
        help='minio host'
    )
    mygroup.addoption(
        "--user",
        default='admin',
        dest='minio_user',
        help='minio access key'
    )
    mygroup.addoption(
        "--password",
        default='changeme',
        dest='minio_password',
        help='minio secret key'
    )
    mygroup.addoption(
        "--prefix",
        default='report.html',
        dest='minio_prefix',
        help='mini object prefix'
    )


def pytest_terminal_summary(terminalreporter, config):

    htmlpath = config.getoption("htmlpath")
    rootdir = config.getoption("rootdir")
    if rootdir == None:
        rootdir = os.getcwd()
    minio_host = config.getoption("minio_host")
    minio_user = config.getoption("minio_user")
    minio_password = config.getoption("minio_password")
    minio_prefix = config.getoption("minio_prefix")
    logger.info((minio_user, minio_host, minio_password, minio_prefix))

    if os.path.isdir(minio_prefix):
        object_list = []
        for _ in os.listdir(minio_prefix):
            object_list.append(os.path.join(minio_prefix, _))
    else:
        object_list = [minio_prefix]
    try:
        minioClient = Minio(
            minio_host,
            access_key=minio_user,
            secret_key=minio_password,
            secure=False
        )
        logger.info(object_list)
        for key in object_list:
            minioClient.fput_object('atop', key, key)
    except Exception as err:
        logger.debug(err)

    terminalreporter.write_sep(
        "-", f"push report {rootdir}/{htmlpath} to minio")
