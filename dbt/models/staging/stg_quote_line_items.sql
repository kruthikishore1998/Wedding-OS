select
    line_item_id,
    quote_id,
    item_type,
    description as line_item_description,
    unit_price,
    quantity,
    amount as line_amount,
    updated_at
from {{ source('raw', 'quote_line_items') }}
