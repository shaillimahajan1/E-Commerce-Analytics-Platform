with geo as (
    select * from {{ ref('stg_geolocation') }}
),

final as (
    select
        zip_code_prefix,
        avg_latitude,
        avg_longitude,
        primary_city,
        primary_state,
        
        -- Official Brazilian IBGE Macro-Regions
        case primary_state
            when 'SP' then 'Southeast'
            when 'RJ' then 'Southeast'
            when 'MG' then 'Southeast'
            when 'ES' then 'Southeast'
            when 'PR' then 'South'
            when 'SC' then 'South'
            when 'RS' then 'South'
            when 'DF' then 'Central-West'
            when 'GO' then 'Central-West'
            when 'MT' then 'Central-West'
            when 'MS' then 'Central-West'
            when 'BA' then 'Northeast'
            when 'PE' then 'Northeast'
            when 'CE' then 'Northeast'
            when 'MA' then 'Northeast'
            when 'PB' then 'Northeast'
            when 'RN' then 'Northeast'
            when 'AL' then 'Northeast'
            when 'PI' then 'Northeast'
            when 'SE' then 'Northeast'
            when 'AM' then 'North'
            when 'PA' then 'North'
            when 'RO' then 'North'
            when 'TO' then 'North'
            when 'AC' then 'North'
            when 'AP' then 'North'
            when 'RR' then 'North'
            else 'Other / Undefined'
        end as macro_region
    from geo
)

select * from final
