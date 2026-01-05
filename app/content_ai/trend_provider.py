def get_trending_topics(category: str):
    trends_map = {
        "gaming": [
            "best mobile games 2025",
            "pro gaming tips",
            "fps sensitivity settings",
            "budget vs flagship gaming phones",
            "gaming mistakes beginners make"
        ],
        "tech": [
            "ai tools 2025",
            "best gadgets under budget",
            "smartphone comparisons",
            "hidden android features"
        ],
        "fitness": [
            "fat loss mistakes",
            "home workout",
            "diet myths",
            "muscle building basics"
        ],
        "education": [
            "study hacks",
            "career roadmap",
            "ai for students",
            "learning faster techniques"
        ]
    }

    return trends_map.get(category.lower(), [
        "latest trends",
        "viral topics",
        "beginner mistakes",
        "expert tips"
    ])
