-- Grain: one row per quote, with all-in price and comparison helpers.
select
    quote_id, venue_id, vendor_id,
    case when venue_id is not null then 'venue' else 'vendor' end as quote_for,
    event_name, guest_count, quote_status,
    quote_status in ('received', 'negotiating', 'accepted') as is_active,
    line_item_count, base_amount, per_guest_amount, cleaning_amount,
    overtime_amount, service_fee_amount, tax_amount, gratuity_amount,
    service_fee_amount + tax_amount + gratuity_amount as fees_total,
    {{ pct_of('service_fee_amount + tax_amount + gratuity_amount', 'all_in_total') }} as fees_pct_of_all_in,
    all_in_total,
    round(all_in_total / nullif(guest_count, 0), 2) as all_in_per_guest,
    quoted_total,
    all_in_total - quoted_total as all_in_vs_quoted_diff,
    created_at, updated_at
from {{ ref('int_quote_all_in') }}
