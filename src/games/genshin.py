from src.config import parse_cookie_string
from src.games.hoyo_checkin import hoyo_checkin


def run(cookie_str: str):
    cookies = parse_cookie_string(cookie_str)

    uid = cookies["account_id"]
    token = cookies["ltoken"]

    hoyo_checkin(
        "https://hk4e-api-os.mihoyo.com/event/sol",
        "e202102251931481",
        uid,
        token,
        cookie_str,
    )
