from src.config import parse_cookie_string


def run(cookie_str: str):
    cookies = parse_cookie_string(cookie_str)
    print(cookies)
    raise Exception("Not yet implemented")
