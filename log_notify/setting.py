import logging
import os
from dataclasses import dataclass, field


@dataclass
class _SETTING:
    NOTIFY_URL: str = field(default="")
    APP_NAME: str = field(default="undefined")
    NOTIFY_USERID: str = field(default="")
    NOTIFY_INTERVAL: int = field(default=3600)
    NOTIFY_TRACK_LEVEL: int = field(default=logging.ERROR)

    def __init__(self):
        for attr, _field in self.__dataclass_fields__.items():  # noqa
            env_value = os.getenv(attr)
            if env_value is not None:
                setattr(self, attr, self._convert_type(_field.type, env_value))

        self.__post_init__()

    def __post_init__(self):
        assert self.NOTIFY_TRACK_LEVEL in (10, 20, 30, 40, 50), "LogNotify `NOTIFY_TRACK_LEVEL` from env, out of enum."
        assert self.NOTIFY_INTERVAL > 0, "LogNotify `NOTIFY_INTERVAL` from env, must > 0."

    @staticmethod
    def _convert_type(field_type, env_value):
        if field_type == bool:
            return env_value.lower() in ('true', '1', 'yes', 'ok')
        elif field_type == int:
            return int(env_value)
        return env_value


SETTING = _SETTING()
