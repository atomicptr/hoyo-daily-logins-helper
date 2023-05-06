import logging
import os
from typing import Optional

_default_configs = {
    "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/74.0.3729.169 Safari/537.36",
    "LANGUAGE": "en-us"
}

_config_conversions = {
    "LANG": "LANGUAGE"
}

CONFIG_USER_AGENT = "USER_AGENT"
CONFIG_LANG = "LANGUAGE"

def get_config(key: str) -> Optional[str]:
    value = _get_config_value(key)
    logging.debug(f"get configuration variable {key}: {value}")
    return value


def _get_config_value(key: str) -> Optional[str]:
    if key in _config_conversions:
        key = _config_conversions[key]

    if key not in os.environ:
        if key in _default_configs:
            return _default_configs[key]
        return None
    return os.environ[key]