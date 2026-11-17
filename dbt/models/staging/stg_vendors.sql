select
    vendor_id,
    name as vendor_name,
    category as vendor_category,
    city,
    created_at,
    updated_at
from {{ source('raw', 'vendors') }}
