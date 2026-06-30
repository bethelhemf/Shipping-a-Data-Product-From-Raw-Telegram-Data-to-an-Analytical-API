SELECT
    distinct to_char(message_date, 'YYYYMMDD')::int as date_key,
    message_date::date as date_day,
    extract(year from message_date) as year,
    extract(month from message_date) as month,
    to_char(message_date, 'Month') as month_name,
    extract(dow from message_date) in (0, 6) as is_weekend
FROM {{ ref('stg_telegram_messages') }}