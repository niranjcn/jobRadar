-- Whole-word matching: 'ai' must hit 'AI Engineer' but not 'retailer'.
-- Python (app/matcher.py term_matches_text) and this SQL function are the two
-- match implementations and must agree; both treat a term as a hit only when
-- surrounded by non-alphanumeric text or string edges. Postgres ARE regex has
-- no lookbehind, hence the (^|[^a-z0-9])...([^a-z0-9]|$) shape.

create or replace function term_matches(p_haystack text, p_term text)
returns boolean
language sql immutable as
$$
    select p_term is not null and p_term <> ''
        and lower(coalesce(p_haystack, '')) ~ (
            '(^|[^a-z0-9])'
            || regexp_replace(lower(p_term), '([.\^$*+?()\[\]{}|\\])', '\\\1', 'g')
            || '([^a-z0-9]|$)'
        );
$$;

create or replace function recompute_job_matches(
    p_user_id uuid,
    p_roles text[],
    p_keywords text[],
    p_locations jsonb,
    p_seniority text[],
    p_excluded text[]
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
        where term_matches(j.title, r)
    ) rh
    cross join lateral (
        select coalesce(array_agg(k), '{}'::text[]) as keywords_hit
        from unnest(coalesce(p_keywords, '{}'::text[])) k
        where term_matches(coalesce(j.title, '') || ' ' || coalesce(j.description, ''), k)
    ) kh
    cross join lateral (
        select coalesce(array_agg(s2), '{}'::text[]) as seniority_hit
        from unnest(coalesce(p_seniority, '{}'::text[])) s2
        where term_matches(j.title, s2) or lower(s2) = 'any'
    ) sh
    cross join lateral (
        select coalesce(array_agg(x ->> 'raw'), '{}'::text[]) as loc_text
        from jsonb_array_elements(coalesce(p_locations, '[]'::jsonb)) x
        where term_matches(coalesce(j.location, ''), x ->> 'raw')
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
    -- 060: matches-today retention — only jobs first seen in the last 24h.
    and j.first_seen_at >= now() - interval '24 hours';

    get diagnostics inserted = row_count;
    select count(*) into considered from jobs
    where first_seen_at >= now() - interval '24 hours';

    return jsonb_build_object('result', 'ok', 'considered', considered, 'matched', inserted);
end;
$$;
