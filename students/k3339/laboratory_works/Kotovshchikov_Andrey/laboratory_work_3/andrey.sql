SELECT room_id,
    label,
    SUM(
        EXTRACT(
            DAY
            FROM AGE(b.check_out_date, b.check_in_date)
        )
    ) * rt.price_per_day AS profit
FROM booking AS b
    JOIN room AS r ON b.room_id = r.id
    JOIN room_type AS rt ON r.room_type_id = rt.id
WHERE EXTRACT(
        YEAR
        FROM check_in_date
    ) = $current_year
    AND EXTRACT(
        YEAR
        FROM check_out_date
    ) = $current_year
    AND EXTRACT(
        MONTH
        FROM check_in_date
    ) >= $start_month
    AND EXTRACT(
        MONTH
        FROM check_out_date
    ) <= $end_month
GROUP BY room_id,
    label,
    rt.price_per_day;