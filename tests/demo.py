import logging

from log_notify.handle import init_notify
from loguru import logger

if __name__ == '__main__':
    init_notify(logger=logger, notify_track_level=logging.INFO, notify_url='https://autoseo.geeksmonkey.com/wb/api/alive')
    logger.error('错误发生')