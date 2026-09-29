{% macro generate_surrogate_key(field_list) %}
{# 
    Generates a deterministic MD5 hash surrogate key across fields,
    handling NULL values by coalescing to an empty sentinel token.
#}
md5(
    concat(
        {% for field in field_list %}
            coalesce(cast({{ field }} as varchar), '_null_sentinel_')
            {% if not loop.last %}, '-' , {% endif %}
        {% endfor %}
    )
)
{% endmacro %}
