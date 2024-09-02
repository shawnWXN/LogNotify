import logging
import os
from dataclasses import dataclass, field


@dataclass
class _SETTING:
    NOTIFY_URL: str = field(default=os.getenv("NOTIFY_URL", ""))
    APP_NAME: str = field(default=os.getenv("APP_NAME", "undefined"))
    NOTIFY_USERID: str = field(default=os.getenv("NOTIFY_USERID", ""))
    NOTIFY_INTERVAL: int = field(default=os.getenv("NOTIFY_INTERVAL", 3600))
    NOTIFY_TRACK_LEVEL: int = field(default=os.getenv("NOTIFY_TRACK_LEVEL", logging.ERROR))


SETTING = _SETTING()
