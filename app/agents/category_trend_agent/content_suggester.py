def suggest_content(category, trends):
    suggestions = []

    for t, _ in trends[:5]:
        suggestions.append({
            "idea": f"{t.title()} explained in 60 seconds",
            "format": "YouTube Short",
            "hook": f"Why everyone is talking about {t}"
        })

    return {
        "category": category,
        "suggestions": suggestions
    }
