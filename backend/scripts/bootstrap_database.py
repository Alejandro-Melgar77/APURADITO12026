"""Create the canonical SQLAlchemy schema in a configured Postgres database.

Supabase must have the PostGIS extension enabled first (see migrations/init.sql).
Run this once from backend/: python scripts/bootstrap_database.py
"""

import asyncio

from app.core.database import engine, init_db


async def main() -> None:
    await init_db()
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
