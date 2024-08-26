import time
import logging
import threading
import traceback
from queue import Empty

from .helper import track_log
from .send import sender
from .transport import Transport


class ReportThread:

    def __init__(self, logger, transport: Transport, worker_num: int = 1, sleep_interval: int = 2):
        """
        :param logger: LoggerHandler
        :param transport: Transport
        :param worker_num:
        :param sleep_interval:
        """
        assert worker_num >= 1, "LogNotify ReportThread `worker_num` must >= 1"
        assert sleep_interval >= 2, "LogNotify ReportThread `sleep_interval` must >= 2"
        self._logger = logger
        self._transport: Transport = transport

        self.worker_num: int = worker_num
        self.sleep_interval: int = sleep_interval

        self.task_thread_list: list = []
        self.is_running: bool = False

    def __run(self, main_thread: threading.Thread):

        while self.is_running:
            try:

                if not main_thread.is_alive():
                    self.stop()
                    continue

                task = self._transport.pop(timeout=2)
                if not isinstance(task, dict):  # tips, The default consumer processes only dict tasks
                    track_log(self._logger, logging.WARNING, 'LogNotify ReportThread invalid ({}){}, from {}.'
                                                             ''.format(type(task), str(task)[:1024], self._transport))
                    continue

            except Empty:
                track_log(self._logger, logging.DEBUG, 'LogNotify ReportThread empty {}, sleep {}s ...'
                                                       ''.format(self._transport, self.sleep_interval))
                time.sleep(self.sleep_interval)
                continue

            except Exception:  # noqa
                track_log(self._logger, logging.ERROR, 'LogNotify ReportThread running error.\n'
                                                       '' + traceback.format_exc())
                time.sleep(self.sleep_interval)
                continue

            res = sender.report(task)
            if res:
                track_log(self._logger, res[0], res[1])
            else:

                track_log(self._logger, logging.DEBUG,
                          'LogNotify ReportThread success {}, left: {}.'.format(str(task)[:1024],
                                                                                self._transport.count()))

        track_log(self._logger, logging.INFO, "LogNotify ReportThread terminated.")

    def start(self):

        for worker_no in range(self.worker_num):
            self.task_thread_list.append(
                threading.Thread(target=self.__run, name='LogNotifyReportThread-{}'.format(worker_no),
                                 args=(threading.current_thread(),))
            )

        self.is_running = True
        for task_thread in self.task_thread_list:
            task_thread.start()

        track_log(self._logger, logging.INFO, "LogNotify ReportThread started.")

    def stop(self):
        self.is_running = False
        track_log(self._logger, logging.INFO, "LogNotify ReportThread try to terminate...")
