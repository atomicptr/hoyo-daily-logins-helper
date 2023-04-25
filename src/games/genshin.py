import json
import random
import time

from src.config import parse_cookie_string, log
from src.http import http_get_json, http_post_json

_LANG = "en-us"
_ACT_ID = "e202102251931481"
_REFERER_URL = f"https://webstatic-sea.mihoyo.com/ys/event/signin-sea/index" \
               f".html?act_id={_ACT_ID}"
_REWARD_URL = f"https://hk4e-api-os.mihoyo.com/event/sol/home?lang={_LANG}" \
              f"&act_id={_ACT_ID}"
_INFO_URL = f"https://hk4e-api-os.mihoyo.com/event/sol/info?lang={_LANG}" \
            f"&act_id={_ACT_ID}"
_SIGN_URL = f"https://hk4e-api-os.mihoyo.com/event/sol/sign?lang={_LANG}"
RET_CODE_ALREADY_SIGNED_IN = -5003


def run(cookie_str: str):
    cookies = parse_cookie_string(cookie_str)

    token = cookies["ltoken"]
    uid = cookies["account_id"]

    log.debug(f"UID: {uid}")

    if not token or not uid:
        raise Exception("account_id and/or ltoken data is missing")

    headers = {
        "Referer": _REFERER_URL,
        "Accept-Encoding": "gzip, deflate, br",
        "Cookie": cookie_str,
    }

    info_list = http_get_json(_INFO_URL, headers=headers)

    today = info_list.get("data", {}).get("today")
    total_sign_in_day = info_list.get("data", {}).get("total_sign_day")
    already_signed_in = info_list.get("data", {}).get("is_sign")
    first_bind = info_list.get("data", {}).get("first_bind")

    log.debug(f"Today is {today}")

    if already_signed_in:
        log.info("Already checked in today")
        return

    if first_bind:
        log.info("Please check in manually once")
        return

    awards_data = http_get_json(_REWARD_URL)

    awards = awards_data.get("data", {}).get("awards")

    log.info(f"Checking in account {uid} for today...")

    # a normal human can't instantly click, so we wait a bit
    sleep_time = random.uniform(2.0, 10.0)
    log.debug(f"Sleep for {sleep_time}")
    time.sleep(sleep_time)

    request_data = json.dumps({
        "act_id": _ACT_ID,
    }, ensure_ascii=False)

    response = http_post_json(_SIGN_URL, headers=headers, data=request_data)

    code = response.get("retcode", 99999)

    log.debug(f"return code {code}")

    if code == RET_CODE_ALREADY_SIGNED_IN:
        log.info("Already signed in for today...")
        return
    elif code != 0:
        log.error(f"Something might have gone wrong, unknown retcode: {code}")
        return

    reward = awards[total_sign_in_day - 1]

    log.info("Check-in complete!")
    log.info(f"\tTotal Sign-in Days: {total_sign_in_day + 1}")
    log.info(f"\tReward: {reward['cnt']}x {reward['name']}")
    log.info(f"\tMessage: {response['message']}")
