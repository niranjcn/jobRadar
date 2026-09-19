-- Phase 1 of the job_matches index cleanup.
--
-- job_matches_user_id_idx on (user_id) is strictly redundant: every query it
-- can serve is served equally by the UNIQUE (user_id, job_id) constraint index
-- (same leftmost column, index-only capable). All reads are user-scoped, so
-- nothing loses a plan. Dropping it saves ~4 MB plus one index write on every
-- insert (5 index writes per row -> 4).
--
-- Kept deliberately: pkey (id) and (user_id, created_at) are phase 2/3, and
-- job_id_idx is load-bearing for the 035 CASCADE FK plus all job-side joins.

drop index if exists job_matches_user_id_idx;
