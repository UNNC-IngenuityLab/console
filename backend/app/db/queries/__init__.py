"""SQL query files."""

# Common query fragments
SELECT_USER_FIELDS = """
    id, openid, student_id, nickname, avatar_url, total_points, level, is_active, created_at, updated_at
"""

SELECT_ACTIVITY_FIELDS = """
    id, activity_id, creator_openid, name, venue, date_range, start_date, end_date,
    total_point, sign_up_count, completed_count, is_active, created_at, updated_at
"""

SELECT_ANNOUNCEMENT_FIELDS = """
    id, creator_openid, title, content, is_active, priority, created_at, updated_at
"""

SELECT_LEVEL_CONFIG_FIELDS = """
    id, level, name, name_en, name_zh_tw, min_score, max_score, icon_url, icon_dark_url,
    bg_color, bg_gradient_start, bg_gradient_end, description, description_en,
    animation_type, sound_url, is_active, sort_order, created_at, updated_at
"""
