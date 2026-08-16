import asyncio

from app.adapters.oracle import OracleAdapter


async def main() -> None:
    adapter = OracleAdapter()
    for board in [
        "https://careers.americanexpress.com/en/sites/CX_1",
        "https://jpmc.fa.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1002/jobs",
    ]:
        try:
            jobs = await adapter.fetch_jobs(board)
            print(f"{board[:50]}... -> fetched={len(jobs)}")
            if jobs:
                j = jobs[0]
                print("  sample:", j.title[:60], "|", j.location, "|", j.url[:100])
        except Exception as e:
            print(f"{board[:50]}... -> ERROR {type(e).__name__}: {str(e)[:150]}")


asyncio.run(main())