from src.config import parse_cookie_string
from src.games.hoyo_checkin import hoyo_checkin


def run(cookie_str: str):
    cookies = parse_cookie_string(cookie_str)

    uid = cookies["account_id"]
    token = cookies["ltoken"]

    hoyo_checkin(
        "https://sg-public-api.hoyolab.com/event/luna/os",
        "e202303301540311",
        uid,
        token,
        cookie_str,
    )
