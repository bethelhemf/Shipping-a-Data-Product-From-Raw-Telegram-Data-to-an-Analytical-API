SELECT
    m.message_id,
    md5(m.channel_name) as channel_key,
    to_char(m.message_date, 'YYYYMMDD')::int as date_key,
    m.views,
    m.forwards,
    m.has_image,
    length(m.message_text) as message_length
FROM {{ ref('stg_telegram_messages') }} m