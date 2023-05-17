import logging
import os
import sys
import tomllib
from pathlib import Path
from typing import Optional

import comboparse

from hoyo_daily_logins_helper._version import __version__
from hoyo_daily_logins_helper.consts import DEFAULT_LANGUAGE
from hoyo_daily_logins_helper.games import GAMES, game_perform_checkin
from hoyo_daily_logins_helper.http import http_set_user_agent
from hoyo_daily_logins_helper.notifications import NotificationManager
from hoyo_daily_logins_helper.scheduler import run_scheduler
from hoyo_daily_logins_helper.utils import dict_prettify


def main():
    """ Main function for CLI """
    cli_args = list(sys.argv[1:])
    default_file = Path("hoyo-daily-logins-helper.toml")

    parser = comboparse.ComboParser(
        prog="hoyo-daily-logins-helper",
        description="Get hoyo daily login rewards automatically!",
        env_prefix="HOYO",
    )

    has_config_file = False
    has_single_game_flag = False
    has_legacy_cookie = False

    if (
            "--config-file" in cli_args or
            parser.create_env_var_name("CONFIG_FILE") in os.environ
    ):
        has_config_file = True

    if default_file.exists():
        has_config_file = True
        cli_args.append("--config-file")
        cli_args.append(default_file.absolute().__str__())

    for game in GAMES.keys():
        if f"--{game}" in cli_args:
            has_single_game_flag = True

    # legacy GAME env var
    if "GAME" in os.environ:
        has_single_game_flag = True
    if "COOKIE" in os.environ:
        has_legacy_cookie = True

    parser.add_argument(
        "-c", "--cookie",
        type=str,
        help="the cookie(s) for your accounts",
        action="append",
        required=not has_config_file and not has_legacy_cookie,
        default=[],
    )

    parser.add_argument(
        "-g", "--game",
        help="the game(s) for which this tool is supposed to run",
        action="append",
        choices=GAMES.keys(),
        required=not has_config_file and not has_single_game_flag,
        default=[],
    )

    for game in GAMES.keys():
        game_name = GAMES[game]["name"]
        parser.add_argument(
            f"--{game}",
            help=f"run for game {game_name}",
            action="store_const",
            dest="overwrite_game",
            const=game,
        )

    parser.add_argument(
        "--user-agent",
        help="run the requests against the API with a different user agent",
        action="store",
    )

    parser.add_argument(
        "--language",
        help="return results in a different language",
        default=DEFAULT_LANGUAGE,
    )

    parser.add_argument(
        "--config-file",
        help="use TOML config file for account configuration",
        action="store",
    )

    parser.add_argument(
        "--debug",
        help="run with debug flags",
        action="store_true",
    )

    parser.add_argument(
        "-v", "--version",
        action="version",
        version=__version__,
    )

    args = parser.parse_args(cli_args)

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="[%(asctime)s][%(levelname)s]: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S"
    )

    logging.info(f"Hoyo Daily Logins Helper - v{__version__}")
    logging.info("If this tool fails, try to update your cookie!")
    logging.debug(f"Arguments: {args}")

    if args.overwrite_game:
        args.game = [args.overwrite_game]

    if has_legacy_environment_variable():
        logging.debug("Legacy environment variable found")

        if "LANGUAGE" in os.environ:
            args.language = os.environ["LANGUAGE"]
        if "COOKIE" in os.environ:
            args.cookie = [os.environ["COOKIE"]]
        if "GAME" in os.environ:
            args.game = [os.environ["GAME"]]

    enable_scheduler = False
    account_identifiers = [None for _ in args.game]
    notification_manager: Optional[NotificationManager] = None

    if args.config_file:
        logging.info(f"Found config file at: {args.config_file}")

        with open(args.config_file, "rb") as file:
            config_data = tomllib.load(file)
            logging.debug(dict_prettify(config_data))

            # parse config from toml file
            language = config_data.get("config", {}).get("language", None)

            if language:
                args.language = language

            user_agent = config_data.get("config", {}).get("user-agent", None)

            if user_agent:
                args.user_agent = user_agent

            enable_scheduler = config_data.get("config", {}) \
                .get("enable_scheduler", False)

            notifications = config_data.get("config", {}).get("notifications",
                                                              [])

            notification_manager = NotificationManager(notifications)

            # parse accounts
            for index, account in enumerate(config_data.get("accounts", [])):
                game = account.get("game", None)
                cookie = account.get("cookie", None)

                if not game:
                    logging.error(f"account #{index} has no game selected")
                    continue

                if game not in GAMES:
                    logging.error(
                        f"account #{index} has invalid game '{game}' set"
                    )
                    continue

                if not cookie:
                    logging.error(f"account #{index} has no cookie set")
                    continue

                account_identifiers.append(account.get("identifier", None))
                args.game.append(game)
                args.cookie.append(cookie)

    if len(args.cookie) != len(args.game):
        logging.error(
            f"number of cookies ({len(args.cookie)}) and "
            f"games ({len(args.game)}) does not match"
        )
        exit(1)

    if args.user_agent:
        http_set_user_agent(args.user_agent)

    if enable_scheduler:
        run_scheduler(config_data, args.language, notification_manager)
        return

    for index, game in enumerate(args.game):
        identifier = f"Account #{index}"
        cookie = args.cookie[index]

        if account_identifiers[index]:
            identifier = account_identifiers[index]

        game_perform_checkin(
            identifier,
            game,
            cookie,
            args.language,
            notification_manager
        )


def has_legacy_environment_variable() -> bool:
    for env_var in ["LANGUAGE", "COOKIE", "GAME"]:
        if env_var in os.environ:
            return True
    return False
