import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone

from src.games import game_perform_checkin

_RESET_TIME = {
    # running this one hour after reset to prevent potential fuckery with
    # timezones
    "hour": 5,
    "minute": 1,
}

_RESET_TIMES = {
    "Asia": CronTrigger(timezone=timezone("Etc/GMT+8"), **_RESET_TIME),
    "EU": CronTrigger(timezone=timezone("Etc/GMT+1"), **_RESET_TIME),
    "NA": CronTrigger(timezone=timezone("Etc/GMT-5"), **_RESET_TIME)
}


def run_scheduler(config_data: dict, language: str):
    logging.info("Run in scheduler mode")

    # only show warnings and above from apscheduler
    logging.getLogger("apscheduler").setLevel(logging.WARNING)

    scheduler = BlockingScheduler()

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

        scheduler.add_job(
            create_checkin_job(
                identifier,
                account.get("game"),
                account.get("cookie"),
                language,
            ),
            _RESET_TIMES[region]
        )

        logging.info(
            f"Added account '{identifier}' to scheduler, region: '{region}'"
        )

    if len(scheduler.get_jobs()) == 0:
        logging.error("No jobs scheduled")
        exit(1)

    scheduler.start()


def create_checkin_job(
    account_ident: str,
    game: str,
    cookie_str: str,
    language: str
):
    def _checkin_job():
        logging.info(f"Running scheduler for '{account_ident}'...")
        game_perform_checkin(account_ident, game, cookie_str, language)

    return _checkin_job
