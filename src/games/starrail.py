from src.games.hoyo_checkin import hoyo_checkin


def run(cookie_str: str):
    hoyo_checkin(
        "https://sg-public-api.hoyolab.com/event/luna/os",
        "e202303301540311",
        cookie_str,
    )
