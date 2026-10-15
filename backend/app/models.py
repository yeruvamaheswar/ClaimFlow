"""Relational records; document text is synthetic and never executed."""

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import TypeDecorator

from .database import Base


def utcnow() -> datetime:
    return datetime.now(UTC)


class UTCDateTime(TypeDecorator):
    """Stores UTC; SQLite drops tzinfo on read, so naive values are re-marked as UTC."""

    impl = DateTime(timezone=True)
    cache_ok = True

    def process_result_value(self, value, dialect):
        if value is not None and value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value


class Claim(Base):
    __tablename__ = "claims"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    claim_ref: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    claimant_label: Mapped[str] = mapped_column(String(100))
    policy_ref: Mapped[str] = mapped_column(String(40))
    incident_date: Mapped[str] = mapped_column(String(10))
    status: Mapped[str] = mapped_column(String(30), default="intake")
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow)

    documents: Mapped[list["Document"]] = relationship(
        back_populates="claim", cascade="all, delete-orphan", order_by="Document.created_at"
    )
    audit_events: Mapped[list["AuditEvent"]] = relationship(
        back_populates="claim", cascade="all, delete-orphan", order_by="AuditEvent.created_at"
    )


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    claim_id: Mapped[str] = mapped_column(ForeignKey("claims.id"), index=True)
    filename: Mapped[str] = mapped_column(String(150))
    document_type: Mapped[str] = mapped_column(String(40))
    text: Mapped[str] = mapped_column(Text)
    extracted_facts: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow)

    claim: Mapped[Claim] = relationship(back_populates="documents")


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    claim_id: Mapped[str] = mapped_column(ForeignKey("claims.id"), index=True)
    action: Mapped[str] = mapped_column(String(60))
    detail: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow)

    claim: Mapped[Claim] = relationship(back_populates="audit_events")
