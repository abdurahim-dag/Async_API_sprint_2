with persons as (
    select
        p.id,
        p.created,
        p.modified,
        p.full_name,
        pfw.role,
        json_agg (
                pfw.film_work_id::text
            ) as "film_ids"
    from content.person p
             inner join content.person_film_work pfw on pfw.person_id = p.id
    group by
        p.id,
        p.created,
        p.modified,
        p.full_name,
        pfw.role
    order by p.id
)

select
    json_build_object('id', p.id,
                      'full_name', p.full_name,
                      'role', p.role,
                      'film_ids', coalesce(p.film_ids,'[]')
        ) as "xyz"
from persons p
