with genres as (
    select
        id,
        created,
        modified,
        name,
        description
    from {from_schema}.genre
)
select
    json_build_object('id', g.id,
                      'name', coalesce(g.name, ''),
                      'description', coalesce(g.description, '')
    ) as "xyz"
from genres g
where
    (g.modified > '{date_from}' or g.created > '{date_from}')
  and
    (g.modified <= '{date_to}' or g.created <= '{date_to}')
order by g.id
offset {offset};
