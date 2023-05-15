import json
import logging
from typing import Dict

import requests
from requests import HTTPError, Response

from src.utils import dict_prettify

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " \
              "AppleWebKit/537.36 (KHTML, like Gecko) " \
              "Chrome/74.0.3729.169 Safari/537.36"
_http_req_settings = {"user_agent": USER_AGENT}


def http_set_user_agent(user_agent: str):
    _http_req_settings["user_agent"] = user_agent


def http_get(url: str, max_retries: int = 2, **kwargs) -> Response:
    return http_request("get", url, max_retries, **kwargs)


def http_get_json(url: str, max_retries: int = 2, **kwargs) -> Dict[str, any]:
    resp = http_get(url, max_retries, **kwargs)
    data = resp.text
    return json.loads(data)


def http_post(url: str, max_retries: int = 2, **kwargs) -> Response:
    return http_request("post", url, max_retries, **kwargs)


def http_post_json(url: str, max_retries: int = 2, **kwargs) -> Dict[str, any]:
    resp = http_post(url, max_retries, **kwargs)
    data = resp.text
    return json.loads(data)


def http_request(
    method: str,
    url: str,
    max_retries: int = 2,
    **kwargs
) -> Response:
    for i in range(max_retries + 1):
        try:
            logging.debug(f"{method.upper()} {url}, REQ: {i+1}/{max_retries}")
            session = requests.Session()
            session.headers["User-Agent"] = _http_req_settings["user_agent"]
            resp = session.request(method, url, **kwargs)

            text = resp.text
            if resp.headers.get("Content-Type", "") == "application/json":
                text = dict_prettify(json.loads(text))
            logging.debug(f"Response: {resp.status_code}\n\n{text}\n")
        except HTTPError as e:
            logging.error(f"HTTP error: {e}, REQ: {i+1}/{max_retries}")
        except KeyError as e:
            logging.error(f"Wrong response: {e}, REQ: {i+1}/{max_retries}")
        except Exception as e:
            logging.error(f"Unknown error: {e}, REQ: {i+1}/{max_retries}")
        else:
            return resp
    raise Exception(f"All {max_retries} HTTP requests have failed")
