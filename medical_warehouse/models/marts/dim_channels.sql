SELECT
    md5(channel_name) as channel_key,
    channel_name,
    count(*) as total_messages,
    avg(views) as avg_views
FROM {{ ref('stg_telegram_messages') }}
GROUP BY 1, 2