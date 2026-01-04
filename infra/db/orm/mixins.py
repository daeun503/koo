from sqlalchemy import Column, DateTime

from app.utils import get_utc_now


class TimestampMixin:
    created_at = Column(DateTime, nullable=False, default=get_utc_now)
    updated_at = Column(DateTime, nullable=False, default=get_utc_now, onupdate=get_utc_now)


class SoftDeleteMixin:
    deleted_at = Column(DateTime, nullable=True, default=None)

    def soft_delete(self):
        if self.deleted_at is None:
            self.deleted_at = get_utc_now()

    def restore(self):
        self.deleted_at = None

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None
