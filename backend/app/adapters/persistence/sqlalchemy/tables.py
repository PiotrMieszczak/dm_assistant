"""PostgreSQL schema. Mapped to the domain by mappers.py, not equal to it."""

from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Identity, MetaData, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# Stable constraint names, so migrations can refer to them.
NAMING = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING)


class CampaignRow(Base):
    """owner_id arrives with auth (ADR-0008, DEC-005). No owner scope until then."""

    __tablename__ = "campaign"

    id: Mapped[str] = mapped_column(Text, primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    system: Mapped[str] = mapped_column(Text)
    tint: Mapped[str] = mapped_column(Text)
    image_path: Mapped[str | None] = mapped_column(Text)
    last_played_at: Mapped[date | None] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class ConversationRow(Base):
    __tablename__ = "conversation"

    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    campaign_id: Mapped[str] = mapped_column(
        ForeignKey("campaign.id", ondelete="CASCADE"), index=True
    )
    mode: Mapped[str] = mapped_column(Text)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    messages: Mapped[list["MessageRow"]] = relationship(
        order_by="MessageRow.id", cascade="all, delete-orphan"
    )


class MessageRow(Base):
    __tablename__ = "message"

    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("conversation.id", ondelete="CASCADE"), index=True
    )
    role: Mapped[str] = mapped_column(Text)
    content: Mapped[str] = mapped_column(Text)
    mode: Mapped[str] = mapped_column(Text)
    tool_label: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
