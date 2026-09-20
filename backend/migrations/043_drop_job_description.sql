-- Drop jobs.description: keyword matching is title-only by product decision,
-- descriptions average 21 bytes (mostly empty) with monster outliers, and no
-- reader needs the column (detail endpoints return null, frontend falls back).
-- Every reader is updated alongside this drop (recompute function here,
-- TEXT_SQL, detail selects, matcher/normalize path); missing any of them
-- would be a hard SQL error, not silent drift.

-- v_job_source selects the column (nothing in-app reads the view, but
-- PostgREST exposes it, so keep its shape with a null placeholder).
drop view if exists v_job_source;

alter table jobs drop column if exists description;

create or replace view v_job_source as
select
    j.id,
    j.source_id,
    s.company_name,
    s.ats_type,
    j.external_job_id,
    j.title,
    j.location,
    j.url,
    null::text as description,
    j.first_seen_at
from jobs j
join sources s on s.id = j.source_id;

-- Recompute keywords against title only (043: description arm removed).
-- Body is otherwise identical to 041_job_lifecycle.sql.
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
        where position(lower(k) in lower(coalesce(j.title, ''))) > 0
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
