# -*- coding:utf-8 -*-
import logging


logger = logging.getLogger()
LOG_FILE = "D:\\info.log"
handler = logging.FileHandler(LOG_FILE)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
# 将格式器设置到处理器上
handler.setFormatter(formatter)
# 将处理器加到日志对象上
logger.addHandler(handler)
logger.setLevel(logging.NOTSET)


def info(msg, *args):
    # logger.info(">>当前时间:%s 定时任务执行时间:%s", *args)
    logger.info(msg, *args)


def error(msg, *args):
    logger.error(msg, *args)
