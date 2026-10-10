"""system table; campaign references one system

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-10
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# The systems the campaign picker offers on day one (data-model.md, DEC-013).
SYSTEMS = [
    {"id": "dnd-2024", "name": "D&D 2024"},
    {"id": "traveller-2e", "name": "Traveller 2e"},
]


def upgrade() -> None:
    system = op.create_table(
        "system",
        sa.Column("id", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_system"),
        sa.UniqueConstraint("name", name="uq_system_name"),
    )
    op.bulk_insert(system, SYSTEMS)

    # Any other free-text system already stored becomes a row of its own, so no
    # campaign loses its system.
    op.execute(
        """
        INSERT INTO system (id, name)
        SELECT DISTINCT
            trim(both '-' from
                lower(regexp_replace(c.system, '[^A-Za-z0-9]+', '-', 'g'))),
            c.system
        FROM campaign c
        WHERE NOT EXISTS (SELECT 1 FROM system s WHERE s.name = c.system)
        """
    )

    op.add_column("campaign", sa.Column("system_id", sa.Text(), nullable=True))
    op.execute(
        "UPDATE campaign c SET system_id = s.id FROM system s WHERE s.name = c.system"
    )
    op.alter_column("campaign", "system_id", nullable=False)
    op.create_foreign_key(
        "fk_campaign_system_id_system",
        "campaign",
        "system",
        ["system_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_index("ix_campaign_system_id", "campaign", ["system_id"])
    op.drop_column("campaign", "system")


def downgrade() -> None:
    op.add_column("campaign", sa.Column("system", sa.Text(), nullable=True))
    op.execute(
        "UPDATE campaign c SET system = s.name FROM system s WHERE s.id = c.system_id"
    )
    op.alter_column("campaign", "system", nullable=False)
    op.drop_index("ix_campaign_system_id", table_name="campaign")
    op.drop_constraint("fk_campaign_system_id_system", "campaign", type_="foreignkey")
    op.drop_column("campaign", "system_id")
    op.drop_table("system")
