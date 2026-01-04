from sqlalchemy import (
    JSON,
    Column,
    Enum,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.enums import Domain, SourceType
from infra.db.base import Base
from infra.db.orm.mixins import SoftDeleteMixin, TimestampMixin


class Chunk(TimestampMixin, Base):
    __tablename__ = "chunk"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="청크 ID")
    document_id = Column(
        Integer,
        ForeignKey("document.id"),
        nullable=False,
        comment="FK: Document.id, 관련 문서 ID",
    )
    context_id = Column(Integer, nullable=False, comment="청크가 속한 컨텍스트 ID")

    chunk_index = Column(Integer, nullable=False, comment="문서 내 청크 인덱스")
    chunk_text = Column(Text, nullable=False, comment="청크 텍스트 내용")
    chunk_hash = Column(String(64), nullable=False, comment="청크 내용 해시")

    # relation
    document = relationship("Document", back_populates="chunks")


class Document(SoftDeleteMixin, TimestampMixin, Base):
    __tablename__ = "document"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="문서 ID")
    domain = Column(Enum(Domain), nullable=False, comment="문서 도메인")
    source_type = Column(Enum(SourceType), nullable=False, comment="문서 출처 유형")
    source_id = Column(String(255), nullable=False, comment="출처에서 제공하는 문서 ID")
    title = Column(String(512), nullable=True, comment="문서 제목")
    raw_content = Column(Text, nullable=True, comment="문서 내용")
    raw_content_gz = Column(LargeBinary, nullable=False, comment="압축된 문서 내용")
    content_hash = Column(String(64), nullable=False, comment="문서 내용 해시")
    version = Column(Integer, nullable=False, default=1, comment="문서 버전")

    # relation
    chunks = relationship("Chunk", back_populates="document")

    __table_args__ = (
        UniqueConstraint(
            "source_type",
            "source_id",
            name="u_idx_source_type_source_id",
        ),
    )


class QueryLog(TimestampMixin, Base):
    __tablename__ = "query_log"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="쿼리 로그 ID")

    query_text = Column(Text, nullable=False, comment="사용자 쿼리 텍스트")
    topk = Column(Integer, nullable=False, comment="검색된 청크 개수")
    selected_chunk_ids = Column(JSON, nullable=True, comment="선택된 청크 ID들 (JSON 직렬화된 형태)")
    expended_chunk_ids = Column(JSON, nullable=True, comment="확장된 청크 ID들 (JSON 직렬화된 형태)")
    answer = Column(Text, nullable=True, comment="생성된 답변 텍스트")
    input_tokens = Column(Integer, nullable=True, comment="입력 토큰 수")
    output_tokens = Column(Integer, nullable=True, comment="출력 토큰 수")
    total_tokens = Column(Integer, nullable=True, comment="총 토큰 수")
    meta = Column(JSON, nullable=True, comment="메타데이터")
