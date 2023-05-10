import logging
import sys

import comboparse

from src._version import __version__
from src.games import GAMES, game_perform_checkin
from src.http import http_set_user_agent

_DEFAULT_LANGUAGE = "en-us"


def main():
    """ Main function for CLI """
    parser = comboparse.ComboParser(
        prog="hoyo-daily-logins-helper",
        description="Get hoyo daily login rewards automatically!",
        env_prefix="HOYO",
    )

    parser.add_argument(
        "-c", "--cookie",
        type=str,
        help="the cookie(s) for your accounts",
        action="append",
        required=True,
    )

    parser.add_argument(
        "-g", "--game",
        help="the game(s) for which this tool is supposed to run",
        action="append",
        choices=GAMES.keys(),
        required=True,
    )

    parser.add_argument(
        "--user-agent",
        help="run the requests against the API with a different user agent",
        action="store",
    )

    parser.add_argument(
        "--language",
        help="return results in a different language",
        default=_DEFAULT_LANGUAGE,
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

    args = parser.parse_args(sys.argv[1:])

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="[%(asctime)s][%(levelname)s]: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S"
    )

    logging.info(f"Hoyo Daily Logins Helper - v{__version__}")
    logging.info("If this tool fails, try to update your cookie!")
    logging.debug(f"Arguments: {args}")

    if len(args.cookie) != len(args.game):
        logging.error(
            f"number of cookies ({len(args.cookie)}) and "
            f"games ({len(args.game)}) does not match"
        )
        exit(1)

    if args.user_agent:
        http_set_user_agent(args.user_agent)

    for index, game in enumerate(args.game):
        cookie = args.cookie[index]
        game_perform_checkin(f"Account #{index}", game, cookie, args.language)
