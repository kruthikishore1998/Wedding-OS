select
    venue_id,
    name as venue_name,
    city,
    intended_event,
    capacity,
    overage_fee_per_guest,
    allows_outside_caterer,
    allows_baraat,
    allows_open_flame,
    noise_curfew,
    alcohol_policy,
    created_at,
    updated_at
from {{ source('raw', 'venues') }}
