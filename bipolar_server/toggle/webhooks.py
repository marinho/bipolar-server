import requests
import json

try:
    import pusher
except ImportError:
    pusher = None


class BaseWebhook(object):
    pass


class PusherWebhook(BaseWebhook):
    _test = {
        "mode": False,
        "pool": None,
        }

    def __init__(self):
        if pusher is None:
            raise ImportError("pusher package was not found.")

    def send(self, data, webhook):
        p = pusher.Pusher(
            app_id=str(webhook.param1),
            key=str(webhook.param2),
            secret=str(webhook.param3),
            )

        # For mocking during tests
        if PusherWebhook._test["mode"]:
            data["client"] = p
            if PusherWebhook._test["pool"] is None:
                PusherWebhook._test["pool"] = None
            PusherWebhook._test["pool"].append(data)
            return

        p[str(webhook.param4)].trigger(str(webhook.param5), data)


class UrlWebhook(BaseWebhook):
    def send(self, data, webhook):
        return requests.post(
                webhook.param1,
                data=json.dumps(data),
                headers={"content-type": "text/javascript"},
                )


def send_to_webhook(data, webhook):
    if webhook.type == webhook.TYPE_PUSHER:
        return PusherWebhook().send(data, webhook)
    elif webhook.type == webhook.TYPE_URL:
        return UrlWebhook().send(data, webhook)

