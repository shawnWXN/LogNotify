import logging

from log_notify import init_notify
from loguru import logger

if __name__ == '__main__':
    init_notify(logger=logger, notify_track_level=logging.INFO, notify_url='https://**')
    logger.error('错误发生')
