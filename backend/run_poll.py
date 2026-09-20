import asyncio
import sys

from app.config import load_settings
from app.db import close_async_pool
from app.migrate import run_migrations
from app.poller import poll_all_sources


async def main() -> None:
    settings = load_settings()
    run_migrations(settings.database_url)
    result = await poll_all_sources()
    # Advisory lock held → another poll (web scheduler) is running; exit 0 is success.
    if result.get("status") == "skipped":
        print(
            f"poll: skipped ({result.get('error') or 'advisory lock held'}) — web scheduler holds lock, exit 0"
        )
        return
    print(
        f"poll: {result.get('status')} fetched={result.get('jobs_fetched', 0)} new={result.get('jobs_new', 0)}"
    )
    # Ensure async pool is closed cleanly to avoid psycopg thread warnings.
    try:
        await close_async_pool()
    except Exception:
        pass


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
    # Exit 0 even when skipped — not an error; web's IntervalTrigger is the scheduler.
    sys.exit(0)
