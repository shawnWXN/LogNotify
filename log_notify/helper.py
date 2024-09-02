import pytz
import requests

import socket
import typing
import logging
import datetime
from functools import lru_cache


@lru_cache
def get_hostname() -> str:
    try:
        return socket.gethostname()
    except Exception:  # noqa
        return "localhost"


@lru_cache
def get_ip_isp() -> typing.Optional[str]:
    # FIXME It is possible that null is returned due to a timeout
    try:
        resp = requests.get('http://ip-api.com/json', timeout=3)  # noqa
        if resp.status_code != 200:
            return None

        resp_dict = resp.json()
        if resp_dict.get('isp') and resp_dict.get('query'):
            return "{} | {}".format(resp_dict.get('isp'), resp_dict.get('query'))

    except Exception:  # noqa
        return None


def get_gmt_time() -> str:
    return datetime.datetime.now(pytz.timezone('GMT')).strftime("%Y-%m-%d %H:%M:%S%z")


def do_excluded(info) -> bool:
    exclude_info = []
    for item in exclude_info:
        if item in info:
            return True

    return False


@lru_cache()
def level_switch(logger, level: int) -> typing.Union[int, str]:
    try:
        import loguru
        if isinstance(logger, loguru._logger.Logger) and isinstance(level, int):  # noqa
            return logging.getLevelName(level)
        return level
    except Exception:  # noqa
        return level


@lru_cache()
def is_loguru(logger) -> bool:
    try:
        import loguru
        if isinstance(logger, loguru._logger.Logger):  # noqa
            return True
        return False
    except Exception:  # noqa
        return False


def track_log(logger, level: int, msg: str):
    from .setting import SETTING

    if SETTING.NOTIFY_TRACK_LEVEL <= level:
        print(f'enter!! {level_switch(logger, level)} {msg}')
        logger.log(level_switch(logger, level), msg)
