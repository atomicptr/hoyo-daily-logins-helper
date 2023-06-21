import json
import logging
from dataclasses import dataclass
from datetime import UTC, datetime

from hoyo_daily_logins_helper.http import http_post
from hoyo_daily_logins_helper.utils import dict_prettify


@dataclass
class Notification:
    success: bool
    game_name: str
    account_identifier: str
    message: str
    custom_fields: list[dict] = ()


@dataclass
class _NotificationHandler:
    on: list[str]

    @staticmethod
    def create(data: dict):
        raise NotImplementedError

    def send(self, notification: Notification):
        raise NotImplementedError

    def run_on_success(self) -> bool:
        return "success" in self.on

    def run_on_failure(self) -> bool:
        return "failure" in self.on


@dataclass
class _DiscordNotificationHandler(_NotificationHandler):
    webhook_url: str

    @staticmethod
    def create(data: dict):
        if "webhook_url" not in data:
            msg = "No webhook_url defined in Discord notifications"
            raise Exception(msg)
        if "on" not in data:
            data["on"] = ["success", "failure"]
        return _DiscordNotificationHandler(data["on"], data["webhook_url"])

    def send(self, notification: Notification):
        if notification.success and not self.run_on_success():
            return

        if not notification.success and not self.run_on_failure():
            return

        color_success = 4431943
        color_failure = 15022389

        fields = [
            {
                "name": "Game",
                "value": notification.game_name,
            },
            {
                "name": "Account",
                "value": notification.account_identifier,
            },
        ]

        for custom_field in notification.custom_fields:
            fields.append({
                "name": custom_field["key"],
                "value": custom_field["value"],
                "inline": False,
            })

        tz = datetime.now(UTC).astimezone().tzinfo

        data = json.dumps({
            "content": "",
            "embeds": [
                {
                    "author": {
                        "name": "atomicptr/hoyo-daily-logins-helper",
                        "url": "https://github.com/atomicptr/hoyo-daily-logins-helper",
                    },
                    "color": color_success if notification.success else color_failure,
                    "title": "Hoyo Daily Logins Helper",
                    "description": notification.message,
                    "fields": fields,
                    "thumbnail": {
                        "url": "https://i.imgur.com/LiWb3EG.png",
                    },
                    "timestamp": datetime.now(tz=tz).isoformat(),
                },
            ],
        }, ensure_ascii=False)

        http_post(self.webhook_url, data=data, headers={
            "Content-Type": "application/json",
        })


class NotificationManager:
    _handler: list[_NotificationHandler] = []

    def __init__(self, notifications: list[dict]) -> None:
        for notification in notifications:
            if "type" not in notification:
                logging.error(
                    "Notification entry without type found:"
                    f"\n{dict_prettify(notification)}",
                )
                continue
            match notification["type"]:
                case "discord":
                    self._handler.append(
                        _DiscordNotificationHandler.create(notification),
                    )
                case other_type:
                    logging.error(f"Unknown notification type {other_type}")
                    continue

    def send(self, notification: Notification):
        logging.debug(notification)
        for handler in self._handler:
            handler.send(notification)
