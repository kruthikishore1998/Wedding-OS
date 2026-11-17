-- Grain: one row per quote version (from the SCD2 snapshot).
select
    quote_id,
    row_number() over (partition by quote_id order by dbt_valid_from) as version_number,
    status as quote_status,
    quoted_total,
    quoted_total - lag(quoted_total) over (
        partition by quote_id order by dbt_valid_from
    ) as change_from_previous,
    dbt_valid_from as valid_from,
    dbt_valid_to   as valid_to,
    dbt_valid_to is null as is_current
from {{ ref('snap_quotes') }}
