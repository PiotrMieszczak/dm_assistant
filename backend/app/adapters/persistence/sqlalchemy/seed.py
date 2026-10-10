"""Local development data: the campaign the frontend fixtures point at.

Campaign CRUD does not exist yet, and a conversation needs a campaign row to belong to.
Idempotent. Run with: python -m app.adapters.persistence.sqlalchemy.seed
"""

import os

from sqlalchemy.dialects.postgresql import insert

from app.adapters.persistence.sqlalchemy.engine import create_session_factory
from app.adapters.persistence.sqlalchemy.tables import CampaignRow

DEV_CAMPAIGNS = [
    {
        "id": "ashfall",
        "name": "The Ashfall Compact",
        "system_id": "dnd-2024",  # systems themselves come from migration 0002
        "tint": "#8a5a3c",
    },
]


def main() -> None:
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise SystemExit("Set DATABASE_URL to seed the database.")
    sessions = create_session_factory(url)
    with sessions.begin() as session:
        session.execute(
            insert(CampaignRow).values(DEV_CAMPAIGNS).on_conflict_do_nothing()
        )
    print(f"Seeded {len(DEV_CAMPAIGNS)} campaign(s).")


if __name__ == "__main__":
    main()
