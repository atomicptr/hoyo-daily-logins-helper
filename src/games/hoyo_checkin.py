import json
import random
import time
import logging

from src.http import http_get_json, http_post_json


RET_CODE_ALREADY_SIGNED_IN = -5003


def hoyo_checkin(
    event_base_url: str,
    act_id: str,
    uid: str,
    token: str,
    cookie_str: str
):
    lang = "en-us"
    referer_url = "https://act.hoyolab.com/"
    reward_url = f"{event_base_url}/home?lang={lang}" \
                 f"&act_id={act_id}"
    info_url = f"{event_base_url}/info?lang={lang}" \
               f"&act_id={act_id}"
    sign_url = f"{event_base_url}/sign?lang={lang}"

    if not token or not uid:
        raise Exception("account_id and/or ltoken data is missing")

    headers = {
        "Referer": referer_url,
        "Accept-Encoding": "gzip, deflate, br",
        "Cookie": cookie_str,
    }

    info_list = http_get_json(info_url, headers=headers)

    today = info_list.get("data", {}).get("today")
    total_sign_in_day = info_list.get("data", {}).get("total_sign_day")
    already_signed_in = info_list.get("data", {}).get("is_sign")
    first_bind = info_list.get("data", {}).get("first_bind")

    logging.debug(f"Today is {today}")

    if already_signed_in:
        logging.info("Already checked in today")
        return

    if first_bind:
        logging.info("Please check in manually once")
        return

    awards_data = http_get_json(reward_url)

    awards = awards_data.get("data", {}).get("awards")

    logging.info(f"Checking in account {uid} for today...")

    # a normal human can't instantly click, so we wait a bit
    sleep_time = random.uniform(2.0, 10.0)
    logging.debug(f"Sleep for {sleep_time}")
    time.sleep(sleep_time)

    request_data = json.dumps({
        "act_id": act_id,
    }, ensure_ascii=False)

    response = http_post_json(sign_url, headers=headers, data=request_data)

    code = response.get("retcode", 99999)

    logging.debug(f"return code {code}")

    if code == RET_CODE_ALREADY_SIGNED_IN:
        logging.info("Already signed in for today...")
        return
    elif code != 0:
        logging.error(response['message'])
        return

    reward = awards[total_sign_in_day - 1]

    logging.info("Check-in complete!")
    logging.info(f"\tTotal Sign-in Days: {total_sign_in_day + 1}")
    logging.info(f"\tReward: {reward['cnt']}x {reward['name']}")
    logging.info(f"\tMessage: {response['message']}")