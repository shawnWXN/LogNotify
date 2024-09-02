import os
import functools
import inspect
import logging
import traceback
import typing
import warnings

from .report import ReportThread
from .setting import SETTING
from .transport import Transport
from .helper import track_log, is_loguru, level_switch, get_hostname, get_ip_isp, get_gmt_time, do_excluded


class _LoggerHandler:

    def __init__(self, logger, transport: Transport):
        self._logger = logger
        self._transport: typing.Optional[Transport] = transport

    @property
    def logger(self):
        return self._logger

    def log(self, msg, data=None, userid=None, do_print=True, do_report=False, exc_info=False, level=logging.DEBUG,
            title='custom_log'):
        """
        :param msg:
        :param data:
        :param userid:
        :param do_print:
        :param do_report:
        :param exc_info:
        :param level:
        :param title:
        :return:
        """

        if not isinstance(msg, str):
            msg = str(msg)

        track_log(self._logger, logging.DEBUG, "LogNotify custom_log: {} / {} / {} / {}".format(msg[0:1024],
                                                                                                data, do_print,
                                                                                                do_report))

        frame = inspect.getframeinfo(inspect.stack()[1][0])
        if do_print:
            log_info = '|{}:{} {}'.format(os.path.basename(frame.filename), frame.lineno, msg)
            if exc_info:
                if is_loguru(self._logger):
                    self._logger.log(logging.getLevelName(logging.ERROR), log_info + '\n' + traceback.format_exc())
                else:
                    self._logger.log(logging.ERROR, log_info, exc_info=exc_info)
            else:
                self._logger.log(level_switch(self._logger, level), log_info)

        if do_report and self._transport:
            message = {
                'title': title,
                'content': msg,
                'level': level,
                'app': "{} | {}".format(SETTING.APP_NAME or 'undefined', get_hostname()),
                'isp': get_ip_isp(),
                'lineno': r"{}:{}:{}".format(frame.filename.replace('\\', '\\\\'), frame.function, frame.lineno),
                'ts': get_gmt_time(),
                'userid': userid or SETTING.NOTIFY_USERID
            }
            if data and isinstance(data, dict):
                message['kwargs'] = data

            if do_excluded(message['lineno']):
                return

            self._transport.push(message)
            track_log(self._logger, logging.DEBUG, "LogNotify push {} to {}, left: {}".format(str(message)[:1024],
                                                                                              self._transport,
                                                                                              self._transport.count()))


def init_notify(logger, notify_url: str = '', app_name: str = '', notify_userid: str = '',
                notify_interval: typing.Optional[int] = None, notify_track_level: typing.Optional[int] = None):
    """
    :param logger:
    :param notify_url:
    :param app_name:
    :param notify_userid:
    :param notify_interval:
    :param notify_track_level:
    :return:
    """
    if notify_url:
        SETTING.NOTIFY_URL = notify_url
    if app_name:
        SETTING.APP_NAME = app_name
    if notify_userid:
        SETTING.NOTIFY_USERID = notify_userid
    if notify_interval:
        SETTING.NOTIFY_INTERVAL = notify_interval
    if notify_track_level:
        SETTING.NOTIFY_TRACK_LEVEL = notify_track_level

    track_log(logger, logging.INFO, "LogNotify init, {}".format(SETTING))

    t = None
    if isinstance(SETTING.NOTIFY_URL, str) and SETTING.NOTIFY_URL.startswith('http'):
        t = Transport()
        ReportThread(logger, t).start()
    else:
        warnings.warn("LogNotify `NOTIFY_URL` invalid, ReportThread will not start.")

    logger_handler = _LoggerHandler(logger, t)

    logger_handler.logger.exception = functools.partial(logger_handler.log, do_report=True, exc_info=True,
                                                        level=logging.ERROR, title='exception log')
    logger_handler.logger.error = functools.partial(logger_handler.log, do_report=True, exc_info=False,
                                                    level=logging.ERROR, title='error log')
    logger_handler.logger.warning = functools.partial(logger_handler.log, exc_info=False,
                                                      level=logging.WARNING, title='warn log')
    logger_handler.logger.info = functools.partial(logger_handler.log, exc_info=False,
                                                   level=logging.INFO, title='info log')
    logger_handler.logger.debug = functools.partial(logger_handler.log, exc_info=False,
                                                    level=logging.DEBUG, title='debug log')
