import logging
import sys
from datetime import UTC, datetime, time, timedelta
from time import sleep

import pytz
from scheduler import Scheduler

from hoyo_daily_logins_helper.games import GAMES, game_perform_checkin
from hoyo_daily_logins_helper.notifications import NotificationManager

_RESET_TIME = time(tzinfo=pytz.timezone("Asia/Shanghai"), hour=0, minute=5)


def run_scheduler(
        config_data: dict,
        language: str,
        notifications_manager: NotificationManager | None,
):
    logging.info("Run in scheduler mode")

    tz = datetime.now(UTC).astimezone().tzinfo

    schedule = Scheduler(tzinfo=tz)

    accounts = config_data.get("accounts", [])

    for index, account in enumerate(accounts):
        identifier = account.get("identifier", None)

        if not identifier:
            identifier = f"Account #{index}"

        game = account.get("game")
        game_name = GAMES[game]["name"]

        schedule.daily(
            _RESET_TIME,
            create_checkin_job(
                identifier,
                game,
                account.get("cookie"),
                language,
                notifications_manager,
            ),
        )

        logging.info(
            f"Added {game_name} account '{identifier}' to scheduler",
        )

    if len(schedule.jobs) == 0:
        logging.error("No jobs scheduled")
        sys.exit(1)

    print_time_till_next_reset()
    schedule.hourly(
        time(minute=0, second=0, tzinfo=tz),
        print_time_till_next_reset,
    )

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
        notification_manager: NotificationManager | None,
):
    def _checkin_job():
        logging.info(f"Running scheduler for '{account_ident}'...")
        game_perform_checkin(
            account_ident,
            game,
            cookie_str,
            language,
            notification_manager,
        )

    return _checkin_job


def print_time_till_next_reset():
    tz = datetime.now(UTC).astimezone().tzinfo
    now = datetime.now(tz=tz)
    next_reset = datetime.now(tz=_RESET_TIME.tzinfo)
    next_reset = next_reset.replace(
        hour=_RESET_TIME.hour,
        minute=_RESET_TIME.minute,
        second=0,
    )

    if next_reset < now:
        next_reset = next_reset + timedelta(days=1)

    diff = next_reset - now

    hours = round(diff.total_seconds() / 60 / 60, 1)

    logging.info(f"Next reset time is in {hours} hours.")
