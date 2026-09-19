-- Phase 3 of the job_matches index cleanup.
--
-- job_matches_user_created_idx on (user_id, created_at DESC) is not worth its
-- ~4 MB + one index write per insert. Proven by plan comparison on live data:
--   * big user (99% of rows): plans byte-identical with/without it (parallel
--     seq scan either way — no index helps when one user owns the table).
--   * small user: plans keep the same shape without it (Index Only Scan and
--     Bitmap Heap Scan move to the (user_id, job_id) PK; created_at becomes a
--     heap filter over a few thousand rows — microseconds).
-- The new-matches since-queries (routes.py matches_jobs, bot _list_matches)
-- keep index-backed plans via the PK. No query loses an access path.

drop index if exists job_matches_user_created_idx;
