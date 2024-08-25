import logging

from log_notify.handle import init
from loguru import logger

if __name__ == '__main__':
    init(logger=logger, notify_track_level=logging.DEBUG, notify_url='https://baidu.com')
    logger.error('错误发生')