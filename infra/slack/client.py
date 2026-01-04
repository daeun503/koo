from slack_sdk import WebClient


class SlackClient:
    def __init__(self, token: str):
        self._client = WebClient(token=token)

    def fetch_channel_messages(
        self,
        channel_id: str,
        limit: int = 200,
    ) -> list[dict]:
        messages: list[dict] = []
        cursor: str | None = None

        while True:
            resp = self._client.conversations_history(
                channel=channel_id,
                limit=limit,
                cursor=cursor,
            )
            messages.extend(resp["messages"])

            cursor = resp.get("response_metadata", {}).get("next_cursor")
            if not cursor:
                break

        return messages
