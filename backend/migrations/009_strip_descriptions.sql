-- Strip HTML tags from existing job descriptions to reclaim space
-- (new writes are already stripped by app.models.strip_html). Only touches
-- rows that actually contain '<', leaving plain-text descriptions untouched.
update jobs
set description = nullif(
        trim(
            regexp_replace(
                regexp_replace(description, '<[^>]+>', ' ', 'g'),
                '\s+', ' ', 'g'
            )
        ),
        ''
    )
where description is not null and position('<' in description) > 0;
