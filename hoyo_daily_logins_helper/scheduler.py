import logging
import sys
from datetime import UTC, datetime, time, timedelta
from time import sleep

import pytz
from scheduler import Scheduler

from hoyo_daily_logins_helper.games import GAMES, game_perform_checkin
from hoyo_daily_logins_helper.notifications import NotificationManager

_RESET_HOUR = 0
_RESET_MINUTE = 5
_RESET_TIMEZONE = "Asia/Shanghai"


def run_scheduler(
        config_data: dict,
        language: str,
        notifications_manager: NotificationManager | None,
):
    logging.info("Run in scheduler mode")

    tz = datetime.now(UTC).astimezone().tzinfo

    schedule = Scheduler(tzinfo=tz)

    accounts = config_data.get("accounts", [])
    times = []

    for index, account in enumerate(accounts):
        identifier = account.get("identifier", None)
        checkin_time = account.get("checkin_time", None)

        if not identifier:
            identifier = f"Account #{index}"

        game = account.get("game")
        game_name = GAMES[game]["name"]

        if checkin_time is None:
            checkin_time = {}

        if "hour" not in checkin_time:
            checkin_time["hour"] = _RESET_HOUR
        if "minute" not in checkin_time:
            checkin_time["minute"] = _RESET_MINUTE
        if "timezone" not in checkin_time:
            checkin_time["timezone"] = _RESET_TIMEZONE

        schedule.daily(
            time(
                tzinfo=pytz.timezone(checkin_time["timezone"]),
                hour=checkin_time["hour"],
                minute=checkin_time["minute"],
            ),
            create_checkin_job(
                identifier,
                game,
                account.get("cookie"),
                language,
                notifications_manager,
            ),
        )

        times.append((game_name, identifier, checkin_time))

        logging.info(
            f"Added {game_name} account '{identifier}' to scheduler",
        )

    if len(schedule.jobs) == 0:
        logging.error("No jobs scheduled")
        sys.exit(1)

    print_time_till_next_reset(times)
    schedule.hourly(
        time(minute=0, second=0, tzinfo=tz),
        lambda: print_time_till_next_reset(times),
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


def print_time_till_next_reset(times: list[tuple]):
    tz = datetime.now(UTC).astimezone().tzinfo
    now = datetime.now(tz=tz)

    lines = []

    for game_name, identifier, checkin_time in times:
        reset_time = time(
            tzinfo=pytz.timezone(checkin_time["timezone"]),
            hour=checkin_time["hour"],
            minute=checkin_time["minute"],
        )

        next_reset = datetime.now(tz=reset_time.tzinfo)
        next_reset = next_reset.replace(
            hour=reset_time.hour,
            minute=reset_time.minute,
            second=0,
        )

        if next_reset < now:
            next_reset = next_reset + timedelta(days=1)

        diff = next_reset - now

        hours = round(diff.total_seconds() / 60 / 60, 1)

        lines.append(
            f"\t{game_name} - {identifier} in {hours} hours",
        )

    lines_str = "\n".join(lines)
    logging.info(f"Next reset times are:\n{lines_str}")
