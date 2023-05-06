import argparse
import os
import sys
import logging

from src.games import genshin, starrail
from src._version import __version__


def main():
    """ Main function for CLI """
    parser = argparse.ArgumentParser(
        prog="hoyo-daily-logins-helper",
        description="Get hoyo daily login rewards automatically!",
    )

    parser.add_argument(
        "-c", "--cookie",
        type=str,
        help="your login cookie",
        action="store",
    )

    parser.add_argument(
        "--genshin",
        help="run the tool for Genshin Impact",
        action="store_true",
    )

    parser.add_argument(
        "--starrail",
        help="run the tool for Honkai Star Rail",
        action="store_true",
    )

    parser.add_argument(
        "--debug",
        help="run with debug flags",
        action="store_true"
    )

    args = parser.parse_args(sys.argv[1:])

    if os.getenv("DEBUG_MODE"):
        args.debug = True

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="[%(asctime)s][%(levelname)s]: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S"
    )

    logging.info(f"Hoyo Daily Logins Helper - v{__version__}")
    logging.info("If this tool fails, try to update your cookie!")

    game_args = [
        args.genshin,
        args.starrail,
    ]

    # if the flag was not set, check if the environment variable is
    if not args.cookie:
        args.cookie = os.getenv("COOKIE")

    if not args.cookie:
        logging.error(
            "Cookies are not set, please set the COOKIE environment variable or "
            "--cookie flag")
        sys.exit(1)

    one_game_set = False

    for game_set in game_args:
        if game_set and one_game_set:
            logging.error("You set more than one game, please use either 'genshin' or 'starrail'")
            sys.exit(1)
        if game_set:
            one_game_set = True

    if not one_game_set:
        if (
                "GAME" not in os.environ and
                os.environ["GAME"] not in ["genshin", "starrail"]
        ):
            logging.error("No game was set!")
            sys.exit(1)

        if os.environ["GAME"] == "genshin":
            args.genshin = True
        elif os.environ["GAME"] == "starrail":
            args.starrail = True

    if args.genshin:
        genshin.run(args.cookie)
    elif args.starrail:
        starrail.run(args.cookie)
