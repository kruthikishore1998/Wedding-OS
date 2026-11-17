{% macro pct_of(numerator, denominator, decimals=1) -%}
    round(100.0 * ({{ numerator }}) / nullif({{ denominator }}, 0), {{ decimals }})
{%- endmacro %}
