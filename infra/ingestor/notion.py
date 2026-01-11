from typing import Any, Iterable

from app.enums import SourceType
from app.models.base import Document
from app.repositories.ingestor import Ingestor
from app.repositories.llm import Answerer
from config import settings
from infra.notion.client import NotionClient


class NotionIngestor(Ingestor):
    source_type = SourceType.NOTION

    def __init__(self, llm: Answerer | None = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.llm = llm

        if not settings.NOTION_API_TOKEN:
            raise ValueError("NOTION_API_TOKEN is not set in settings.")

        self.client = NotionClient(token=settings.NOTION_API_TOKEN)

    def build_document(self) -> Document:
        page = self.client.get_page(self.source_id)
        title = self._extract_page_title(page) or self.title or "(Untitled)"

        blocks = self._get_blocks_recursive(self.source_id)
        content = self.blocks_to_text(blocks).strip()

        return Document(
            domain=self.domain,
            source_type=self.source_type,
            source_id=self.source_id,
            title=title,
            raw_content=content,
        )

    # -------------------------
    # Notion helpers
    # -------------------------
    def _extract_page_title(self, page: dict[str, Any]) -> str | None:
        props = (page or {}).get("properties") or {}
        for _, prop in props.items():
            if not isinstance(prop, dict):
                continue
            if prop.get("type") == "title":
                title_items = prop.get("title") or []
                return self._rich_text_to_plain(title_items).strip() or None

        # fallback (rare)
        if isinstance(page, dict) and isinstance(page.get("title"), list):
            t = self._rich_text_to_plain(page["title"]).strip()
            return t or None

        return None

    def _get_blocks_recursive(self, block_id: str) -> list[dict[str, Any]]:
        """Fetch blocks and their children recursively."""
        blocks = self.client.get_page_blocks(block_id)

        out: list[dict[str, Any]] = []
        for b in blocks:
            out.append(b)
            if b.get("has_children") and b.get("id"):
                out.extend(self._get_block_children_recursive(b["id"]))
        return out

    def _get_block_children_recursive(self, block_id: str) -> list[dict[str, Any]]:
        # NotionClient wraps the SDK; for recursion we access the underlying client.
        sdk = getattr(self.client, "_client", None)
        if sdk is None:
            return []

        collected: list[dict[str, Any]] = []
        cursor: str | None = None
        while True:
            resp = sdk.blocks.children.list(block_id=block_id, start_cursor=cursor)
            children = resp.get("results") or []

            for c in children:
                collected.append(c)
                if c.get("has_children") and c.get("id"):
                    collected.extend(self._get_block_children_recursive(c["id"]))

            if not resp.get("has_more"):
                break
            cursor = resp.get("next_cursor")

        return collected

    # -------------------------
    # Block → text
    # -------------------------
    def blocks_to_text(self, blocks: Iterable[dict[str, Any]]) -> str:
        lines: list[str] = []
        for block in blocks:
            line = self.block_to_line(block)
            if line:
                lines.append(line)
        return "\n".join(lines)

    def block_to_line(self, block: dict[str, Any]) -> str | None:
        btype = (block or {}).get("type")
        if not btype:
            return None

        data = (block or {}).get(btype) or {}

        # 이미지 블록 처리
        if btype == "image":
            if self.llm:
                image_url = self._extract_image_url(data)
                if image_url:
                    try:
                        summary = self.llm.summarize_image(image_url)
                        if summary:
                            return f"### 이미지 내용\n{summary}"
                    except Exception:
                        return None
            return None

        # ✅ 기타 미디어/링크 블록은 제거 (텍스트만 추출)
        if btype in {
            "video",
            "file",
            "pdf",
            "audio",
            "bookmark",
            "embed",
            "link_preview",
        }:
            return None

        if btype == "link_to_page":
            return None  # 링크도 제외 (원하면 제목만 추가하도록 확장 가능)

        # --- 이하 기존 텍스트 처리 로직 유지 ---
        if btype in {
            "paragraph",
            "heading_1",
            "heading_2",
            "heading_3",
            "quote",
            "callout",
            "toggle",
        }:
            text = self._rich_text_to_plain(data.get("rich_text") or []).strip()
            if not text:
                return None

            if btype.startswith("heading_"):
                level = btype.split("_")[1]
                prefix = {"1": "# ", "2": "## ", "3": "### "}.get(level, "")
                return f"{prefix}{text}"

            if btype == "quote":
                return f"> {text}"

            if btype == "callout":
                icon = data.get("icon")
                icon_txt = ""
                if isinstance(icon, dict) and icon.get("type") == "emoji":
                    icon_txt = f"{icon.get('emoji')} "
                return f"{icon_txt}{text}"

            if btype == "toggle":
                return f"- {text}"

            return text

        if btype in {"bulleted_list_item", "numbered_list_item"}:
            text = self._rich_text_to_plain(data.get("rich_text") or []).strip()
            if not text:
                return None
            prefix = "- " if btype == "bulleted_list_item" else "1. "
            return f"{prefix}{text}"

        if btype == "to_do":
            text = self._rich_text_to_plain(data.get("rich_text") or []).strip()
            if not text:
                return None
            checked = data.get("checked")
            mark = "[x]" if checked else "[ ]"
            return f"- {mark} {text}"

        if btype == "code":
            code = self._rich_text_to_plain(data.get("rich_text") or []).rstrip()
            if not code:
                return None
            lang = data.get("language") or ""
            return f"```{lang}\n{code}\n```".strip()

        if btype == "divider":
            return "---"

        # Unknown block types: best-effort
        rt = data.get("rich_text")
        if isinstance(rt, list):
            text = self._rich_text_to_plain(rt).strip()
            return text or None
        return None

    def _extract_image_url(self, image_data: dict[str, Any]) -> str | None:
        file = image_data.get("file") or {}
        external = image_data.get("external") or {}

        url = file.get("url") or external.get("url")
        return url

    def _rich_text_to_plain(self, rich_text: list[dict[str, Any]]) -> str:
        parts: list[str] = []
        for t in rich_text or []:
            if not isinstance(t, dict):
                continue

            pt = t.get("plain_text")
            if isinstance(pt, str):
                parts.append(pt)
                continue

            txt = (t.get("text") or {}).get("content")
            if isinstance(txt, str):
                parts.append(txt)

        return "".join(parts)
