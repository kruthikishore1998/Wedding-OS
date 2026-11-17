-- Grain: one row per quote line item. Incremental: only reprocess changed rows.
{{ config(materialized='incremental', unique_key='line_item_id') }}

select
    li.line_item_id, li.quote_id,
    q.venue_id, q.vendor_id, q.event_name, q.quote_status,
    li.item_type, li.line_item_description,
    li.unit_price, li.quantity, li.line_amount,
    -- a status change on the quote should also refresh its line items
    greatest(li.updated_at, q.updated_at) as updated_at
from {{ ref('stg_quote_line_items') }} as li
join {{ ref('stg_quotes') }} as q using (quote_id)
{% if is_incremental() %}
where greatest(li.updated_at, q.updated_at) > (select max(updated_at) from {{ this }})
{% endif %}
