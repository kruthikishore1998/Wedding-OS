-- One row per quote: line items pivoted by type, summed to an all-in price.
with rolled_up as (
    select
        quote_id,
        count(*) as line_item_count,
        sum(line_amount) filter (where item_type = 'base')        as base_amount,
        sum(line_amount) filter (where item_type = 'per_guest')   as per_guest_amount,
        sum(line_amount) filter (where item_type = 'cleaning')    as cleaning_amount,
        sum(line_amount) filter (where item_type = 'overtime')    as overtime_amount,
        sum(line_amount) filter (where item_type = 'service_fee') as service_fee_amount,
        sum(line_amount) filter (where item_type = 'tax')         as tax_amount,
        sum(line_amount) filter (where item_type = 'gratuity')    as gratuity_amount,
        sum(line_amount) as all_in_total
    from {{ ref('stg_quote_line_items') }}
    group by quote_id
)

select
    q.quote_id, q.venue_id, q.vendor_id, q.event_name,
    q.guest_count, q.quote_status, q.quoted_total,
    r.line_item_count,
    coalesce(r.base_amount, 0)        as base_amount,
    coalesce(r.per_guest_amount, 0)   as per_guest_amount,
    coalesce(r.cleaning_amount, 0)    as cleaning_amount,
    coalesce(r.overtime_amount, 0)    as overtime_amount,
    coalesce(r.service_fee_amount, 0) as service_fee_amount,
    coalesce(r.tax_amount, 0)         as tax_amount,
    coalesce(r.gratuity_amount, 0)    as gratuity_amount,
    coalesce(r.all_in_total, 0)       as all_in_total,
    q.created_at, q.updated_at
from {{ ref('stg_quotes') }} as q
left join rolled_up as r using (quote_id)
