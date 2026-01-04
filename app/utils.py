import gzip
import hashlib
import re
from datetime import datetime

import pytz
from pydantic import BaseModel as PydanticBaseModel

KST = pytz.timezone("Asia/Seoul")


class BaseModel(PydanticBaseModel):
    pass


class ORMBaseModel(BaseModel):
    class Config:
        from_orm = True


def convert_utc_to_kst(utc_datetime):
    return utc_datetime.astimezone(KST)


def get_utc_now() -> datetime:
    return datetime.now(pytz.UTC)


def get_with_tz(dt: datetime, tz=pytz.UTC):
    """현재 시간(DB에 들어있는 값 기준, pytz.UTC) 에 타임존 설정하여 반환"""
    return tz.normalize(dt.astimezone(pytz.UTC))


def normalize_content(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.strip()
    text = re.sub(r"[ \t]+", " ", text)
    return text


def compute_content_hash(raw_content: str) -> str:
    normalized = normalize_content(raw_content)
    h = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    return h


def gzip_compress_text(text: str, *, level: int = 6) -> bytes:
    return gzip.compress(text.encode("utf-8"), compresslevel=level)


def gzip_decompress_text(blob: bytes) -> str:
    return gzip.decompress(blob).decode("utf-8")
