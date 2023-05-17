import json
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import List

from src.http import http_post


@dataclass
class Notification:
    success: bool
    game_name: str
    account_identifier: str
    message: str
    custom_fields: List[dict] = ()


@dataclass
class _NotificationHandler:
    pass

    @staticmethod
    def create(data: dict):
        raise NotImplementedError()

    def send(self, notification: Notification):
        raise NotImplementedError()


@dataclass
class _DiscordNotificationHandler(_NotificationHandler):
    webhook_url: str

    @staticmethod
    def create(data: dict):
        if "webhook_url" not in data:
            raise Exception("No webhook_url defined in Discord notifications")
        return _DiscordNotificationHandler(data["webhook_url"])

    def send(self, notification: Notification):
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
                    "timestamp": datetime.now().isoformat(),
                }
            ]
        }, ensure_ascii=False)

        http_post(self.webhook_url, data=data, headers={
            "Content-Type": "application/json",
        })


class NotificationManager:
    _handler: List[_NotificationHandler] = []

    def __init__(self, notifications: List[dict]):
        for notification in notifications:
            if "type" not in notification:
                logging.error(
                    "Notification entry without type found",
                    notification
                )
                continue
            match notification["type"]:
                case "discord":
                    self._handler.append(
                        _DiscordNotificationHandler.create(notification)
                    )
                case other_type:
                    logging.error(f"Unknown notification type {other_type}")
                    continue

    def send(self, notification: Notification):
        logging.debug(notification)
        for handler in self._handler:
            handler.send(notification)
