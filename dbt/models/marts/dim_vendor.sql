select vendor_id, vendor_name, vendor_category, city, updated_at
from {{ ref('stg_vendors') }}
