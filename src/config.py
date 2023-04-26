import os
from http.cookies import SimpleCookie
from typing import Optional, Dict

_default_configs = {
    "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/74.0.3729.169 Safari/537.36"
}

CONFIG_USER_AGENT = "USER_AGENT"


def get_config(key: str) -> Optional[str]:
    if key not in os.environ:
        if key in _default_configs:
            return _default_configs[key]
        return None
    return os.environ[key]


def parse_cookie_string(cookie: str) -> Dict[str, str]:
    c = SimpleCookie()
    c.load(cookie)
    return {k: v.value for k, v in c.items()}
