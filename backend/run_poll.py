import asyncio

from app.config import load_settings
from app.migrate import run_migrations
from app.poller import poll_all_sources


async def main() -> None:
    settings = load_settings()
    run_migrations(settings.database_url)
    await poll_all_sources()


if __name__ == "__main__":
    asyncio.run(main())
