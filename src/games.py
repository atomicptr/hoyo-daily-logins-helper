import json
import random
import time
import logging

from src.http import http_get_json, http_post_json


RET_CODE_ALREADY_SIGNED_IN = -5003

GAMES = {
    "genshin": {
        "name": "Genshin Impact",
        "event_base_url": "https://hk4e-api-os.mihoyo.com/event/sol",
        "act_id": "e202102251931481",
    },
    "starrail": {
        "name": "Honkai: Star Rail",
        "event_base_url": "https://sg-public-api.hoyolab.com/event/luna/os",
        "act_id": "e202303301540311",
    }
}


def game_perform_checkin(
    account_ident: str,
    game: str,
    cookie_str: str,
    language: str,
):
    if game not in GAMES:
        raise Exception(f"unknown game identifier found: {game}")

    game_name = GAMES[game]["name"]
    event_base_url = GAMES[game]["event_base_url"]
    act_id = GAMES[game]["act_id"]

    referer_url = "https://act.hoyolab.com/"
    reward_url = f"{event_base_url}/home?lang={language}" \
                 f"&act_id={act_id}"
    info_url = f"{event_base_url}/info?lang={language}" \
               f"&act_id={act_id}"
    sign_url = f"{event_base_url}/sign?lang={language}"

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

    logging.info(f"Attempting checking for game {game_name} ({account_ident})")

    if already_signed_in:
        logging.info("Already checked in today")
        return

    if first_bind:
        logging.info("Please check in manually once")
        return

    awards_data = http_get_json(reward_url)

    awards = awards_data.get("data", {}).get("awards")

    logging.info(f"Checking in account for {today}...")

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