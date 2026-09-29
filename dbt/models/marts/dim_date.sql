with raw_dates as (
    {% if target.type == 'bigquery' %}
    select date_day
    from unnest(generate_date_array('2016-01-01', '2019-12-31', interval 1 day)) as date_day
    {% else %}
    select cast(range as date) as date_day
    from range(date '2016-01-01', date '2020-01-01', interval 1 day)
    {% endif %}
),

final as (
    select
        cast(strftime(date_day, '%Y%m%d') as integer) as date_key,
        date_day,
        extract(year from date_day) as year,
        extract(quarter from date_day) as quarter,
        extract(month from date_day) as month,
        case extract(month from date_day)
            when 1 then 'January'
            when 2 then 'February'
            when 3 then 'March'
            when 4 then 'April'
            when 5 then 'May'
            when 6 then 'June'
            when 7 then 'July'
            when 8 then 'August'
            when 9 then 'September'
            when 10 then 'October'
            when 11 then 'November'
            when 12 then 'December'
        end as month_name,
        strftime(date_day, '%Y-%m') as year_month,
        extract(day from date_day) as day_of_month,
        extract(dayofweek from date_day) as day_of_week,
        case extract(dayofweek from date_day)
            when 0 then 'Sunday'
            when 1 then 'Monday'
            when 2 then 'Tuesday'
            when 3 then 'Wednesday'
            when 4 then 'Thursday'
            when 5 then 'Friday'
            when 6 then 'Saturday'
            when 7 then 'Sunday'
        end as day_name,
        case when extract(dayofweek from date_day) in (0, 6, 7) then 1 else 0 end as is_weekend
    from raw_dates
)

select * from final
