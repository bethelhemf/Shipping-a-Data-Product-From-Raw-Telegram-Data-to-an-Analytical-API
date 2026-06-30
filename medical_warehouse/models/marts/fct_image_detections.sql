SELECT
    m.message_id,
    m.channel_key,
    m.date_key,
    y.image_category,
    y.detected_objects,
    m.views,
    m.forwards
FROM {{ ref('fct_messages') }} m
JOIN {{ source('raw', 'yolo_detections') }} y ON m.message_id = y.message_id