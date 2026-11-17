-- Fails if a quote has zero or more than one current version in the snapshot.
select quote_id, count(*) filter (where is_current) as current_versions
from {{ ref('fct_quote_versions') }}
group by quote_id
having count(*) filter (where is_current) <> 1
