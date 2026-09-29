{% macro datediff(start_date, end_date, unit='day') %}
{#
    Portable date difference macro supporting both BigQuery and local DuckDB targets.
#}
{%- if target.type == 'bigquery' -%}
    date_diff(cast({{ end_date }} as date), cast({{ start_date }} as date), {{ unit | upper }})
{%- else -%}
    datediff('{{ unit | lower }}', cast({{ start_date }} as timestamp), cast({{ end_date }} as timestamp))
{%- endif -%}
{% endmacro %}
