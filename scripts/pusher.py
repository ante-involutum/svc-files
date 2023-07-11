import os
import shutil
import datetime
import traceback
from minio import Minio
from loguru import logger


logger.info('====== atop 开始处理测试报告 ======')
report = os.getenv('REPORT')
logger.info(f'测试报告路径为: {report}')

prefix = os.getenv('PREFIX')
logger.info(f'测试报告名称为: {prefix}')

minio_host = os.getenv('MINIO_HOST')
files_service = os.getenv('FILES_SERViCE')


def get_all_abs_path(source_dir):
    path_list = []
    for fpathe, dirs, fs in os.walk(source_dir):
        for f in fs:
            p = os.path.join(fpathe, f)
            path_list.append(p)
    return path_list


def push(bucket_name, prefix, metadata=None):

    try:
        minioClient = Minio(
            minio_host,
            access_key='admin',
            secret_key='changeme',
            secure=False
        )
        logger.info('minio客户端连接成功')
    except Exception as err:
        logger.debug('minio客户端连接失败')
        logger.debug(err)

    try:
        if os.path.isdir(report):
            object_list = get_all_abs_path(report)
        else:
            object_list = [report]
        logger.info('==开始备份测试报告至minio')
        for key in object_list:
            resp = minioClient.fput_object(
                bucket_name,
                prefix+key,
                key,
                metadata=metadata
            )
        logger.info('==测试报告已备份至minio')
    except Exception as err:
        logger.debug('测试报告备份至minio失败')
        logger.debug(err)


if __name__ == "__main__":
    if os.path.exists(report):
        try:
            t = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            source_folder = report
            # target_folder = f"/report/{prefix}/{t}{report}"
            target_folder = f"report/{prefix}/{t}/{report}"  # debug
            logger.info(f'开始复制测试报告到文件服务器共享存储目录:{target_folder} ...')
            try:
                shutil.rmtree(target_folder)
                logger.info(f'存在同名目录: {target_folder}')
                logger.info(f'删除同名目录: {target_folder}')
            except FileNotFoundError:
                pass

            shutil.copytree(source_folder, target_folder)
            logger.info('复制完成')

            # push('result', f"{prefix}/{t}")
        except Exception as err:
            logger.debug(err)
            logger.error(traceback.format_exc())
    else:
        logger.info('测试报告不存在')
    logger.info('======= atop 完成测试报告处理 =======')
