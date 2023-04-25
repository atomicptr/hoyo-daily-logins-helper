import argparse
import os
import sys

from src.config import log
from src.games import genshin, starrail


def main():
    """ Main function for CLI """
    log.info("Hoyo Daily Logins Helper")
    log.info("If this tool fails, try to update your cookie!")

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

    args = parser.parse_args(sys.argv[1:])

    game_args = [
        args.genshin,
        args.starrail,
    ]

    if not args.cookie:
        if "COOKIE" not in os.environ:
            log.error("Cookies are not set!")
            sys.exit(1)
        args.cookie = os.environ["COOKIE"]

    one_game_set = False

    for game_set in game_args:
        if game_set and one_game_set:
            log.error("More than one game was set!")
            sys.exit(1)
        if game_set:
            one_game_set = True

    if not one_game_set:
        if (
                "GAME" not in os.environ and
                os.environ["GAME"] not in ["genshin", "starrail"]
        ):
            log.error("No game was set!")
            sys.exit(1)

        if os.environ["GAME"] == "genshin":
            args.genshin = True
        elif os.environ["GAME"] == "starrail":
            args.starrail = True

    if args.genshin:
        genshin.run(args.cookie)
    elif args.starrail:
        starrail.run(args.cookie)
