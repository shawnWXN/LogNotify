import json
import time
import typing
import logging
import traceback
import requests
from functools import lru_cache
from urllib.parse import urlparse

from .setting import SETTING
from .helper import get_gmt_time


class _ReportSender:
    def __init__(self):
        self.task_ts_map = {}

    @staticmethod
    def _send_wework(task) -> typing.Optional[typing.Tuple[int, str]]:
        try:
            font_color = {50: 'red', 40: 'red', 30: 'yellow', 20: 'black', 10: 'gray'}.get(task.get('level')) or 'gray'
            markdown = '### Title: {title}\n' \
                       '<font color="{color}">[{level}]: {content}</font>\n' \
                       '> app: <font color="comment">{app}</font>\n' \
                       '> loc: <font color="comment">{isp}</font>\n' \
                       '> GTM: <font color="comment">{ts}</font>\n' \
                       '> code: <font color="comment">{lineno}</font>\n' \
                       '> kwargs: <font color="comment">{kwargs}</font>\n' \
                       ''.format(
                        title=task.get('title'),
                        color=font_color,
                        content=task.get('content'),
                        level=logging.getLevelName(task.get('level')),
                        app=task.get('app'),
                        isp=task.get('isp'),
                        ts=task.get('ts'),
                        lineno=task.get('lineno'),
                        kwargs=json.dumps(task.get('kwargs'), ensure_ascii=False)
            )
            if task.get('userid'):
                markdown += ",".join(['<@{}>'.format(u) for u in task.get('userid').split(',')])

            msg = {
                'msgtype': 'markdown',
                'markdown': {'content': markdown}
            }

            log_text = "LogNotify requests.post {}, json:{}, ".format(SETTING.NOTIFY_URL, str(task)[:1024])
            resp: requests.Response = requests.post(url=SETTING.NOTIFY_URL, json=msg, timeout=6)  # noqa

            if resp.status_code != 200 or not resp.headers.get('Content-Type').count('application/json') \
                    or resp.json().get('errcode') != 0:
                return logging.WARNING, log_text + "Response[{}] {}".format(resp.status_code, resp.content)

        except Exception:  # noqa
            return logging.ERROR, "LogNotify send wework error.\n" + traceback.format_exc()

    @staticmethod
    def _send_custom(task) -> typing.Optional[typing.Tuple[int, str]]:
        try:
            task.update({
                'level': logging.getLevelName(task.get('level'))
            })

            log_text = "LogNotify requests.post {}, json:{}, ".format(SETTING.NOTIFY_URL, str(task)[:1024])
            resp: requests.Response = requests.post(url=SETTING.NOTIFY_URL, json=task, timeout=6)  # noqa

            if resp.status_code != 200:
                return logging.WARNING, log_text + "Response[{}] {}".format(resp.status_code, resp.content)

            print(resp.status_code, resp.content)

        except Exception:  # noqa
            return logging.ERROR, "LogNotify send custom error.\n" + traceback.format_exc()

    @lru_cache()
    def _send(self, task_str: str, quotient: float) -> typing.Optional[typing.Tuple[int, str]]:
        """
        :param task_str:
        :param quotient: execution interval buffer
        :return:
        """
        task = json.loads(task_str)
        task['ts'] = self.task_ts_map.pop(task_str, None) or get_gmt_time()

        if 'qyapi.weixin.qq.com' == urlparse(SETTING.NOTIFY_URL).netloc:
            return self._send_wework(task)
        else:
            return self._send_custom(task)

    def report(self, task: dict) -> typing.Optional[typing.Tuple[int, str]]:
        ts = task.pop('ts', None)
        task_str = json.dumps(task, ensure_ascii=False)
        self.task_ts_map[task_str] = ts
        return self._send(task_str, time.time() // SETTING.NOTIFY_INTERVAL)


sender = _ReportSender()
