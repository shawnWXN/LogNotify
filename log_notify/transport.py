import multiprocessing


class Transport:

    def __init__(self):
        self.queue = multiprocessing.Queue()

    def push(self, msg: dict):
        self.queue.put(msg)

    def pop(self, block=True, timeout=None) -> dict:
        return self.queue.get(block, timeout)

    def count(self) -> int:
        return self.queue.qsize()

    def __str__(self) -> str:
        return f'{__class__.__name__}[{id(self.queue)}]'
