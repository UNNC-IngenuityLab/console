"""SQL query files."""

# Common query fragments
SELECT_USER_FIELDS = """
    id, openid, student_id, password, IFNULL(nickname, student_id) AS nickname, avatar_url, total_points, level, is_active, created_at, updated_at
"""

SELECT_ACTIVITY_FIELDS = """
    id, activity_id, creator_openid, name, venue, start_date, end_date,
    total_point, is_active, created_at, updated_at,
    (SELECT COUNT(*) FROM registered_activities ra WHERE ra.activity_id = activities.id) AS sign_up_count,
    (SELECT COUNT(*) FROM registered_activities ra WHERE ra.activity_id = activities.id AND ra.is_completed = 1) AS completed_count,
    (SELECT COUNT(*) FROM sub_activities sa WHERE sa.activity_id = activities.id) AS sub_activity_count
"""

SELECT_ANNOUNCEMENT_FIELDS = """
    id, creator_openid, title, content, is_active, priority, created_at, updated_at
"""

SELECT_LEVEL_CONFIG_FIELDS = """
    id, level, name, name_en, name_zh_tw, min_score, max_score, icon_url, icon_dark_url,
    bg_color, bg_gradient_start, bg_gradient_end, description, description_en,
    animation_type, sound_url, is_active, sort_order, created_at, updated_at
"""
