select
    quote_id,
    venue_id,
    vendor_id,
    event_name,
    guest_count,
    status as quote_status,
    quoted_total,
    created_at,
    updated_at
from {{ source('raw', 'quotes') }}
