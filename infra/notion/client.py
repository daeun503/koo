from notion_client import Client as NotionSDKClient


class NotionClient:
    def __init__(self, token: str):
        self._client = NotionSDKClient(auth=token)

    def get_page(self, page_id: str) -> dict:
        return self._client.pages.retrieve(page_id=page_id)

    def get_page_blocks(self, page_id: str) -> list[dict]:
        blocks: list[dict] = []
        cursor: str | None = None

        while True:
            resp = self._client.blocks.children.list(
                block_id=page_id,
                start_cursor=cursor,
            )
            blocks.extend(resp["results"])

            if not resp.get("has_more"):
                break
            cursor = resp.get("next_cursor")

        return blocks
