import logging
from datetime import datetime, timezone, time
from time import sleep
from typing import Optional

import pytz
from scheduler import Scheduler

from hoyo_daily_logins_helper.games import game_perform_checkin
from hoyo_daily_logins_helper.notifications import NotificationManager

_RESET_TIME = {
    # running this one hour after reset to prevent potential fuckery with
    # timezones
    "hour": 5,
    "minute": 1,
}

_RESET_TIMES = {
    "Asia": time(tzinfo=pytz.timezone("Asia/Shanghai"), **_RESET_TIME),
    "EU": time(tzinfo=pytz.timezone("CET"), **_RESET_TIME),
    "NA": time(tzinfo=pytz.timezone("US/Pacific"), **_RESET_TIME),
}


def run_scheduler(
        config_data: dict,
        language: str,
        notifications_manager: Optional[NotificationManager]
):
    logging.info("Run in scheduler mode")

    tz = datetime.now(timezone.utc).astimezone().tzinfo

    schedule = Scheduler(tzinfo=tz)

    accounts = config_data.get("accounts", [])
    default_region = config_data.get("config", {}).get("region", None)

    for index, account in enumerate(accounts):
        region = account.get("region", default_region)

        if not region:
            logging.error(f"Account #{index}: No region defined")
            continue

        if region not in _RESET_TIMES:
            logging.error(f"Account #{index}: Invalid region set '{region}'")
            continue

        identifier = account.get("identifier", None)

        if not identifier:
            identifier = f"Account #{index}"

        checkin_job = create_checkin_job(
            identifier,
            account.get("game"),
            account.get("cookie"),
            language,
            notifications_manager,
        )

        job = schedule.daily(
            _RESET_TIMES[region],
            checkin_job
        )

        due_in_hours = round(
            job.timedelta(datetime.now(tz=tz)).total_seconds() / 60 / 60,
            1
        )

        logging.info(
            f"Added account '{identifier}' to scheduler, region: '{region}', "
            f"next fire time in {due_in_hours} hours"
        )

    if len(schedule.jobs) == 0:
        logging.error("No jobs scheduled")
        exit(1)

    logging.debug("Job schedule:")
    logging.debug(schedule)

    while True:
        schedule.exec_jobs()
        sleep(60)


def create_checkin_job(
        account_ident: str,
        game: str,
        cookie_str: str,
        language: str,
        notification_manager: Optional[NotificationManager]
):
    def _checkin_job():
        logging.info(f"Running scheduler for '{account_ident}'...")
        game_perform_checkin(
            account_ident,
            game,
            cookie_str,
            language,
            notification_manager
        )

    return _checkin_job
