"""Mock data generators for testing."""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any
import random
import string


def generate_object_id() -> str:
    """Generate a MongoDB-like ObjectId."""
    import time
    timestamp = int(time.time())
    random_str = ''.join(random.choices('0123456789abcdef', k=16))
    return f"{timestamp:08x}{random_str}"


def generate_mock_user(override: dict[str, Any] | None = None) -> dict[str, Any]:
    """Generate mock user data."""
    user_id = generate_object_id()
    timestamp = int(datetime.now().timestamp() * 1000)

    data = {
        "id": user_id,
        "openid": f"openid_{timestamp}",
        "student_id": f"{random.randint(20240001, 20249999)}",
        "password": "hashed_password_here",
        "security_question": "What is your favorite color?",
        "security_answer": "blue",
        "nickname": f"User {random.randint(1, 1000)}",
        "avatar_url": f"https://api.dicebear.com/7.x/avataaars/svg?seed={user_id}",
        "total_points": Decimal(str(random.randint(0, 100))),
        "level": random.randint(1, 10),
        "is_active": True,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }

    if override:
        data.update(override)

    return data


def generate_mock_activity(override: dict[str, Any] | None = None) -> dict[str, Any]:
    """Generate mock activity data."""
    activity_id = generate_object_id()
    timestamp_id = int(datetime.now().timestamp() * 1000)

    start_date = datetime.now() + timedelta(days=random.randint(1, 30))

    data = {
        "id": activity_id,
        "activity_id": timestamp_id,
        "creator_openid": "admin_openid",
        "name": random.choice([
            "Welcome Orientation",
            "Mid-Autumn Festival",
            "Hackathon 2024",
            "Sports Day",
            "Career Workshop",
            "Charity Bazaar",
            "Winter Concert",
            "New Year Gala",
        ]),
        "venue": random.choice([
            "Main Auditorium",
            "Student Plaza",
            "Innovation Hub",
            "Sports Field",
            "Conference Room A",
            "Student Center",
        ]),
        "date_range": start_date.strftime("%Y.%m.%d 9:00~17:00"),
        "start_date": start_date.date().isoformat(),
        "end_date": (start_date + timedelta(days=1)).date().isoformat(),
        "total_point": Decimal(str(random.choice([15, 20, 25, 30]))),
        "sign_up_count": random.randint(10, 200),
        "completed_count": random.randint(5, 150),
        "is_active": True,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }

    if override:
        data.update(override)

    return data


def generate_mock_sub_activity(activity_id: str, index: int = 0) -> dict[str, Any]:
    """Generate mock sub-activity data."""
    timestamp_id = int(datetime.now().timestamp() * 1000) + index

    return {
        "id": timestamp_id,
        "activity_id": activity_id,
        "name": random.choice([
            "Check-in",
            "Registration",
            "Main Event",
            "Group Activity",
            "Survey",
            "Photo Session",
        ]),
        "point": Decimal(str(random.choice([5, 10, 15]))),
        "is_stopped": False,
        "sort_order": index,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }


def generate_mock_announcement(override: dict[str, Any] | None = None) -> dict[str, Any]:
    """Generate mock announcement data."""
    announcement_id = generate_object_id()

    data = {
        "id": announcement_id,
        "creator_openid": "admin_openid",
        "title": random.choice([
            "Welcome to Leo the Billionaire!",
            "New Activity Registration Open",
            "Leaderboard Update",
            "Special Event Announcement",
        ]),
        "content": "This is a sample announcement content for testing purposes.",
        "is_active": True,
        "priority": random.randint(0, 10),
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }

    if override:
        data.update(override)

    return data


