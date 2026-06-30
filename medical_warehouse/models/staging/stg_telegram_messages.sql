SELECT
    message_id::int,
    channel_name,
    message_date::timestamp as message_date,
    LOWER(message_text) as message_text,
    views::int,
    forwards::int,
    has_media::boolean as has_image
FROM {{ source('raw', 'telegram_messages') }}
WHERE message_id IS NOT NULL