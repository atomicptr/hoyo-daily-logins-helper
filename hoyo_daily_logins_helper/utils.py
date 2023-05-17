import json


def dict_prettify(d: dict) -> str:
    return json.dumps(d, sort_keys=True, indent=4)