def generate_mock_level_config(level: int, override: dict[str, Any] | None = None) -> dict[str, Any]:
    """Generate mock level config data."""
    level_names = [
        ("车库小店", "Garage Store"),
        ("家庭商店", "Family Store"),
        ("邻里市场", "Neighborhood Market"),
        ("社区商店", "Community Shop"),
        ("区域超市", "District Supermarket"),
        ("城市商城", "City Mall"),
        ("区域中心", "Regional Center"),
        ("国家总部", "National Headquarters"),
        ("国际总部", "International HQ"),
        ("世界级总部", "World-Class HQ"),
    ]

    if 1 <= level <= len(level_names):
        name_zh, name_en = level_names[level - 1]
    else:
        name_zh = f"Level {level}"
        name_en = f"Level {level}"

    colors = ["#9E9E9E", "#4CAF50", "#8BC34A", "#CDDC39", "#FFEB3B",
              "#FFC107", "#FF9800", "#FF5722", "#F44336", "#E91E63"]

    data = {
        "id": level,
        "level": level,
        "name": name_zh,
        "name_en": name_en,
        "name_zh_tw": None,
        "min_score": Decimal(str((level - 1) * 10)),
        "max_score": Decimal(str(level * 10 - 1)) if level < 10 else None,
        "icon_url": f"/assets/levels/level-{level}.png",
        "icon_dark_url": None,
        "bg_color": colors[level - 1] if level <= len(colors) else "#9C27B0",
        "bg_gradient_start": None,
        "bg_gradient_end": None,
        "description": f"Reach level {level} by earning points!",
        "description_en": f"Reach level {level} by earning points!",
        "animation_type": random.choice(["none", "scale", "glow", "particles", "confetti"]),
        "sound_url": None,
        "is_active": True,
        "sort_order": level,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }

    if override:
        data.update(override)

    return data


def generate_mock_ui_config(category: str = "general") -> dict[str, Any]:
    """Generate mock UI config data."""
    configs = {
        "general": {
            "key": "app.primary_color",
            "value": '"#2196F3"',
            "type": "color",
            "category": "general",
            "label": "主题色",
            "description": "应用主题色",
        },
        "home": {
            "key": "home.welcome_text",
            "value": '"欢迎回来，{nickname}!"',
            "type": "string",
            "category": "home",
            "label": "欢迎语",
            "description": "主页顶部欢迎文案",
        },
        "timeline": {
            "key": "timeline.node_size",
            "value": "60",
            "type": "number",
            "category": "timeline",
            "label": "节点大小",
            "description": "蜿蜒小路节点大小（像素）",
        },
    }

    return configs.get(category, configs["general"])


def generate_mock_dashboard_stats() -> dict[str, Any]:
    """Generate mock dashboard statistics."""
    return {
        "total_users": random.randint(100, 1000),
        "total_activities": random.randint(20, 100),
        "active_activities": random.randint(5, 20),
        "total_signups": random.randint(500, 5000),
        "total_completions": random.randint(300, 4000),
        "avg_completion_rate": round(random.uniform(60, 95), 2),
        "total_points_awarded": Decimal(str(random.randint(10000, 100000))),
    }


def generate_mock_leaderboard_entry(rank: int) -> dict[str, Any]:
    """Generate mock leaderboard entry."""
    return {
        "rank": rank,
        "user_id": generate_object_id(),
        "student_id": f"{random.randint(20240001, 20249999)}",
        "nickname": f"Player {rank}",
        "avatar_url": f"https://api.dicebear.com/7.x/avataaars/svg?seed={rank}",
        "total_points": Decimal(str(100 - rank * 5 + random.randint(0, 10))),
        "level": random.randint(1, 10),
    }


def generate_mock_admin_log(action: str = "create_activity") -> dict[str, Any]:
    """Generate mock admin log entry."""
    return {
        "id": random.randint(1, 10000),
        "admin_openid": "admin_openid",
        "action": action,
        "target_id": generate_object_id(),
        "description": f"Performed {action} operation",
        "old_value": None,
        "new_value": {"test": "data"},
        "ip_address": "127.0.0.1",
        "created_at": datetime.now().isoformat(),
    }


# Bulk data generators
def generate_mock_users(count: int = 10) -> list[dict[str, Any]]:
    """Generate multiple mock users."""
    return [generate_mock_user() for _ in range(count)]


def generate_mock_activities(count: int = 5) -> list[dict[str, Any]]:
    """Generate multiple mock activities."""
    return [generate_mock_activity() for _ in range(count)]


def generate_mock_announcements(count: int = 3) -> list[dict[str, Any]]:
    """Generate multiple mock announcements."""
    return [generate_mock_announcement() for _ in range(count)]


def generate_mock_level_configs() -> list[dict[str, Any]]:
    """Generate all mock level configs."""
    return [generate_mock_level_config(i) for i in range(1, 11)]


def generate_mock_leaderboard(count: int = 50) -> list[dict[str, Any]]:
    """Generate mock leaderboard."""
    return [generate_mock_leaderboard_entry(i) for i in range(1, count + 1)]
