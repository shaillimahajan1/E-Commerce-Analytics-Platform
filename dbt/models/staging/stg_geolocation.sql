with source as (
    select * from {{ source('ecommerce_raw', 'raw_geolocation') }}
),

city_counts as (
    select
        cast(geolocation_zip_code_prefix as varchar) as zip_code_prefix,
        trim(cast(geolocation_city as varchar)) as city,
        upper(trim(cast(geolocation_state as varchar))) as state,
        cast(geolocation_lat as double) as latitude,
        cast(geolocation_lng as double) as longitude,
        count(*) over (
            partition by cast(geolocation_zip_code_prefix as varchar), trim(cast(geolocation_city as varchar))
        ) as city_frequency
    from source
),

ranked_locations as (
    select
        zip_code_prefix,
        latitude,
        longitude,
        city,
        state,
        row_number() over (
            partition by zip_code_prefix
            order by city_frequency desc
        ) as rn
    from city_counts
),

aggregated as (
    select
        zip_code_prefix,
        round(avg(latitude), 6) as avg_latitude,
        round(avg(longitude), 6) as avg_longitude,
        max(case when rn = 1 then city end) as primary_city,
        max(case when rn = 1 then state end) as primary_state
    from ranked_locations
    group by zip_code_prefix
)

select * from aggregated
