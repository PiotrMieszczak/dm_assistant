"""campaign, conversation, message

Revision ID: 0001
Revises:
Create Date: 2026-10-10
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # pgvector, for chunk embeddings (ADR-0014). Enabled now so the extension is
    # proven present before any table depends on it.
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "campaign",
        sa.Column("id", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("system", sa.Text(), nullable=False),
        sa.Column("tint", sa.Text(), nullable=False),
        sa.Column("image_path", sa.Text(), nullable=True),
        sa.Column("last_played_at", sa.Date(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_campaign"),
    )

    op.create_table(
        "conversation",
        sa.Column("id", sa.Integer(), sa.Identity(), nullable=False),
        sa.Column("campaign_id", sa.Text(), nullable=False),
        sa.Column("mode", sa.Text(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["campaign_id"],
            ["campaign.id"],
            name="fk_conversation_campaign_id_campaign",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_conversation"),
    )
    op.create_index("ix_conversation_campaign_id", "conversation", ["campaign_id"])

    op.create_table(
        "message",
        sa.Column("id", sa.Integer(), sa.Identity(), nullable=False),
        sa.Column("conversation_id", sa.Integer(), nullable=False),
        sa.Column("role", sa.Text(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("mode", sa.Text(), nullable=False),
        sa.Column("tool_label", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["conversation_id"],
            ["conversation.id"],
            name="fk_message_conversation_id_conversation",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_message"),
    )
    op.create_index("ix_message_conversation_id", "message", ["conversation_id"])


def downgrade() -> None:
    op.drop_table("message")
    op.drop_table("conversation")
    op.drop_table("campaign")
    # The vector extension stays: it may predate this migration or serve other objects.
