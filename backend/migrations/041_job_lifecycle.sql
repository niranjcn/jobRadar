-- Job lifecycle state: identity (source_id, external_job_id) already exists;
-- this completes the model with snapshot freshness + lifecycle on the same row.
-- job_snapshots table deferred until a history-needing feature exists.
--
-- Rollout assumes live: defaults stamp now()/true at ALTER time (metadata-only,
-- instant), so no dashboard goes dark on deploy day; genuine misses drain out
-- over the grace window. Never backfill last_seen_at from first_seen_at —
-- that would mass-deactivate the catalog on deploy.
--
-- Conventions the pipeline relies on:
--   last_seen_at     advanced by sightings (daily granularity, not per poll)
--   is_active        false only after 72h unseen across successful polls
--   last_updated_at  advances on content or lifecycle change (observability)

alter table jobs add column if not exists last_seen_at timestamptz not null default now();
alter table jobs add column if not exists is_active boolean not null default true;
alter table jobs add column if not exists last_updated_at timestamptz not null default now();

create index if not exists jobs_source_seen_idx on jobs (source_id, last_seen_at);

-- Recompute matches only against open postings (041: + is_active filter).
-- Body is otherwise identical to 012_excluded_roles.sql.
create or replace function recompute_job_matches(
    p_user_id uuid,
    p_roles text[],
    p_keywords text[],
    p_locations jsonb,
    p_seniority text[],
    p_excluded text[],
    p_excluded_roles text[]
) returns jsonb
language plpgsql
as $$
declare
    inserted bigint;
    considered bigint;
begin
    delete from job_matches where user_id = p_user_id;

    insert into job_matches (user_id, job_id, matched_on, match_score)
    select
        p_user_id,
        j.id,
        array_remove(
            array[
                case when cardinality(rh.roles_hit) > 0
                     then 'role:' || array_to_string(rh.roles_hit, ',') end,
                case when cardinality(kh.keywords_hit) > 0
                     then 'keyword:' || array_to_string(kh.keywords_hit, ',') end,
                case when cardinality(lf.loc_hit) > 0
                     then 'location:' || array_to_string(lf.loc_hit, ',') end,
                case when cardinality(sh.seniority_hit) > 0
                     then 'seniority:' || array_to_string(sh.seniority_hit, ',') end
            ],
            null
        ) as matched_on,
        case
            when (coalesce(cardinality(p_roles), 0) > 0)::int
               + (coalesce(cardinality(p_keywords), 0) > 0)::int
               + (coalesce(jsonb_array_length(p_locations), 0) > 0)::int
               + (coalesce(cardinality(p_seniority), 0) > 0)::int = 0
            then 100
            else round(
                ((cardinality(rh.roles_hit) > 0)::int
               + (cardinality(kh.keywords_hit) > 0)::int
               + (cardinality(lf.loc_hit) > 0)::int
               + (cardinality(sh.seniority_hit) > 0)::int) * 100.0
               / coalesce(
                    ((coalesce(cardinality(p_roles), 0) > 0)::int
                   + (coalesce(cardinality(p_keywords), 0) > 0)::int
                   + (coalesce(jsonb_array_length(p_locations), 0) > 0)::int
                   + (coalesce(cardinality(p_seniority), 0) > 0)::int),
                    1)
            )::int
        end as match_score
    from jobs j
    join sources s on s.id = j.source_id
    cross join lateral (
        select coalesce(array_agg(r), '{}'::text[]) as roles_hit
        from unnest(coalesce(p_roles, '{}'::text[])) r
        where position(lower(r) in lower(j.title)) > 0
    ) rh
    cross join lateral (
        select coalesce(array_agg(k), '{}'::text[]) as keywords_hit
        from unnest(coalesce(p_keywords, '{}'::text[])) k
        where position(lower(k) in lower(coalesce(j.title, '') || ' ' || coalesce(j.description, ''))) > 0
    ) kh
    cross join lateral (
        select coalesce(array_agg(s2), '{}'::text[]) as seniority_hit
        from unnest(coalesce(p_seniority, '{}'::text[])) s2
        where position(lower(s2) in lower(j.title)) > 0 or lower(s2) = 'any'
    ) sh
    cross join lateral (
        select coalesce(array_agg(x ->> 'raw'), '{}'::text[]) as loc_text
        from jsonb_array_elements(coalesce(p_locations, '[]'::jsonb)) x
        where position(lower(x ->> 'raw') in lower(coalesce(j.location, ''))) > 0
    ) lt
    cross join lateral (
        select coalesce(array_agg(x2 ->> 'raw'), '{}'::text[]) as loc_country
        from jsonb_array_elements(coalesce(p_locations, '[]'::jsonb)) x2
        where ((x2 ->> 'remote')::boolean and j.is_remote)
           or (cardinality(j.countries) > 0
               and j.countries && array(
                   select jsonb_array_elements_text(x2 -> 'codes')
               ))
    ) lc
    cross join lateral (
        select case
            when cardinality(lt.loc_text) > 0 then lt.loc_text
            when cardinality(j.countries) > 0 then lc.loc_country
            else '{}'::text[]
        end as loc_hit
    ) lf
    where not exists (
        select 1 from unnest(coalesce(p_excluded, '{}'::text[])) ex
        where lower(ex) = lower(s.company_name)
    )
    and not exists (
        -- excluded roles: any term present in the title disqualifies the job
        select 1 from unnest(coalesce(p_excluded_roles, '{}'::text[])) er
        where position(lower(er) in lower(j.title)) > 0
    )
    and (
        -- location is a hard filter when set
        coalesce(jsonb_array_length(p_locations), 0) = 0
        or cardinality(lf.loc_hit) > 0
    )
    and (
        -- roles / keywords / seniority are OR'd together
        (
            coalesce(cardinality(p_roles), 0) = 0
            and coalesce(cardinality(p_keywords), 0) = 0
            and coalesce(cardinality(p_seniority), 0) = 0
        )
        or cardinality(rh.roles_hit) > 0
        or cardinality(kh.keywords_hit) > 0
        or cardinality(sh.seniority_hit) > 0
    )
    -- lifecycle (041): only open postings can match
    and j.is_active;

    get diagnostics inserted = row_count;
    select count(*) into considered from jobs where is_active;

    return jsonb_build_object('result', 'ok', 'considered', considered, 'matched', inserted);
end;
$$;
