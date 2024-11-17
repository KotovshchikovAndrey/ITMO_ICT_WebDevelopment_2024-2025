SELECT_PROFIT_PER_ROOM_FOR_QUARTER = """
    SELECT 
        room_id,
        label,
        SUM(
            EXTRACT(
                DAY
                FROM AGE(
                    LEAST(
                        b.check_out_date,
                        %(quarter_end)s::date + INTERVAL '1 DAY'
                    ), 
                    b.check_in_date
                )
            ) * rt.price_per_day
        ) AS profit
    FROM booking AS b
        JOIN room AS r ON b.room_id = r.id
        JOIN room_type AS rt ON r.room_type_id = rt.id
    WHERE check_in_date BETWEEN %(quarter_start)s AND %(quarter_end)s
    GROUP BY 
        room_id,
        label,
        rt.price_per_day;
"""
