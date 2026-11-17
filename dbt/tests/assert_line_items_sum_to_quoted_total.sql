-- Fails if any quote's line items don't add up to its quoted total (1 cent tolerance).
select quote_id, all_in_total, quoted_total, all_in_vs_quoted_diff
from {{ ref('fct_quote_all_in') }}
where abs(all_in_vs_quoted_diff) > 0.01
