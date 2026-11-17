-- Grain: one row per quote line item.
select
    li.line_item_id, li.quote_id,
    q.venue_id, q.vendor_id, q.event_name, q.quote_status,
    li.item_type, li.line_item_description,
    li.unit_price, li.quantity, li.line_amount, li.updated_at
from {{ ref('stg_quote_line_items') }} as li
join {{ ref('stg_quotes') }} as q using (quote_id)
