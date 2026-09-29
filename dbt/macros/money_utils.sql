{% macro round_currency(field, precision=2) %}
    round(cast({{ field }} as double), {{ precision }})
{% endmacro %}
